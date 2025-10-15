"""
Real-time Progress Monitor for Long-running Docker Commands
Provides feedback every 5-10 seconds during long operations
"""

import subprocess
import threading
import time
from typing import Callable, Optional, Tuple
import sys


def run_command_with_progress(
    cmd_list: list,
    log_callback: Optional[Callable[[str, str], None]] = None,
    timeout: Optional[int] = None,
    progress_interval: int = 5  # Phản hồi mỗi 5 giây
) -> Tuple[int, str, str]:
    """
    Chạy command với progress updates thường xuyên
    
    Args:
        cmd_list: Command list (e.g., ['docker', 'exec', ...])
        log_callback: Callback(message, tag) để hiển thị progress
        timeout: Timeout tổng (seconds)
        progress_interval: Khoảng thời gian giữa các updates (seconds)
    
    Returns:
        (returncode, stdout, stderr)
    """
    
    # Create subprocess params for hidden console
    params = {}
    if sys.platform == 'win32':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        params['startupinfo'] = startupinfo
        params['creationflags'] = subprocess.CREATE_NO_WINDOW
    
    # Start process
    process = subprocess.Popen(
        cmd_list,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        errors='replace',
        bufsize=1,
        **params
    )
    
    # Storage for output
    stdout_lines = []
    stderr_lines = []
    stdout_lock = threading.Lock()
    stderr_lock = threading.Lock()
    
    # Progress tracker
    start_time = time.time()
    last_progress_time = start_time
    
    def read_stdout():
        """Read stdout in separate thread"""
        try:
            for line in process.stdout:
                if line:
                    with stdout_lock:
                        stdout_lines.append(line)
                    if log_callback:
                        log_callback(line.rstrip(), 'normal')
        except Exception as e:
            print(f"⚠️ Error reading stdout: {e}")
    
    def read_stderr():
        """Read stderr in separate thread"""
        try:
            for line in process.stderr:
                if line:
                    with stderr_lock:
                        stderr_lines.append(line)
                    if log_callback:
                        log_callback(line.rstrip(), 'warning')
        except Exception as e:
            print(f"⚠️ Error reading stderr: {e}")
    
    def show_progress():
        """Show progress updates every N seconds"""
        nonlocal last_progress_time
        
        while process.poll() is None:
            time.sleep(1)  # Check every second
            
            current_time = time.time()
            elapsed = int(current_time - start_time)
            since_last = current_time - last_progress_time
            
            # Show progress every progress_interval seconds
            if since_last >= progress_interval:
                if log_callback:
                    minutes = elapsed // 60
                    seconds = elapsed % 60
                    
                    if minutes > 0:
                        log_callback(
                            f"⏰ Vẫn đang chạy... ({minutes} phút {seconds} giây đã trôi qua)",
                            'info'
                        )
                    else:
                        log_callback(
                            f"⏰ Vẫn đang chạy... ({seconds} giây đã trôi qua)",
                            'info'
                        )
                
                last_progress_time = current_time
    
    # Start threads
    stdout_thread = threading.Thread(target=read_stdout, daemon=True)
    stderr_thread = threading.Thread(target=read_stderr, daemon=True)
    progress_thread = threading.Thread(target=show_progress, daemon=True)
    
    stdout_thread.start()
    stderr_thread.start()
    progress_thread.start()
    
    # Wait for process with timeout
    try:
        returncode = process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        if log_callback:
            log_callback(f'⏱️ Command timed out after {timeout}s', 'error')
        returncode = -1
    finally:
        # Wait for threads to finish
        stdout_thread.join(timeout=2)
        stderr_thread.join(timeout=2)
    
    # Collect output
    with stdout_lock:
        stdout_output = ''.join(stdout_lines)
    with stderr_lock:
        stderr_output = ''.join(stderr_lines)
    
    # Show completion time
    if log_callback:
        total_time = time.time() - start_time
        minutes = int(total_time // 60)
        seconds = int(total_time % 60)
        
        if returncode == 0:
            if minutes > 0:
                log_callback(
                    f"✅ Hoàn thành trong {minutes} phút {seconds} giây",
                    'success'
                )
            else:
                log_callback(
                    f"✅ Hoàn thành trong {seconds} giây",
                    'success'
                )
        else:
            log_callback(f"❌ Lỗi sau {minutes}m {seconds}s", 'error')
    
    return returncode, stdout_output, stderr_output


def run_docker_exec_with_progress(
    container: str,
    command: list,
    log_callback: Optional[Callable[[str, str], None]] = None,
    timeout: Optional[int] = None,
    progress_interval: int = 5
) -> Tuple[int, str, str]:
    """
    Chạy docker exec với progress updates
    
    Example:
        returncode, stdout, stderr = run_docker_exec_with_progress(
            container='spark-worker',
            command=['pip', 'install', 'pandas'],
            log_callback=my_log_func,
            timeout=600,
            progress_interval=10  # Cập nhật mỗi 10 giây
        )
    """
    cmd = ['docker', 'exec', container] + command
    return run_command_with_progress(cmd, log_callback, timeout, progress_interval)


def run_spark_submit_with_progress(
    container: str,
    master: str,
    script_path: str,
    log_callback: Optional[Callable[[str, str], None]] = None,
    timeout: int = 600,
    progress_interval: int = 10
) -> Tuple[int, str, str]:
    """
    Chạy spark-submit với progress updates mỗi 10 giây
    
    Example:
        returncode, stdout, stderr = run_spark_submit_with_progress(
            container='spark-worker',
            master='spark://spark-master:7077',
            script_path='/tmp/job.py',
            log_callback=my_log_func,
            progress_interval=10
        )
    """
    cmd = [
        'docker', 'exec', container,
        '/spark/bin/spark-submit',
        '--master', master,
        script_path
    ]
    
    return run_command_with_progress(cmd, log_callback, timeout, progress_interval)


# Example usage
if __name__ == "__main__":
    def test_log(msg, tag):
        print(f"[{tag}] {msg}")
    
    print("Testing progress monitor...")
    print("Running: pip install pandas (long command)")
    
    returncode, stdout, stderr = run_docker_exec_with_progress(
        container='spark-worker',
        command=['pip', 'install', 'pandas'],
        log_callback=test_log,
        timeout=900,  # 15 minutes
        progress_interval=5  # Update every 5 seconds
    )
    
    print(f"\nReturn code: {returncode}")
    print(f"Success: {returncode == 0}")
