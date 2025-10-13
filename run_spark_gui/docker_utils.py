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
            timeout=5,
            text=True
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
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
    Start Docker Desktop application
    
    Returns:
        tuple: (success: bool, message: str)
    """
    system = platform.system()
    docker_path = find_docker_desktop_path()
    
    if not docker_path:
        return False, f"Docker Desktop not found on {system}. Please install Docker Desktop."
    
    try:
        if system == 'Windows':
            # Start Docker Desktop in background
            subprocess.Popen(
                [docker_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
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
                subprocess.run(['sudo', 'systemctl', 'start', 'docker'], check=True)
                return True, "Docker service is starting..."
            except subprocess.CalledProcessError:
                return False, "Failed to start Docker service. Please start it manually with: sudo systemctl start docker"
        
        return False, f"Unsupported platform: {system}"
    
    except Exception as e:
        return False, f"Failed to start Docker Desktop: {str(e)}"


def wait_for_docker(timeout=60, log_callback=None):
    """
    Wait for Docker daemon to become available
    
    Args:
        timeout: Maximum seconds to wait
        log_callback: Optional callback for progress updates (message, tag)
    
    Returns:
        bool: True if Docker is running, False if timeout
    """
    start_time = time.time()
    last_log_time = 0
    
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
