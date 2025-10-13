"""
Spark Backend Logic - Separated from UI
Contains all Docker and Spark execution logic
Enhanced with caching, database tracking, and auto-start Docker Desktop (v4.4.3)
"""
import subprocess
import shutil
import os
import sys
from pathlib import Path
from datetime import datetime

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
    # Create dummy decorators
    def timed(name):
        def decorator(func):
            return func
        return decorator
    def retry_with_backoff(max_retries=3):
        def decorator(func):
            return func
        return decorator


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
    Run a Docker command and return result
    
    Args:
        cmd_list: List of command arguments
        log_callback: Function to call with log messages (message, tag)
        timeout: Optional timeout in seconds
        stream_output: If True, stream output line by line in realtime
        
    Returns:
        tuple: (returncode, stdout, stderr)
    """
    if log_callback:
        log_callback(f'💻 $ {" ".join(cmd_list)}', 'info')
    
    try:
        if stream_output and log_callback:
            # Stream output in realtime
            process = subprocess.Popen(
                cmd_list,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,  # Line buffered
                universal_newlines=True
            )
            
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
                    for line in process.stdout:
                        if line:
                            with stdout_lock:  # Thread-safe append
                                stdout_lines.append(line)
                            log_callback(line.rstrip(), 'normal')
                
                def read_stderr():
                    for line in process.stderr:
                        if line:
                            with stderr_lock:  # Thread-safe append
                                stderr_lines.append(line)
                            log_callback(line.rstrip(), 'warning')
                
                stdout_thread = threading.Thread(target=read_stdout, daemon=True)
                stderr_thread = threading.Thread(target=read_stderr, daemon=True)
                
                stdout_thread.start()
                stderr_thread.start()
                
                # Wait for process with timeout
                try:
                    returncode = process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    process.kill()
                    log_callback(f'⏱️ Command timed out after {timeout}s', 'warning')
                    return -1, '', 'Timeout'
                
                # Wait for threads to finish reading
                stdout_thread.join(timeout=1)
                stderr_thread.join(timeout=1)
                
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
                return returncode, ''.join(stdout_lines), ''.join(stderr_lines)
        
        else:
            # Normal execution (no streaming)
            result = subprocess.run(
                cmd_list,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=timeout
            )
            
            return result.returncode, result.stdout, result.stderr
    
    except subprocess.TimeoutExpired:
        if log_callback:
            log_callback(f'⏱️ Command timed out after {timeout}s', 'warning')
        return -1, '', 'Timeout'
    
    except Exception as e:
        if log_callback:
            log_callback(f'❌ Error running command: {e}', 'error')
        return -1, '', str(e)


def copy_file_to_container(filepath, container, log_callback=None):
    """
    Copy a file to Docker container
    
    Returns:
        bool: True if successful
    """
    if not os.path.exists(filepath):
        if log_callback:
            log_callback(f'❌ File not found: {filepath}', 'error')
        return False
    
    if log_callback:
        log_callback(f'→ Copying {Path(filepath).name} to container...', 'info')
    
    cmd = ['docker', 'cp', filepath, f'{container}:/tmp']
    returncode, stdout, stderr = run_docker_command(cmd, log_callback, timeout=30)
    
    if stdout:
        log_callback(f'  {stdout.strip()}', 'normal')
    if stderr:
        log_callback(f'  ⚠️ {stderr.strip()}', 'warning')
    
    if returncode == 0:
        if log_callback:
            log_callback('✅ File copied successfully', 'success')
        return True
    else:
        if log_callback:
            log_callback(f'❌ Copy failed with code {returncode}', 'error')
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
    
    cmd = [
        'docker', 'exec', container,
        '/spark/bin/spark-submit', '--master', master, f'/tmp/{filename}'
    ]
    
    # Use streaming output for realtime logs
    returncode, stdout, stderr = run_docker_command(cmd, log_callback, timeout=timeout, stream_output=True)
    
    if log_callback:
        log_callback('=' * 70, 'header')
    
    if returncode == 0:
        if log_callback:
            log_callback('✅ Spark job completed successfully', 'success')
        return True
    else:
        if log_callback:
            log_callback(f'❌ Spark job failed with code {returncode}', 'error')
        return False


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
    success = submit_spark_job(container, master, filename, log_callback, timeout=300)
    
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
    
    cmd = ['docker-compose']
    
    if compose_file:
        cmd.extend(['-f', compose_file])
    
    cmd.append(action)
    
    # Add flags based on action
    if action == 'up':
        cmd.extend(['-d'])  # Detached mode
    elif action == 'down':
        cmd.extend(['-v'])  # Remove volumes
    
    return run_docker_command(cmd, log_callback, timeout=120)


@timed('get_container_status')
@retry_with_backoff(max_attempts=2, initial_delay=0.5)
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
    Force kill all Spark processes in container
    
    Returns:
        bool: True if successful
    """
    if log_callback:
        log_callback('⚠️ Force killing Spark processes...', 'warning')
    
    # Kill java processes (Spark runs on JVM)
    cmd = ['docker', 'exec', container, 'pkill', '-9', 'java']
    returncode, stdout, stderr = run_docker_command(cmd, log_callback, timeout=30)
    
    if returncode == 0 or 'no process found' in stderr.lower():
        if log_callback:
            log_callback('✅ Spark processes terminated', 'success')
        return True
    else:
        if log_callback:
            log_callback(f'❌ Failed to kill processes: {stderr}', 'error')
        return False
