"""
Spark Backend Logic - Separated from UI
Contains all Docker and Spark execution logic
"""
import subprocess
import shutil
import os
import sys
from pathlib import Path
from datetime import datetime


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
                
                def read_stdout():
                    for line in process.stdout:
                        if line:
                            stdout_lines.append(line)
                            log_callback(line.rstrip(), 'normal')
                
                def read_stderr():
                    for line in process.stderr:
                        if line:
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
                
                return returncode, ''.join(stdout_lines), ''.join(stderr_lines)
            
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


def auto_run_spark_job(filepath, container, master, log_callback=None, stop_check=None):
    """
    Automatically run Spark job (copy file + submit job)
    
    Args:
        filepath: Path to Python file
        container: Docker container name
        master: Spark master URL
        log_callback: Function for logging (message, tag)
        stop_check: Function that returns True if should stop
        
    Returns:
        bool: True if successful
    """
    if log_callback:
        log_callback('=' * 70, 'header')
        log_callback('🚀 STARTING AUTOMATED SPARK JOB', 'header')
        log_callback('=' * 70, 'header')
    
    # Check Docker availability
    if not shutil.which('docker'):
        if log_callback:
            log_callback('❌ Docker not found in PATH', 'error')
        return False
    
    # Step 0: Clear output directory (auto-detect from common patterns)
    if log_callback:
        log_callback('\n→ STEP 0: Clear previous output', 'info')
    
    # Try to detect output path from file
    output_paths = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Look for common output patterns
            import re
            # Match: saveAsTextFile("hdfs://...") or saveAsTextFile('/output')
            matches = re.findall(r'saveAsTextFile\(["\']([^"\']+)["\']\)', content)
            if matches:
                output_paths = matches
    except:
        pass
    
    # Clear detected output paths
    if output_paths:
        for output_path in output_paths:
            if log_callback:
                log_callback(f'  📁 Detected output: {output_path}', 'info')
            clear_hdfs_output('namenode', output_path, log_callback)
    else:
        if log_callback:
            log_callback('  ℹ️  No output paths detected in code', 'info')
    
    # Check if should stop
    if stop_check and stop_check():
        if log_callback:
            log_callback('⏹️ Stopped by user request', 'warning')
        return False
    
    # Step 1: Copy file
    if log_callback:
        log_callback('\n→ STEP 1: Copy file to container', 'info')
    
    if not copy_file_to_container(filepath, container, log_callback):
        return False
    
    # Check if should stop
    if stop_check and stop_check():
        if log_callback:
            log_callback('⏹️ Stopped by user request', 'warning')
        return False
    
    # Step 2: Submit Spark job
    if log_callback:
        log_callback('\n→ STEP 2: Submit Spark job', 'info')
    
    filename = Path(filepath).name
    success = submit_spark_job(container, master, filename, log_callback, timeout=300)
    
    if success:
        if log_callback:
            log_callback('=' * 70, 'header')
            log_callback('🎉 ALL STEPS COMPLETED SUCCESSFULLY!', 'success')
            log_callback('=' * 70, 'header')
    
    return success


def docker_compose_command(action, compose_file=None, log_callback=None):
    """
    Run docker-compose command
    
    Args:
        action: 'up', 'down', 'start', 'stop', 'restart', 'ps', 'build'
        compose_file: Path to docker-compose.yml
        log_callback: Logging function
        
    Returns:
        tuple: (returncode, stdout, stderr)
    """
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


def get_container_status(container, log_callback=None):
    """
    Get Docker container status
    
    Returns:
        str: 'running', 'exited', 'paused', 'not_found', 'error'
    """
    cmd = ['docker', 'inspect', '-f', '{{.State.Status}}', container]
    returncode, stdout, stderr = run_docker_command(cmd, log_callback=None, timeout=10)
    
    if returncode == 0:
        status = stdout.strip().lower()
        return status
    else:
        if 'no such object' in stderr.lower() or 'not found' in stderr.lower():
            return 'not_found'
        return 'error'


def get_docker_compose_status(compose_file=None, log_callback=None):
    """
    Get status of all containers in docker-compose
    
    Returns:
        list: List of (container_name, status) tuples
    """
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
        return [(c.get('Name', 'unknown'), c.get('State', 'unknown')) for c in containers]
    except:
        # Fallback to simple text parsing
        lines = stdout.strip().split('\n')
        result = []
        for line in lines[1:]:  # Skip header
            parts = line.split()
            if len(parts) >= 2:
                result.append((parts[0], parts[1]))
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
