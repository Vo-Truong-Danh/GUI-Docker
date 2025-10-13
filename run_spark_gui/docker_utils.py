"""
Docker Utilities - Auto-start Docker Desktop if not running
Supports Windows, macOS, and Linux
"""
import subprocess
import platform
import time
import os
from pathlib import Path


def is_docker_running():
    """
    Check if Docker daemon is running
    
    Returns:
        bool: True if Docker is running, False otherwise
    """
    try:
        result = subprocess.run(
            ['docker', 'info'],
            capture_output=True,
            timeout=10,  # Increased timeout from 5 to 10
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        # Timeout usually means Docker is starting or hung
        return False
    except FileNotFoundError:
        # Docker command not found
        return False
    except Exception as e:
        # Log unexpected errors
        print(f"⚠️ Unexpected error checking Docker status: {e}")
        return False


def find_docker_desktop_path():
    """
    Find Docker Desktop executable path based on OS
    
    Returns:
        str or None: Path to Docker Desktop executable
    """
    system = platform.system()
    
    if system == 'Windows':
        # Common Windows paths for Docker Desktop
        paths = [
            r"C:\Program Files\Docker\Docker\Docker Desktop.exe",
            r"C:\Program Files\Docker\Docker\frontend\Docker Desktop.exe",
            os.path.expandvars(r"%ProgramFiles%\Docker\Docker\Docker Desktop.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Docker\Docker\Docker Desktop.exe"),
        ]
        
        for path in paths:
            if os.path.exists(path):
                return path
        
        # Try to find via registry
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\Docker Desktop.exe"
            )
            path, _ = winreg.QueryValueEx(key, "")
            if os.path.exists(path):
                return path
        except:
            pass
    
    elif system == 'Darwin':  # macOS
        paths = [
            '/Applications/Docker.app',
            os.path.expanduser('~/Applications/Docker.app'),
        ]
        
        for path in paths:
            if os.path.exists(path):
                return path
    
    elif system == 'Linux':
        # Linux doesn't typically have Docker Desktop in the same way
        # Try common installation paths
        paths = [
            '/usr/bin/docker',
            '/usr/local/bin/docker',
        ]
        
        for path in paths:
            if os.path.exists(path):
                return path
    
    return None


def start_docker_desktop():
    """
    Start Docker Desktop application with enhanced error handling
    
    Returns:
        tuple: (success: bool, message: str)
    """
    system = platform.system()
    docker_path = find_docker_desktop_path()
    
    if not docker_path:
        error_msg = (
            f"Docker Desktop not found on {system}.\n"
            f"Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
        )
        return False, error_msg
    
    try:
        if system == 'Windows':
            # Start Docker Desktop in background with proper flags
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0  # SW_HIDE
            
            subprocess.Popen(
                [docker_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True, "Docker Desktop is starting... Please wait 30-60 seconds."
        
        elif system == 'Darwin':  # macOS
            subprocess.Popen(
                ['open', '-a', docker_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True, "Docker Desktop is starting... Please wait 30-60 seconds."
        
        elif system == 'Linux':
            # On Linux, try to start Docker service
            try:
                # Try systemctl first
                result = subprocess.run(
                    ['sudo', 'systemctl', 'start', 'docker'],
                    capture_output=True,
                    timeout=10,
                    text=True
                )
                if result.returncode == 0:
                    return True, "Docker service is starting..."
                else:
                    # Try service command as fallback
                    result = subprocess.run(
                        ['sudo', 'service', 'docker', 'start'],
                        capture_output=True,
                        timeout=10,
                        text=True
                    )
                    if result.returncode == 0:
                        return True, "Docker service is starting..."
                    else:
                        return False, f"Failed to start Docker service: {result.stderr}"
            except subprocess.TimeoutExpired:
                return False, "Timeout starting Docker service"
            except FileNotFoundError:
                return False, "Cannot start Docker service. Please start it manually with: sudo systemctl start docker"
        
        return False, f"Unsupported platform: {system}"
    
    except PermissionError:
        return False, f"Permission denied. Please run as administrator or check file permissions: {docker_path}"
    
    except FileNotFoundError as e:
        return False, f"File not found: {e}"
    
    except Exception as e:
        return False, f"Failed to start Docker Desktop: {type(e).__name__}: {str(e)}"


def wait_for_docker(timeout=90, log_callback=None, check_interval=2):
    """
    Wait for Docker daemon to become available with better feedback
    
    Args:
        timeout: Maximum seconds to wait
        log_callback: Optional callback for progress updates (message, tag)
        check_interval: Seconds between checks
    
    Returns:
        bool: True if Docker is running, False if timeout
    """
    start_time = time.time()
    last_log_time = 0
    attempts = 0
    max_attempts = int(timeout / check_interval)
    
    if log_callback:
        log_callback("⏳ Waiting for Docker to start...", 'info')
    
    while time.time() - start_time < timeout:
        attempts += 1
        
        if is_docker_running():
            elapsed = time.time() - start_time
            if log_callback:
                log_callback(f"✅ Docker is now running! (took {elapsed:.1f}s)", 'success')
            return True
        
        # Log progress every 5 seconds
        elapsed = time.time() - start_time
        if log_callback and elapsed - last_log_time >= 5:
            remaining = int(timeout - elapsed)
            progress = int((attempts / max_attempts) * 100)
            log_callback(f"   Still waiting... ({remaining}s remaining, {progress}% elapsed)", 'info')
            last_log_time = elapsed
        
        time.sleep(check_interval)
    
    if log_callback:
        log_callback("❌ Timeout waiting for Docker to start", 'error')
        log_callback("   Please check Docker Desktop manually and ensure it's running", 'error')
    
    return False
    
    if log_callback:
        log_callback("⏳ Waiting for Docker to start...", 'info')
    
    while time.time() - start_time < timeout:
        if is_docker_running():
            if log_callback:
                log_callback("✅ Docker is now running!", 'success')
            return True
        
        # Log progress every 5 seconds
        elapsed = time.time() - start_time
        if log_callback and elapsed - last_log_time >= 5:
            remaining = int(timeout - elapsed)
            log_callback(f"   Still waiting... ({remaining}s remaining)", 'info')
            last_log_time = elapsed
        
        time.sleep(2)
    
    if log_callback:
        log_callback("❌ Timeout waiting for Docker to start", 'error')
    return False


def ensure_docker_running(log_callback=None, auto_start=True, wait=True):
    """
    Ensure Docker is running, optionally start it if not
    
    Args:
        log_callback: Optional callback for logging (message, tag)
        auto_start: If True, attempt to start Docker Desktop
        wait: If True, wait for Docker to become available
    
    Returns:
        tuple: (is_running: bool, message: str)
    """
    # Check if Docker is already running
    if is_docker_running():
        if log_callback:
            log_callback("✅ Docker is already running", 'success')
        return True, "Docker is running"
    
    # Docker is not running
    if log_callback:
        log_callback("⚠️ Docker is not running", 'warning')
    
    if not auto_start:
        return False, "Docker is not running. Please start Docker Desktop manually."
    
    # Try to start Docker Desktop
    if log_callback:
        log_callback("🚀 Attempting to start Docker Desktop...", 'info')
    
    success, message = start_docker_desktop()
    
    if not success:
        if log_callback:
            log_callback(f"❌ {message}", 'error')
        return False, message
    
    if log_callback:
        log_callback(f"📢 {message}", 'info')
    
    # Wait for Docker to become available
    if wait:
        docker_ready = wait_for_docker(timeout=90, log_callback=log_callback)
        if docker_ready:
            return True, "Docker is now running"
        else:
            return False, "Timeout waiting for Docker to start. Please check Docker Desktop manually."
    
    return True, message


def get_docker_info():
    """
    Get Docker system information
    
    Returns:
        dict: Docker info or None if not available
    """
    try:
        result = subprocess.run(
            ['docker', 'info', '--format', '{{json .}}'],
            capture_output=True,
            timeout=5,
            text=True
        )
        
        if result.returncode == 0:
            import json
            return json.loads(result.stdout)
        
        return None
    except Exception:
        return None


def check_docker_compose():
    """
    Check if docker-compose is available
    
    Returns:
        tuple: (available: bool, version: str or None)
    """
    try:
        result = subprocess.run(
            ['docker-compose', '--version'],
            capture_output=True,
            timeout=5,
            text=True
        )
        
        if result.returncode == 0:
            version = result.stdout.strip()
            return True, version
        
        return False, None
    except (FileNotFoundError, Exception):
        return False, None


# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_docker_utils():
    """Test all Docker utility functions"""
    print("=" * 70)
    print("TESTING DOCKER UTILITIES")
    print("=" * 70)
    
    # Test 1: Check if Docker is running
    print("\n1. Checking if Docker is running...")
    running = is_docker_running()
    print(f"   Result: {'✅ Running' if running else '❌ Not running'}")
    
    # Test 2: Find Docker Desktop path
    print("\n2. Finding Docker Desktop path...")
    docker_path = find_docker_desktop_path()
    if docker_path:
        print(f"   Found: {docker_path}")
    else:
        print(f"   Not found (System: {platform.system()})")
    
    # Test 3: Check docker-compose
    print("\n3. Checking docker-compose...")
    compose_available, compose_version = check_docker_compose()
    if compose_available:
        print(f"   ✅ {compose_version}")
    else:
        print("   ❌ docker-compose not available")
    
    # Test 4: Get Docker info (if running)
    if running:
        print("\n4. Getting Docker info...")
        info = get_docker_info()
        if info:
            print(f"   Server Version: {info.get('ServerVersion', 'N/A')}")
            print(f"   OS/Arch: {info.get('OperatingSystem', 'N/A')} / {info.get('Architecture', 'N/A')}")
            print(f"   Containers: {info.get('Containers', 0)} (Running: {info.get('ContainersRunning', 0)})")
        else:
            print("   Failed to get Docker info")
    
    print("\n" + "=" * 70)
    print("✅ All tests completed!")
    print("=" * 70)


if __name__ == '__main__':
    test_docker_utils()
