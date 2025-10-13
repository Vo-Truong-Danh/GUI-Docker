"""
Docker Utilities - Auto-start Docker Desktop if not running
Supports Windows, macOS, and Linux
Version: 5.2.0 - Enhanced Error Handling & Diagnostics
"""
import subprocess
import platform
import time
import os
import socket
from pathlib import Path
from typing import Tuple, Optional, Callable, Dict, Any


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
        except (ImportError, OSError, WindowsError) as e:
            # Registry access failed or key not found
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
    Get Docker system information with enhanced error handling
    
    Returns:
        dict: Docker info or None if not available
    """
    try:
        result = subprocess.run(
            ['docker', 'info', '--format', '{{json .}}'],
            capture_output=True,
            timeout=10,  # Increased timeout
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
        
        if result.returncode == 0:
            import json
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError as e:
                print(f"⚠️ Failed to parse Docker info JSON: {e}")
                return None
        
        return None
    except subprocess.TimeoutExpired:
        print("⚠️ Timeout getting Docker info")
        return None
    except FileNotFoundError:
        print("⚠️ Docker command not found")
        return None
    except Exception as e:
        print(f"⚠️ Unexpected error getting Docker info: {e}")
        return None


def check_docker_compose():
    """
    Check if docker-compose is available with fallback to 'docker compose'
    
    Returns:
        tuple: (available: bool, version: str or None, command: str or None)
    """
    # Try docker-compose (standalone)
    try:
        result = subprocess.run(
            ['docker-compose', '--version'],
            capture_output=True,
            timeout=5,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
        
        if result.returncode == 0:
            version = result.stdout.strip()
            return True, version, 'docker-compose'
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # Try docker compose (plugin)
    try:
        result = subprocess.run(
            ['docker', 'compose', 'version'],
            capture_output=True,
            timeout=5,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
        
        if result.returncode == 0:
            version = result.stdout.strip()
            return True, version, 'docker compose'
    except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.CalledProcessError):
        pass
    
    return False, None, None


# ============================================================================
# ENHANCED FEATURES - V5.2.0
# ============================================================================

def get_docker_diagnostics() -> Dict[str, Any]:
    """
    Get comprehensive Docker diagnostics information
    
    Returns:
        dict: Detailed Docker system information
    """
    diagnostics = {
        'docker_running': False,
        'docker_version': None,
        'docker_compose': {
            'available': False,
            'version': None,
            'command': None
        },
        'docker_desktop_path': None,
        'containers': {
            'total': 0,
            'running': 0,
            'stopped': 0
        },
        'images': 0,
        'disk_usage': None,
        'system': platform.system(),
        'errors': []
    }
    
    # Check if Docker is running
    diagnostics['docker_running'] = is_docker_running()
    
    # Get Docker Desktop path
    diagnostics['docker_desktop_path'] = find_docker_desktop_path()
    
    # Get docker-compose info
    compose_available, compose_version, compose_cmd = check_docker_compose()
    diagnostics['docker_compose'] = {
        'available': compose_available,
        'version': compose_version,
        'command': compose_cmd
    }
    
    if not diagnostics['docker_running']:
        diagnostics['errors'].append('Docker daemon is not running')
        return diagnostics
    
    # Get Docker version
    try:
        result = subprocess.run(
            ['docker', '--version'],
            capture_output=True,
            timeout=5,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
        if result.returncode == 0:
            diagnostics['docker_version'] = result.stdout.strip()
    except Exception as e:
        diagnostics['errors'].append(f'Failed to get Docker version: {e}')
    
    # Get container stats
    try:
        result = subprocess.run(
            ['docker', 'ps', '-a', '--format', '{{.State}}'],
            capture_output=True,
            timeout=10,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
        if result.returncode == 0:
            states = result.stdout.strip().split('\n')
            diagnostics['containers']['total'] = len(states)
            diagnostics['containers']['running'] = sum(1 for s in states if s == 'running')
            diagnostics['containers']['stopped'] = diagnostics['containers']['total'] - diagnostics['containers']['running']
    except Exception as e:
        diagnostics['errors'].append(f'Failed to get container stats: {e}')
    
    # Get image count
    try:
        result = subprocess.run(
            ['docker', 'images', '-q'],
            capture_output=True,
            timeout=10,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
        if result.returncode == 0:
            diagnostics['images'] = len([line for line in result.stdout.strip().split('\n') if line])
    except Exception as e:
        diagnostics['errors'].append(f'Failed to get image count: {e}')
    
    return diagnostics


def check_docker_port_connectivity(host: str = 'localhost', port: int = 2375, timeout: int = 3) -> Tuple[bool, str]:
    """
    Check if Docker daemon port is accessible
    
    Args:
        host: Docker host
        port: Docker port (default 2375 for HTTP, 2376 for HTTPS)
        timeout: Connection timeout in seconds
    
    Returns:
        tuple: (is_accessible: bool, message: str)
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            return True, f"Port {port} is accessible"
        else:
            return False, f"Port {port} is not accessible (error code: {result})"
    
    except socket.timeout:
        return False, f"Connection timeout after {timeout}s"
    except socket.gaierror as e:
        return False, f"Host resolution failed: {e}"
    except Exception as e:
        return False, f"Connection check failed: {e}"


def restart_docker_desktop(log_callback: Optional[Callable] = None) -> Tuple[bool, str]:
    """
    Restart Docker Desktop (stop then start)
    
    Args:
        log_callback: Optional callback for progress updates
    
    Returns:
        tuple: (success: bool, message: str)
    """
    system = platform.system()
    
    if log_callback:
        log_callback('🔄 Restarting Docker Desktop...', 'info')
    
    # Stop Docker
    if system == 'Windows':
        try:
            # Kill Docker Desktop process
            subprocess.run(
                ['taskkill', '/F', '/IM', 'Docker Desktop.exe'],
                capture_output=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            if log_callback:
                log_callback('   Stopped Docker Desktop', 'info')
            time.sleep(3)
        except Exception as e:
            if log_callback:
                log_callback(f'   ⚠️ Error stopping Docker: {e}', 'warning')
    
    elif system == 'Darwin':  # macOS
        try:
            subprocess.run(
                ['osascript', '-e', 'quit app "Docker"'],
                capture_output=True,
                timeout=10
            )
            if log_callback:
                log_callback('   Stopped Docker Desktop', 'info')
            time.sleep(3)
        except Exception as e:
            if log_callback:
                log_callback(f'   ⚠️ Error stopping Docker: {e}', 'warning')
    
    elif system == 'Linux':
        try:
            subprocess.run(
                ['sudo', 'systemctl', 'restart', 'docker'],
                capture_output=True,
                timeout=10
            )
            if log_callback:
                log_callback('   Restarted Docker service', 'info')
            time.sleep(3)
        except Exception as e:
            return False, f"Failed to restart Docker service: {e}"
    
    # Start Docker
    success, message = start_docker_desktop()
    
    if success:
        # Wait for Docker to be ready
        if wait_for_docker(timeout=90, log_callback=log_callback):
            return True, "Docker Desktop restarted successfully"
        else:
            return False, "Docker restarted but failed to become ready"
    
    return success, message


def get_docker_resource_usage() -> Dict[str, Any]:
    """
    Get Docker resource usage statistics
    
    Returns:
        dict: Resource usage information (CPU, memory, disk)
    """
    usage = {
        'available': False,
        'containers': [],
        'total_cpu': 0.0,
        'total_memory': 0,
        'errors': []
    }
    
    try:
        result = subprocess.run(
            ['docker', 'stats', '--no-stream', '--format', 
             '{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}'],
            capture_output=True,
            timeout=10,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
        
        if result.returncode == 0:
            usage['available'] = True
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split('\t')
                if len(parts) >= 3:
                    name = parts[0]
                    cpu = parts[1].replace('%', '')
                    mem = parts[2]
                    
                    container_info = {
                        'name': name,
                        'cpu': cpu,
                        'memory': mem
                    }
                    usage['containers'].append(container_info)
                    
                    # Try to sum CPU (if numeric)
                    try:
                        usage['total_cpu'] += float(cpu)
                    except ValueError:
                        pass
    
    except subprocess.TimeoutExpired:
        usage['errors'].append('Timeout getting resource usage')
    except Exception as e:
        usage['errors'].append(f'Failed to get resource usage: {e}')
    
    return usage


def validate_docker_installation() -> Tuple[bool, list]:
    """
    Comprehensive validation of Docker installation
    
    Returns:
        tuple: (is_valid: bool, issues: list)
    """
    issues = []
    
    # Check 1: Docker command exists
    try:
        subprocess.run(
            ['docker', '--version'],
            capture_output=True,
            timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
    except FileNotFoundError:
        issues.append('Docker command not found in PATH')
    except Exception as e:
        issues.append(f'Error checking Docker command: {e}')
    
    # Check 2: Docker Desktop installed (Windows/macOS)
    system = platform.system()
    if system in ['Windows', 'Darwin']:
        docker_path = find_docker_desktop_path()
        if not docker_path:
            issues.append(f'Docker Desktop not found on {system}')
    
    # Check 3: Docker daemon running
    if not is_docker_running():
        issues.append('Docker daemon is not running')
    
    # Check 4: Docker compose available
    compose_available, _, _ = check_docker_compose()
    if not compose_available:
        issues.append('docker-compose not available')
    
    is_valid = len(issues) == 0
    return is_valid, issues


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
    compose_available, compose_version, compose_cmd = check_docker_compose()
    if compose_available:
        print(f"   ✅ {compose_version}")
        print(f"   Command: {compose_cmd}")
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
    
    # Test 5: Get diagnostics
    print("\n5. Getting Docker diagnostics...")
    diagnostics = get_docker_diagnostics()
    print(f"   Docker Running: {diagnostics['docker_running']}")
    print(f"   Version: {diagnostics['docker_version']}")
    print(f"   Containers: {diagnostics['containers']}")
    print(f"   Images: {diagnostics['images']}")
    if diagnostics['errors']:
        print(f"   Errors: {diagnostics['errors']}")
    
    # Test 6: Validate installation
    print("\n6. Validating Docker installation...")
    is_valid, issues = validate_docker_installation()
    if is_valid:
        print("   ✅ Docker installation is valid")
    else:
        print("   ❌ Issues found:")
        for issue in issues:
            print(f"      - {issue}")
    
    print("\n" + "=" * 70)
    print("✅ All tests completed!")
    print("=" * 70)


if __name__ == '__main__':
    test_docker_utils()
