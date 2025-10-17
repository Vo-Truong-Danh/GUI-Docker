"""
Spark Backend Logic - Separated from UI
Contains all Docker and Spark execution logic
Enhanced with caching, database tracking, auto-start Docker Desktop, and resource management (v6.1)
"""
import subprocess
import shutil
import os
import sys
import re
import threading
import time
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
from typing import Optional, Callable, Tuple, List

# Central logger for this module
try:
    from logging_config import get_logger
    _logger = get_logger('spark_backend', log_to_file=True, log_to_console=False)
except Exception:
    _logger = None

# Import subprocess utilities for hidden console windows
try:
    from subprocess_utils import get_subprocess_params, run_hidden, popen_hidden
    SUBPROCESS_UTILS_AVAILABLE = True
except ImportError:
    print("⚠️ Warning: subprocess_utils not available, console windows may appear")
    SUBPROCESS_UTILS_AVAILABLE = False
    def get_subprocess_params():
        return {}
    def run_hidden(*args, **kwargs):
        return subprocess.run(*args, **kwargs)
    def popen_hidden(*args, **kwargs):
        return subprocess.Popen(*args, **kwargs)

# Centralized error handler (optional)
try:
    from error_handler import get_error_handler, ErrorSeverity
    _err_handler = get_error_handler(_logger)
except Exception:
    _err_handler = None

# Import Docker utilities for auto-start feature
try:
    from docker_utils import ensure_docker_running, is_docker_running
    DOCKER_AUTO_START = True
except ImportError:
    print("⚠️ Warning: Docker auto-start feature not available")
    DOCKER_AUTO_START = False
    def ensure_docker_running(log_callback=None, auto_start=True, wait=True):
        return True, "Docker check skipped"
    def is_docker_running():
        return True

# Import caching and database modules
try:
    from system_utils import cache_manager, timed, RetryHandler
    from database import db
    ENHANCED_FEATURES = True
    # Create convenient decorator
    retry_with_backoff = RetryHandler.retry
except ImportError as e:
    print(f"⚠️ Warning: Enhanced features (cache/database) not available: {e}")
    ENHANCED_FEATURES = False
    # Create dummy decorators compatible with callers' signatures
    def timed(name):
        def decorator(func):
            return func
        return decorator
    def retry_with_backoff(*_args, **_kwargs):
        # Accept arbitrary kwargs like max_attempts, initial_delay for compatibility
        def decorator(func):
            return func
        return decorator

# Import resource manager
try:
    from resource_manager import managed_resource, get_resource_tracker
    RESOURCE_MANAGER_AVAILABLE = True
except ImportError:
    print("⚠️ Warning: Resource manager not available")
    RESOURCE_MANAGER_AVAILABLE = False
    def managed_resource(resource, cleanup):
        from contextlib import contextmanager
        @contextmanager
        def dummy():
            yield resource
        return dummy()

# Import NEW advanced features
try:
    from connection_pool import get_docker_rate_limiter
    from metrics_system import get_metrics_collector
    from advanced_cache import get_cache
    ADVANCED_FEATURES = True
    rate_limiter = get_docker_rate_limiter()
    metrics_collector = get_metrics_collector()
    advanced_cache = get_cache()
    print("✅ Advanced features enabled (connection pool, metrics, multi-level cache)")
except ImportError as e:
    print(f"⚠️ Warning: Advanced features not available: {e}")
    ADVANCED_FEATURES = False
    rate_limiter = None
    metrics_collector = None
    advanced_cache = None


# Process tracking for cleanup with enhanced safety
_active_processes: List[subprocess.Popen] = []
_process_lock = threading.RLock()
_cleanup_in_progress = False

# Configurable retry policy (can be updated at runtime)
RETRY_POLICY = {
    'copy_max_attempts': 3,
    'submit_max_attempts': 2,
    'compose_max_attempts': 3,
    'compose_status_max_attempts': 2,
    'initial_delay': 0.5,
    'backoff': 2.0,
}

def set_retry_policy(**kwargs):
    for k, v in kwargs.items():
        if k in RETRY_POLICY and isinstance(v, (int, float)):
            RETRY_POLICY[k] = v
    if _logger:
        try:
            _logger.info(f"Retry policy updated: {RETRY_POLICY}")
        except Exception:
            pass

def _execute_with_retry(fn: Callable[[], Tuple[int, str, str]],
                        max_attempts: int,
                        initial_delay: float,
                        backoff: float) -> Tuple[int, str, str]:
    attempt = 1
    delay = initial_delay
    last_result = (-1, '', 'Not executed')
    while attempt <= max_attempts:
        rc, out, err = fn()
        last_result = (rc, out, err)
        if rc == 0:
            return rc, out, err
        # Backoff and retry
        if attempt < max_attempts:
            time.sleep(max(delay, 0))
            delay *= backoff if backoff > 0 else 1.0
        attempt += 1
    return last_result


@contextmanager
def track_process(process: subprocess.Popen):
    """Track subprocess for automatic cleanup with enhanced safety"""
    global _active_processes, _cleanup_in_progress
    
    # Don't add if cleanup is in progress
    if not _cleanup_in_progress:
        with _process_lock:
            if process not in _active_processes:
                _active_processes.append(process)
    
    try:
        yield process
    finally:
        # Safe removal
        if not _cleanup_in_progress:
            with _process_lock:
                try:
                    if process in _active_processes:
                        _active_processes.remove(process)
                except ValueError:
                    # Process already removed, ignore
                    pass


def cleanup_processes():
    """Cleanup all tracked processes with enhanced error handling"""
    global _active_processes, _cleanup_in_progress
    
    # Mark cleanup in progress to prevent race conditions
    _cleanup_in_progress = True
    
    try:
        with _process_lock:
            processes_to_clean = list(_active_processes)  # Create snapshot
            _active_processes.clear()  # Clear immediately to prevent additions
        
        cleanup_errors = []
        
        for process in processes_to_clean:
            try:
                if process.poll() is None:  # Process still running
                    # Try graceful termination first
                    process.terminate()
                    
                    # Wait with timeout for graceful shutdown
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        # Force kill if graceful termination failed
                        print(f"⚠️ Process {process.pid} did not terminate gracefully, forcing kill")
                        try:
                            process.kill()
                            process.wait(timeout=2)
                        except subprocess.TimeoutExpired:
                            # Process is really stuck, log and continue
                            cleanup_errors.append(f"Process {process.pid} is unresponsive")
                        except (ProcessLookupError, PermissionError) as e:
                            cleanup_errors.append(f"Process {process.pid}: {e}")
                            
            except (OSError, ProcessLookupError, PermissionError) as e:
                # Process might already be gone, log and continue
                cleanup_errors.append(f"Process {getattr(process, 'pid', 'unknown')}: {e}")
            except Exception as e:
                # Unexpected error, log but don't crash
                cleanup_errors.append(f"Unexpected error: {type(e).__name__}: {e}")
        
        # Report cleanup errors if any
        if cleanup_errors:
            print(f"⚠️ Cleanup completed with {len(cleanup_errors)} error(s):")
            for error in cleanup_errors[:5]:  # Limit output
                print(f"   - {error}")
            if len(cleanup_errors) > 5:
                print(f"   ... and {len(cleanup_errors) - 5} more")
        
        return len(cleanup_errors) == 0
        
    finally:
        # Always reset cleanup flag
        _cleanup_in_progress = False


# Register cleanup on exit
import atexit
atexit.register(cleanup_processes)


def generate_commands(filepath: str, container: str, master: str) -> str:
    """Generate docker commands for the given file"""
    if not filepath:
        return ""
    
    path = Path(filepath)
    filename = path.name
    
    if not filename.endswith('.py'):
        filename += '.py'
    
    base = filename[:-3]

    original = (
        f"// Các lệnh thủ công:\n"
        f"// 1. Copy file\n"
        f"docker cp {filepath} {container}:/tmp\n"
        f"// 2. Mở bash (tương tác)\n"
        f"docker exec -it {container} bash\n"
        f"// 3. Chạy Spark (trong bash)\n"
        f"/spark/bin/spark-submit --master {master} /tmp/{filename}\n"
    )

    non_interactive = (
        f"\n// Lệnh tự động (non-interactive):\n"
        f"docker cp {filepath} {container}:/tmp\n"
        f"docker exec {container} /spark/bin/spark-submit --master {master} /tmp/{filename}\n"
    )

    return original + non_interactive


def run_docker_command(cmd_list, log_callback=None, timeout=None, stream_output=False):
    """
    Run a Docker command and return result with proper resource management
    
    Args:
        cmd_list: List of command arguments
        log_callback: Function to call with log messages (message, tag)
        timeout: Optional timeout in seconds
        stream_output: If True, stream output line by line in realtime
        
    Returns:
        tuple: (returncode, stdout, stderr)
        
    Raises:
        ValueError: If cmd_list is invalid
    """
    # Input validation
    if not cmd_list or not isinstance(cmd_list, list):
        raise ValueError("cmd_list must be a non-empty list")
    
    # Security: Validate docker command
    if cmd_list[0] not in ['docker', 'docker-compose']:
        raise ValueError(f"Unsupported command: {cmd_list[0]}")
    
    # Apply rate limiting if available
    if ADVANCED_FEATURES and rate_limiter:
        try:
            if not rate_limiter.acquire(timeout=5.0):
                if log_callback:
                    log_callback('⚠️ Rate limit exceeded, please wait...', 'warning')
                return -1, '', 'Rate limit exceeded'
        except Exception as e:
            # Rate limiting failed, continue anyway
            print(f"⚠️ Rate limiter error: {e}")
    
    # Record metrics
    start_time = time.time()
    
    if log_callback:
        log_callback(f'💻 $ {" ".join(cmd_list)}', 'info')
    elif _logger:
        _logger.info(f'$ {" ".join(cmd_list)}')
    
    try:
        if stream_output and log_callback:
            # Stream output in realtime - Use hidden console on Windows
            process = popen_hidden(
                cmd_list,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,  # Line buffered
                universal_newlines=True
            )
            
            # Track process for cleanup
            with track_process(process):
                stdout_lines = []
                stderr_lines = []
                
                import select
                import sys
                
                # For Windows, we need different approach
                if sys.platform == 'win32':
                    import threading
                    
                    # Thread-safe locks for list operations
                    stdout_lock = threading.Lock()
                    stderr_lock = threading.Lock()
                    
                    def read_stdout():
                        try:
                            for line in process.stdout:
                                if line:
                                    with stdout_lock:  # Thread-safe append
                                        stdout_lines.append(line)
                                    log_callback(line.rstrip(), 'normal')
                        except Exception as e:
                            print(f"⚠️ Error reading stdout: {e}")
                    
                    def read_stderr():
                        try:
                            for line in process.stderr:
                                if line:
                                    with stderr_lock:  # Thread-safe append
                                        stderr_lines.append(line)
                                    log_callback(line.rstrip(), 'warning')
                        except Exception as e:
                            print(f"⚠️ Error reading stderr: {e}")
                    
                    stdout_thread = threading.Thread(target=read_stdout, daemon=True)
                    stderr_thread = threading.Thread(target=read_stderr, daemon=True)
                    
                    stdout_thread.start()
                    stderr_thread.start()
                    
                    # Wait for process with timeout
                    try:
                        returncode = process.wait(timeout=timeout)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        if log_callback:
                            log_callback(f'⏱️ Command timed out after {timeout}s', 'warning')
                        elif _logger:
                            _logger.warning(f'Command timed out after {timeout}s')
                        return -1, '', 'Timeout'
                    finally:
                        # Ensure threads are joined
                        stdout_thread.join(timeout=2)
                        stderr_thread.join(timeout=2)
                    
                    # Thread-safe join
                    with stdout_lock:
                        stdout_output = ''.join(stdout_lines)
                    with stderr_lock:
                        stderr_output = ''.join(stderr_lines)
                    
                    return returncode, stdout_output, stderr_output
                
                else:
                    # Unix-like systems - use select
                    import select
                    
                    outputs = [process.stdout, process.stderr]
                    
                    while outputs:
                        readable, _, _ = select.select(outputs, [], [], 0.1)
                        
                        for output in readable:
                            line = output.readline()
                            if line:
                                if output == process.stdout:
                                    stdout_lines.append(line)
                                    log_callback(line.rstrip(), 'normal')
                                else:
                                    stderr_lines.append(line)
                                    log_callback(line.rstrip(), 'warning')
                            else:
                                outputs.remove(output)
                        
                        # Check if process finished
                        if process.poll() is not None:
                            break
                    
                    returncode = process.wait(timeout=timeout)
                    result = returncode, ''.join(stdout_lines), ''.join(stderr_lines)
                    
                    # Record metrics
                    if ADVANCED_FEATURES and metrics_collector:
                        duration = time.time() - start_time
                        metrics_collector.record_duration('docker_command', duration, 
                                                         command=cmd_list[1] if len(cmd_list) > 1 else 'unknown')
                        metrics_collector.record_count('docker_command_total')
                        if returncode == 0:
                            metrics_collector.record_count('docker_command_success')
                        else:
                            metrics_collector.record_count('docker_command_error')
                    
                    return result
        
        else:
            # Normal execution (no streaming) - Use hidden console on Windows
            effective_timeout = timeout if timeout is not None else 60
            result = run_hidden(
                cmd_list,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=effective_timeout
            )
            
            # Record metrics
            if ADVANCED_FEATURES and metrics_collector:
                duration = time.time() - start_time
                metrics_collector.record_duration('docker_command', duration,
                                                 command=cmd_list[1] if len(cmd_list) > 1 else 'unknown')
                metrics_collector.record_count('docker_command_total')
                if result.returncode == 0:
                    metrics_collector.record_count('docker_command_success')
                else:
                    metrics_collector.record_count('docker_command_error')
            
            return result.returncode, result.stdout, result.stderr
    
    except subprocess.TimeoutExpired as e:
        if log_callback:
            log_callback(f'⏱️ Command timed out after {timeout}s', 'warning')
        elif _logger:
            _logger.warning(f'Command timed out after {timeout}s')
        if _err_handler:
            _err_handler.handle_error(e, context='run_docker_command timeout', severity=ErrorSeverity.HIGH)
        return -1, '', f'Command timeout after {timeout}s'
    
    except subprocess.SubprocessError as e:
        # Specific subprocess errors (CalledProcessError, etc.)
        if log_callback:
            log_callback(f'❌ Subprocess error: {e}', 'error')
        elif _logger:
            _logger.error(f'Subprocess error: {e}')
        if _err_handler:
            _err_handler.handle_error(e, context='run_docker_command subprocess', severity=ErrorSeverity.HIGH)
        return -1, '', f'Subprocess failed: {e}'
    
    except FileNotFoundError as e:
        # Docker executable not found
        if log_callback:
            log_callback('❌ Docker executable not found. Is Docker installed?', 'error')
        elif _logger:
            _logger.critical('Docker executable not found. Is Docker installed?')
        if _err_handler:
            _err_handler.handle_error(e, context='run_docker_command docker not found', severity=ErrorSeverity.CRITICAL)
        return -1, '', 'Docker not found. Please install Docker.'
    
    except PermissionError as e:
        # Permission denied to execute Docker
        if log_callback:
            log_callback(f'❌ Permission denied: {e}', 'error')
        elif _logger:
            _logger.error(f'Permission denied: {e}')
        if _err_handler:
            _err_handler.handle_error(e, context='run_docker_command permission', severity=ErrorSeverity.HIGH)
        return -1, '', 'Permission denied. Please check Docker permissions.'
    
    except OSError as e:
        # OS-level errors (file descriptors, etc.)
        if log_callback:
            log_callback(f'❌ OS error: {e}', 'error')
        elif _logger:
            _logger.error(f'OS error: {e}')
        if _err_handler:
            _err_handler.handle_error(e, context='run_docker_command os error', severity=ErrorSeverity.HIGH)
        return -1, '', f'System error: {e}'
    
    except Exception as e:
        # Catch any other unexpected errors
        if log_callback:
            log_callback(f'❌ Unexpected error running command: {type(e).__name__}: {e}', 'error')
        elif _logger:
            _logger.error(f'Unexpected error running command: {type(e).__name__}: {e}')
        import traceback
        traceback.print_exc()
        if _err_handler:
            _err_handler.handle_error(e, context='run_docker_command unexpected', severity=ErrorSeverity.HIGH)
        return -1, '', f'Unexpected error: {type(e).__name__}: {e}'


def copy_file_to_container(filepath, container, log_callback=None):
    """
    Copy a file to Docker container with security validation
    
    Args:
        filepath: Local file path to copy
        container: Container name
        log_callback: Function for logging messages
    
    Returns:
        bool: True if successful
        
    Raises:
        ValueError: If parameters are invalid
    """
    # Validate inputs
    if not filepath:
        if log_callback:
            log_callback('❌ Filepath cannot be empty', 'error')
        return False
    
    if not container:
        if log_callback:
            log_callback('❌ Container name cannot be empty', 'error')
        return False
    
    # Validate container name (basic security check)
    try:
        from security_validator import SecurityValidator
        is_valid, error = SecurityValidator.validate_container_name(container)
        if not is_valid:
            if log_callback:
                log_callback(f'❌ Invalid container name: {error}', 'error')
            return False
    except ImportError:
        # Security validator not available, continue with basic validation
        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9_.-]*$', container):
            if log_callback:
                log_callback('❌ Invalid container name format', 'error')
            return False
    
    # Check file existence
    if not os.path.exists(filepath):
        if log_callback:
            log_callback(f'❌ File not found: {filepath}', 'error')
        return False
    
    # Check if it's actually a file
    if not os.path.isfile(filepath):
        if log_callback:
            log_callback(f'❌ Path is not a file: {filepath}', 'error')
        return False
    
    if log_callback:
        log_callback(f'→ Copying {Path(filepath).name} to container...', 'info')
    
    cmd = ['docker', 'cp', filepath, f'{container}:/tmp']
    
    try:
        # Use local retry wrapper so policy can be tuned at runtime
        def _run():
            return run_docker_command(cmd, log_callback, timeout=30)
        returncode, stdout, stderr = _execute_with_retry(
            _run,
            max_attempts=RETRY_POLICY.get('copy_max_attempts', 3),
            initial_delay=RETRY_POLICY.get('initial_delay', 0.5),
            backoff=RETRY_POLICY.get('backoff', 2.0),
        )
        
        if stdout and log_callback:
            log_callback(f'  {stdout.strip()}', 'normal')
        if stderr and log_callback:
            log_callback(f'  ⚠️ {stderr.strip()}', 'warning')
        
        if returncode == 0:
            if log_callback:
                log_callback('✅ File copied successfully', 'success')
            return True
        else:
            if log_callback:
                log_callback(f'❌ Copy failed with code {returncode}', 'error')
            return False
            
    except Exception as e:
        if log_callback:
            log_callback(f'❌ Exception during file copy: {type(e).__name__}: {e}', 'error')
        if _err_handler:
            _err_handler.handle_error(e, context='copy_file_to_container', severity=ErrorSeverity.HIGH)
        return False


def submit_spark_job(container, master, filename, log_callback=None, timeout=300):
    """
    Submit Spark job to container with realtime output streaming
    
    Args:
        container: Container name
        master: Spark master URL
        filename: Python filename (already in /tmp/)
        log_callback: Logging function
        timeout: Timeout in seconds (default 300 = 5 minutes)
        
    Returns:
        bool: True if successful
    """
    if log_callback:
        log_callback(f'→ Submitting Spark job: {filename}', 'info')
        log_callback('📊 Streaming realtime output...', 'info')
        log_callback('=' * 70, 'header')
    
    # Basic input hardening
    try:
        from security_validator import SecurityValidator
        is_valid, error = SecurityValidator.validate_container_name(container)
        if not is_valid:
            if log_callback:
                log_callback(f'❌ Invalid container name: {error}', 'error')
            return False
    except Exception:
        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9_.-]*$', str(container)):
            if log_callback:
                log_callback('❌ Invalid container name format', 'error')
            return False

    if not filename or '..' in filename or '/' in filename or '\\' in filename:
        if log_callback:
            log_callback('❌ Invalid filename', 'error')
        return False

    # Accept master that startswith spark://, local, yarn
    if not (str(master).startswith('spark://') or str(master).startswith('local') or str(master).startswith('yarn')):
        if log_callback:
            log_callback('❌ Invalid master URL', 'error')
        return False

    cmd = [
        'docker', 'exec', container,
        '/spark/bin/spark-submit', '--master', master, f'/tmp/{filename}'
    ]
    
    # Storage cho output để parse errors
    collected_output = {'stdout': '', 'stderr': ''}
    
    def _run_with_output_collection():
        returncode, stdout, stderr = run_docker_command(cmd, log_callback, timeout=timeout, stream_output=True)
        collected_output['stdout'] = stdout
        collected_output['stderr'] = stderr
        return returncode, stdout, stderr
    
    # Chỉ retry 1 lần (không phải 2) để tránh spam
    returncode, stdout, stderr = _execute_with_retry(
        _run_with_output_collection,
        max_attempts=1,  # Chỉ chạy 1 lần, retry logic sẽ ở bên ngoài
        initial_delay=0,
        backoff=1.0,
    )
    
    if log_callback:
        log_callback('=' * 70, 'header')
    
    # SMART DETECTION: Phát hiện lỗi ngay cả khi returncode = 0
    full_output = collected_output['stdout'] + collected_output['stderr']
    is_failed, error_type, error_details = _detect_job_failure(full_output, returncode)
    
    if not is_failed:
        # Thành công thật sự
        if log_callback:
            log_callback('✅ Spark job completed successfully', 'success')
        return (True, None)
    else:
        # THẤT BẠI - Phân loại và hiển thị lỗi cụ thể
        if error_type == 'missing_module':
            missing_module = error_details
            if log_callback:
                log_callback(f'❌ Spark job failed: Missing Python module', 'error')
                log_callback('=' * 70, 'header')
                log_callback(f'📦 THIẾU THỦ VIỆN: {missing_module}', 'error')
                log_callback(f'💡 Giải pháp:', 'info')
                log_callback(f'   1. Vào tab "🐍 Python Packages"', 'info')
                log_callback(f'   2. Chọn container: spark-worker', 'info')
                log_callback(f'   3. Nhập tên thư viện: {missing_module}', 'info')
                log_callback(f'   4. Nhấn "Cài đặt"', 'info')
                log_callback(f'   5. Sau khi cài xong, chạy lại job này', 'info')
                log_callback('=' * 70, 'header')
            return (False, missing_module)
        
        elif error_type == 'hdfs_error':
            hdfs_error = error_details
            if log_callback:
                log_callback(f'❌ Spark job failed: HDFS Error', 'error')
                log_callback('=' * 70, 'header')
                log_callback(f'📁 {hdfs_error["message"]}', 'error')
                log_callback(f'🔍 Path: {hdfs_error["path"]}', 'error')
                log_callback(f'', 'info')
                log_callback(f'💡 Giải pháp:', 'info')
                log_callback(f'   1. Vào tab "📤 HDFS Upload"', 'info')
                log_callback(f'   2. Upload file cần thiết lên HDFS', 'info')
                log_callback(f'   3. Đảm bảo đường dẫn đúng: {hdfs_error["path"]}', 'info')
                log_callback(f'   4. Sau khi upload xong, chạy lại job này', 'info')
                log_callback('=' * 70, 'header')
            return (False, None)
        
        elif error_type == 'runtime_error':
            if log_callback:
                log_callback(f'❌ Spark job failed: Runtime Error', 'error')
                log_callback(f'💡 Kiểm tra log ở trên để biết chi tiết lỗi', 'info')
            return (False, None)
        
        else:
            # Unknown error
            if log_callback:
                log_callback(f'❌ Spark job failed with code {returncode}', 'error')
            
            if _err_handler:
                try:
                    from subprocess import CalledProcessError
                    _err_handler.handle_error(
                        CalledProcessError(returncode, cmd),
                        context='submit_spark_job',
                        severity=ErrorSeverity.HIGH
                    )
                except Exception as e:
                    _err_handler.handle_error(e, context='submit_spark_job', severity=ErrorSeverity.HIGH)
            return (False, None)


def _parse_missing_module(output):
    """
    Parse output để tìm missing module
    
    Returns:
        str: Tên module bị thiếu, hoặc None
    """
    import re
    
    # Pattern: "ModuleNotFoundError: No module named 'pandas'"
    match = re.search(r"ModuleNotFoundError: No module named '(\w+)'", output)
    if match:
        return match.group(1)
    
    # Pattern: "ImportError: cannot import name 'xxx' from 'yyy'"
    match = re.search(r"ImportError:.*from '(\w+)'", output)
    if match:
        return match.group(1)
    
    return None


def _parse_hdfs_error(output):
    """
    Parse output để phát hiện lỗi HDFS
    
    Returns:
        dict: {'type': 'file_not_found', 'path': '...'} hoặc None
    """
    import re
    
    # Pattern 1: "Input path does not exist: hdfs://namenode:8020/input/file.txt"
    match = re.search(r'Input path does not exist: (hdfs://[^\s\n]+)', output)
    if match:
        return {
            'type': 'file_not_found',
            'path': match.group(1),
            'message': 'File hoặc thư mục không tồn tại trên HDFS'
        }
    
    # Pattern 2: "Path does not exist: hdfs://..."
    match = re.search(r'Path does not exist: (hdfs://[^\s\n]+)', output)
    if match:
        return {
            'type': 'file_not_found',
            'path': match.group(1),
            'message': 'File hoặc thư mục không tồn tại trên HDFS'
        }
    
    # Pattern 3: "FileNotFoundException: File does not exist: /input/..."
    match = re.search(r'FileNotFoundException.*File does not exist: ([^\s\n]+)', output)
    if match:
        return {
            'type': 'file_not_found',
            'path': match.group(1),
            'message': 'File không tồn tại trên HDFS'
        }
    
    # Pattern 4: "java.io.FileNotFoundException"
    if 'FileNotFoundException' in output or 'InvalidInputException' in output:
        # Extract path from context
        match = re.search(r'(hdfs://[^\s\n]+|/[^\s\n]+\.(?:txt|csv|json|parquet))', output)
        if match:
            return {
                'type': 'file_not_found',
                'path': match.group(1),
                'message': 'File không tồn tại trên HDFS'
            }
    
    return None


def _detect_job_failure(output, returncode):
    """
    Phát hiện job thất bại ngay cả khi returncode = 0
    
    Returns:
        tuple: (is_failed, error_type, error_details)
    """
    # Nếu returncode != 0 thì chắc chắn failed
    if returncode != 0:
        # Check các loại lỗi cụ thể
        missing_module = _parse_missing_module(output)
        if missing_module:
            return (True, 'missing_module', missing_module)
        
        hdfs_error = _parse_hdfs_error(output)
        if hdfs_error:
            return (True, 'hdfs_error', hdfs_error)
        
        return (True, 'unknown', None)
    
    # returncode = 0 nhưng có thể vẫn failed (do try-catch trong Python)
    # Phát hiện qua keywords trong output
    
    # Check lỗi HDFS
    hdfs_error = _parse_hdfs_error(output)
    if hdfs_error:
        return (True, 'hdfs_error', hdfs_error)
    
    # Check các keywords báo lỗi (chỉ những keywords chắc chắn báo lỗi)
    critical_error_keywords = [
        'Đã xảy ra lỗi trong quá trình xử lý Spark',  # Vietnamese error message
        'An error occurred while calling',             # PySpark error
    ]
    
    for keyword in critical_error_keywords:
        if keyword in output:
            # Có lỗi nhưng không xác định được loại
            return (True, 'runtime_error', None)
    
    # Check exception patterns (chỉ những exception nghiêm trọng)
    if ('Exception:' in output or 'Error:' in output) and ('at org.apache.spark' in output or 'at org.apache.hadoop' in output):
        # Java exception từ Spark/Hadoop → lỗi thật
        return (True, 'runtime_error', None)
    
    # Không phát hiện lỗi
    return (False, None, None)


def clear_hdfs_output(container, output_path, log_callback=None):
    """
    Clear HDFS output directory if exists
    
    Args:
        container: Container name (e.g., 'namenode')
        output_path: HDFS output path (e.g., 'hdfs://namenode:8020/output')
        log_callback: Logging function
        
    Returns:
        bool: True if cleared or not exists, False if error
    """
    # Extract path without hdfs:// prefix
    if output_path.startswith('hdfs://'):
        # Parse: hdfs://namenode:8020/output -> /output
        parts = output_path.split('/', 3)
        if len(parts) >= 4:
            hdfs_dir = '/' + parts[3]
        else:
            hdfs_dir = '/'
    else:
        hdfs_dir = output_path
    
    if log_callback:
        log_callback(f'→ Checking output directory: {hdfs_dir}', 'info')
    
    # Check if directory exists
    check_cmd = ['docker', 'exec', container, 'hdfs', 'dfs', '-test', '-e', hdfs_dir]
    returncode, _, _ = run_docker_command(check_cmd, None, timeout=10)
    
    if returncode == 0:
        # Directory exists, delete it
        if log_callback:
            log_callback(f'  ⚠️ Output directory exists, deleting...', 'warning')
        
        delete_cmd = ['docker', 'exec', container, 'hdfs', 'dfs', '-rm', '-r', '-f', hdfs_dir]
        returncode, stdout, stderr = run_docker_command(delete_cmd, None, timeout=30)
        
        if returncode == 0:
            if log_callback:
                log_callback(f'  ✓ Output directory cleared', 'success')
            return True
        else:
            if log_callback:
                log_callback(f'  ❌ Failed to delete: {stderr}', 'error')
            if _err_handler:
                try:
                    from subprocess import CalledProcessError
                    _err_handler.handle_error(
                        CalledProcessError(returncode, delete_cmd),
                        context='clear_hdfs_output delete',
                        severity=ErrorSeverity.MEDIUM
                    )
                except Exception as e:
                    _err_handler.handle_error(e, context='clear_hdfs_output delete', severity=ErrorSeverity.MEDIUM)
            return False
    else:
        # Directory doesn't exist, that's fine
        if log_callback:
            log_callback(f'  ✓ Output directory does not exist (OK)', 'success')
        return True


@timed('auto_run_spark_job')
def auto_run_spark_job(filepath, container, master, log_callback=None, stop_check=None):
    """
    Automatically run Spark job (copy file + submit job)
    Enhanced with database tracking and auto-start Docker
    
    Args:
        filepath: Path to Python file
        container: Docker container name
        master: Spark master URL
        log_callback: Function for logging (message, tag)
        stop_check: Function that returns True if should stop
        
    Returns:
        bool: True if successful
    """
    # Initialize database tracking
    job_id = None
    start_time = datetime.now()
    
    if log_callback:
        log_callback('=' * 70, 'header')
        log_callback('🚀 STARTING AUTOMATED SPARK JOB', 'header')
        log_callback('=' * 70, 'header')
    
    # Optional: quick health pre-check (non-blocking)
    try:
        from health_check import health_checker
        hc = health_checker.check_docker_daemon()
        if hc.status != 'healthy' and log_callback:
            log_callback(f'⚠️ Docker daemon status: {hc.status} - {hc.message}', 'warning')
    except Exception:
        pass

    # Check and auto-start Docker if needed
    if DOCKER_AUTO_START:
        if not is_docker_running():
            if log_callback:
                log_callback('\n🐳 Docker not running - Starting Docker Desktop...', 'warning')
            
            docker_ready, message = ensure_docker_running(
                log_callback=log_callback,
                auto_start=True,
                wait=True
            )
            
            if not docker_ready:
                if log_callback:
                    log_callback(f'❌ {message}', 'error')
                    log_callback('Please start Docker Desktop manually and try again.', 'error')
                return False
    
    # Initialize database tracking
    if ENHANCED_FEATURES:
        try:
            job_id = db.add_job({
                'job_name': Path(filepath).stem,
                'file_path': filepath,
                'status': 'running',
                'start_time': start_time.isoformat(),
                'container': container,
                'master': master
            })
            if log_callback:
                log_callback(f'📝 Job tracking ID: {job_id}', 'info')
        except Exception as e:
            if log_callback:
                log_callback(f'⚠️ Database tracking unavailable: {e}', 'warning')
    
    # Check Docker availability
    if not shutil.which('docker'):
        if log_callback:
            log_callback('❌ Docker not found in PATH', 'error')
        # Update database on failure
        if ENHANCED_FEATURES and job_id:
            try:
                db.update_job(job_id, {
                    'status': 'failed',
                    'end_time': datetime.now().isoformat(),
                    'error': 'Docker not found in PATH'
                })
            except Exception as db_error:
                if log_callback:
                    log_callback(f'⚠️ Database update failed: {db_error}', 'warning')
        return False
    
    # Step 0: Clear output directory (auto-detect from common patterns)
    if log_callback:
        log_callback('\n→ STEP 0: Clear previous output', 'info')
    
    # Try to detect output path from file
    output_paths = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # Look for common output patterns
            import re
            # Match: saveAsTextFile("hdfs://...") or saveAsTextFile('/output')
            matches = re.findall(r'saveAsTextFile\(["\']([^"\']+)["\']\)', content)
            if matches:
                output_paths = matches
    except Exception as e:
        if log_callback:
            log_callback(f'  ⚠️ Could not scan file for output paths: {e}', 'warning')
    
    # Clear detected output paths
    if output_paths:
        for output_path in output_paths:
            if log_callback:
                log_callback(f'  📁 Detected output: {output_path}', 'info')
            try:
                clear_hdfs_output('namenode', output_path, log_callback)
            except Exception as e:
                if log_callback:
                    log_callback(f'  ⚠️ Could not clear output path: {e}', 'warning')
    else:
        if log_callback:
            log_callback('  ℹ️  No output paths detected in code', 'info')
    
    # Check if should stop
    if stop_check and stop_check():
        if log_callback:
            log_callback('⏹️ Stopped by user request', 'warning')
        # Update database
        if ENHANCED_FEATURES and job_id:
            try:
                db.update_job(job_id, {
                    'status': 'cancelled',
                    'end_time': datetime.now().isoformat(),
                    'error': 'Stopped by user'
                })
            except Exception as e:
                if log_callback:
                    log_callback(f'⚠️ Could not update job status: {e}', 'warning')
        return False
    
    # Step 1: Copy file
    if log_callback:
        log_callback('\n→ STEP 1: Copy file to container', 'info')
    
    if not copy_file_to_container(filepath, container, log_callback):
        # Update database on failure
        if ENHANCED_FEATURES and job_id:
            try:
                db.update_job(job_id, {
                    'status': 'failed',
                    'end_time': datetime.now().isoformat(),
                    'error': 'Failed to copy file to container'
                })
            except Exception as e:
                if log_callback:
                    log_callback(f'⚠️ Could not update job status: {e}', 'warning')
        return False
    
    # Check if should stop
    if stop_check and stop_check():
        if log_callback:
            log_callback('⏹️ Stopped by user request', 'warning')
        # Update database
        if ENHANCED_FEATURES and job_id:
            try:
                db.update_job(job_id, {
                    'status': 'cancelled',
                    'end_time': datetime.now().isoformat(),
                    'error': 'Stopped by user after file copy'
                })
            except Exception as e:
                if log_callback:
                    log_callback(f'⚠️ Could not update job status: {e}', 'warning')
        return False
    
    # Step 2: Submit Spark job
    if log_callback:
        log_callback('\n→ STEP 2: Submit Spark job', 'info')
    
    filename = Path(filepath).name
    result = submit_spark_job(container, master, filename, log_callback, timeout=300)
    
    # Handle tuple return (success, missing_module)
    if isinstance(result, tuple):
        success, missing_module = result
    else:
        # Backwards compatibility
        success = result
        missing_module = None

    # Fallback: if failed, try recovery and retry once
    # NHƯNG: Skip retry nếu là lỗi thiếu module (retry vô ích)
    if not success:
        if missing_module:
            if log_callback:
                log_callback('⚠️ Không thể retry vì thiếu thư viện Python', 'warning')
                log_callback(f'📦 Vui lòng cài đặt "{missing_module}" và chạy lại', 'info')
            # Skip retry - không có ý nghĩa
        elif stop_check and stop_check():
            if log_callback:
                log_callback('⏹️ Stopped by user before retry', 'warning')
        else:
            if log_callback:
                log_callback('🔁 Attempting recovery: clean stale processes and retry...', 'warning')
            
            # BƯỚC 1: Kiểm tra container có đang chạy không
            check_cmd = ['docker', 'inspect', '-f', '{{.State.Running}}', container]
            returncode, stdout, stderr = run_docker_command(check_cmd, None, timeout=10)
            
            is_running = stdout.strip().lower() == 'true'
            
            if not is_running:
                if log_callback:
                    log_callback('⚠️ Container bị tắt! Đang khởi động lại...', 'warning')
                
                # Restart container
                restart_cmd = ['docker', 'start', container]
                returncode, stdout, stderr = run_docker_command(restart_cmd, log_callback, timeout=30)
                
                if returncode == 0:
                    if log_callback:
                        log_callback('✅ Container đã khởi động lại thành công', 'success')
                    time.sleep(5)  # Đợi container khởi động đầy đủ
                else:
                    if log_callback:
                        log_callback('❌ Không thể khởi động lại container!', 'error')
                    # Update database on recovery failure
                    if ENHANCED_FEATURES and job_id:
                        try:
                            db.update_job(job_id, {
                                'status': 'failed',
                                'end_time': datetime.now().isoformat(),
                                'error': 'Cannot restart container'
                            })
                        except Exception:
                            pass
                    # Mark as failed - cannot recover
                    success = False
            else:
                # BƯỚC 2: Container đang chạy → clean stale processes
                try:
                    force_kill_spark_jobs(container, log_callback)
                except Exception as e:
                    if log_callback:
                        log_callback(f'⚠️ Cleanup warning: {str(e)}', 'warning')
                
                time.sleep(2)
            
            # BƯỚC 3: Retry job
            retry_result = submit_spark_job(container, master, filename, log_callback, timeout=300)
            if isinstance(retry_result, tuple):
                success, _ = retry_result
            else:
                success = retry_result
    
    # Calculate duration
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    if success:
        if log_callback:
            log_callback('=' * 70, 'header')
            log_callback('🎉 ALL STEPS COMPLETED SUCCESSFULLY!', 'success')
            log_callback(f'⏱️  Total duration: {duration:.2f}s', 'success')
            log_callback('=' * 70, 'header')
        
        # Update database on success
        if ENHANCED_FEATURES and job_id:
            try:
                db.update_job(job_id, {
                    'status': 'success',
                    'end_time': end_time.isoformat(),
                    'duration': duration,
                    'exit_code': 0
                })
            except Exception as e:
                if log_callback:
                    log_callback(f'⚠️ Could not update job status: {e}', 'warning')
    else:
        # Update database on failure
        if ENHANCED_FEATURES and job_id:
            try:
                db.update_job(job_id, {
                    'status': 'failed',
                    'end_time': end_time.isoformat(),
                    'duration': duration,
                    'exit_code': 1,
                    'error': 'Spark job execution failed'
                })
            except Exception as e:
                if log_callback:
                    log_callback(f'⚠️ Could not update job status: {e}', 'warning')
    
    return success


def docker_compose_command(action, compose_file=None, log_callback=None, auto_start_docker=True):
    """
    Run docker-compose command with auto-start Docker Desktop
    
    Args:
        action: 'up', 'down', 'start', 'stop', 'restart', 'ps', 'build'
        compose_file: Path to docker-compose.yml
        log_callback: Logging function
        auto_start_docker: If True, auto-start Docker Desktop if not running
        
    Returns:
        tuple: (returncode, stdout, stderr)
    """
    # Validate action
    valid_actions = {'up','down','start','stop','restart','ps','build'}
    if action not in valid_actions:
        if log_callback:
            log_callback(f'❌ Invalid docker-compose action: {action}', 'error')
        elif _logger:
            _logger.error(f'Invalid docker-compose action: {action}')
        return -1, '', f'Invalid action: {action}'

    # Check and auto-start Docker if needed
    if auto_start_docker and DOCKER_AUTO_START:
        if not is_docker_running():
            if log_callback:
                log_callback('=' * 70, 'header')
                log_callback('🐳 DOCKER NOT RUNNING - AUTO-START INITIATED', 'warning')
                log_callback('=' * 70, 'header')
            
            docker_ready, message = ensure_docker_running(
                log_callback=log_callback,
                auto_start=True,
                wait=True
            )
            
            if not docker_ready:
                if log_callback:
                    log_callback('=' * 70, 'header')
                    log_callback(f'❌ {message}', 'error')
                    log_callback('=' * 70, 'header')
                return -1, '', message
            
            if log_callback:
                log_callback('=' * 70, 'header')
    
    # Prefer docker-compose if available, else fall back to 'docker compose'
    compose_cmd = 'docker-compose'
    try:
        from docker_utils import check_docker_compose
        available, _version, detected_cmd = check_docker_compose()
        if available and detected_cmd:
            compose_cmd = detected_cmd
    except Exception:
        # Silent fallback
        pass

    # Build command list (split plugin form into list)
    if compose_cmd == 'docker compose':
        cmd = ['docker', 'compose']
    else:
        cmd = ['docker-compose']
    
    if compose_file:
        cmd.extend(['-f', compose_file])
    
    cmd.append(action)
    
    # Add flags based on action
    if action == 'up':
        cmd.extend(['-d'])  # Detached mode
    elif action == 'down':
        cmd.extend(['-v'])  # Remove volumes
    
    def _run():
        return run_docker_command(cmd, log_callback, timeout=120)
    rc, out, err = _execute_with_retry(
        _run,
        max_attempts=RETRY_POLICY.get('compose_max_attempts', 3),
        initial_delay=RETRY_POLICY.get('initial_delay', 0.5),
        backoff=RETRY_POLICY.get('backoff', 2.0),
    )
    if rc != 0 and _err_handler:
        try:
            from subprocess import CalledProcessError
            _err_handler.handle_error(
                CalledProcessError(rc, cmd),
                context=f'docker_compose_command {action}',
                severity=ErrorSeverity.HIGH
            )
        except Exception as e:
            _err_handler.handle_error(e, context=f'docker_compose_command {action}', severity=ErrorSeverity.HIGH)
    return rc, out, err


@timed('get_container_status')
def get_container_status(container, log_callback=None):
    """
    Get Docker container status with caching
    
    Returns:
        str: 'running', 'exited', 'paused', 'not_found', 'error'
    """
    # Try cache first (10s TTL)
    if ENHANCED_FEATURES:
        cache_key = f'container_status_{container}'
        cached_status = cache_manager.get('docker_status', cache_key)
        if cached_status:
            if log_callback:
                log_callback(f'  ⚡ Using cached status for {container}', 'info')
            return cached_status
    
    cmd = ['docker', 'inspect', '-f', '{{.State.Status}}', container]
    returncode, stdout, stderr = run_docker_command(cmd, log_callback=None, timeout=10)
    
    if returncode == 0:
        status = stdout.strip().lower()
        # Cache the result
        if ENHANCED_FEATURES:
            cache_manager.set('docker_status', cache_key, status)
        return status
    else:
        if 'no such object' in stderr.lower() or 'not found' in stderr.lower():
            status = 'not_found'
        else:
            status = 'error'
        # Cache negative results too (shorter TTL handled by cache_manager)
        if ENHANCED_FEATURES:
            cache_manager.set('docker_status', cache_key, status)
        return status


@timed('get_docker_compose_status')
@retry_with_backoff(max_attempts=2, initial_delay=0.5)
def get_docker_compose_status(compose_file=None, log_callback=None):
    """
    Get status of all containers in docker-compose with caching
    
    Returns:
        list: List of (container_name, status) tuples
    """
    # Try cache first (10s TTL)
    if ENHANCED_FEATURES:
        cache_key = f'compose_status_{compose_file or "default"}'
        cached_status = cache_manager.get('docker_status', cache_key)
        if cached_status:
            return cached_status
    
    # Validate compose file if provided
    if compose_file:
        try:
            p = Path(compose_file)
            if not p.exists() or not p.is_file():
                return []
        except Exception:
            return []

    cmd = ['docker-compose']
    if compose_file:
        cmd.extend(['-f', compose_file])
    cmd.extend(['ps', '--format', 'json'])
    
    returncode, stdout, stderr = run_docker_command(cmd, log_callback=None, timeout=30)
    
    if returncode != 0:
        return []
    
    try:
        import json
        containers = json.loads(stdout) if stdout.strip().startswith('[') else [json.loads(line) for line in stdout.strip().split('\n') if line]
        result = [(c.get('Name', 'unknown'), c.get('State', 'unknown')) for c in containers]
        
        # Cache the result
        if ENHANCED_FEATURES:
            cache_manager.set('docker_status', cache_key, result)
        
        return result
    except (json.JSONDecodeError, ValueError, KeyError) as parse_error:
        # Fallback to simple text parsing on JSON parse error
        if log_callback:
            log_callback(f'⚠️ JSON parsing failed, using text parsing: {parse_error}', 'warning')
        
        lines = stdout.strip().split('\n')
        result = []
        for line in lines[1:]:  # Skip header
            parts = line.split()
            if len(parts) >= 2:
                result.append((parts[0], parts[1]))
        
        # Cache the result
        if ENHANCED_FEATURES:
            cache_manager.set('docker_status', cache_key, result)
            
        return result


def force_kill_spark_jobs(container, log_callback=None):
    """
    Force kill Spark Driver processes (spark-submit) ONLY, NOT Worker daemon
    
    Returns:
        bool: True if successful
    """
    if log_callback:
        log_callback('⚠️ Force killing stale Spark driver processes...', 'warning')
    
    # SAFER: Kill only spark-submit processes (drivers), NOT Worker daemon
    # Sử dụng pgrep để tìm PID của spark-submit, sau đó kill
    cmd = ['docker', 'exec', container, 'sh', '-c', 
           'pgrep -f "spark-submit" | xargs -r kill -9 2>/dev/null || true']
    
    returncode, stdout, stderr = run_docker_command(cmd, log_callback, timeout=30)
    
    # Always return True vì:
    # 1. Spark tự cleanup rất tốt (thấy log "Successfully stopped SparkContext")
    # 2. Nếu không có process nào thì cũng OK
    if log_callback:
        log_callback('✅ Stale Spark drivers cleaned (if any)', 'success')
    
    # Đợi 2 giây để cleanup hoàn tất
    import time
    time.sleep(2)
    
    return True
