"""
HDFS Utilities - Enhanced Error Handling for HDFS Operations
Version: 5.0.0
Features:
- Safe mode detection and handling
- Automatic retry with backoff
- Package installation (unzip, etc.)
- Proper error propagation
"""

import subprocess
import time
from typing import Tuple, Optional, Callable
from pathlib import Path


class HDFSError(Exception):
    """Base exception for HDFS operations"""
    pass


class HDFSSafeModeError(HDFSError):
    """HDFS is in safe mode"""
    pass


class HDFSPermissionError(HDFSError):
    """HDFS permission denied"""
    pass


class HDFSNotFoundException(HDFSError):
    """HDFS file or directory not found"""
    pass


def check_hdfs_safe_mode(container: str, log_callback: Optional[Callable] = None) -> Tuple[bool, str]:
    """
    Check if HDFS is in safe mode
    
    Args:
        container: HDFS container name (e.g., 'namenode')
        log_callback: Optional logging function
    
    Returns:
        Tuple of (is_safe_mode: bool, message: str)
    """
    try:
        result = subprocess.run(
            ['docker', 'exec', container, 'hdfs', 'dfsadmin', '-safemode', 'get'],
            capture_output=True,
            timeout=10,
            text=True
        )
        
        output = result.stdout.strip().lower()
        
        if 'safe mode is on' in output:
            if log_callback:
                log_callback('⚠️ HDFS is in SAFE MODE', 'warning')
            return True, "HDFS is in safe mode"
        elif 'safe mode is off' in output:
            if log_callback:
                log_callback('✅ HDFS safe mode is OFF', 'success')
            return False, "HDFS safe mode is off"
        else:
            return False, f"Unknown safe mode status: {output}"
    
    except subprocess.TimeoutExpired:
        return True, "Timeout checking safe mode (assuming safe mode)"
    except Exception as e:
        if log_callback:
            log_callback(f'⚠️ Could not check safe mode: {e}', 'warning')
        return True, f"Error checking safe mode: {e}"


def wait_for_hdfs_ready(
    container: str,
    max_wait: int = 60,
    log_callback: Optional[Callable] = None
) -> bool:
    """
    Wait for HDFS to exit safe mode
    
    Args:
        container: HDFS container name
        max_wait: Maximum seconds to wait
        log_callback: Optional logging function
    
    Returns:
        bool: True if HDFS is ready, False if timeout
    """
    if log_callback:
        log_callback(f'⏳ Waiting for HDFS to be ready (max {max_wait}s)...', 'info')
    
    start_time = time.time()
    check_interval = 2
    
    while time.time() - start_time < max_wait:
        is_safe, message = check_hdfs_safe_mode(container, log_callback=None)
        
        if not is_safe:
            elapsed = time.time() - start_time
            if log_callback:
                log_callback(f'✅ HDFS is ready (took {elapsed:.1f}s)', 'success')
            return True
        
        # Log progress every 10 seconds
        elapsed = time.time() - start_time
        if elapsed % 10 < check_interval:
            remaining = int(max_wait - elapsed)
            if log_callback:
                log_callback(f'   Still in safe mode... ({remaining}s remaining)', 'info')
        
        time.sleep(check_interval)
    
    if log_callback:
        log_callback(f'❌ Timeout waiting for HDFS (still in safe mode)', 'error')
    
    return False


def leave_safe_mode(container: str, log_callback: Optional[Callable] = None) -> bool:
    """
    Force HDFS to leave safe mode (use with caution!)
    
    Args:
        container: HDFS container name
        log_callback: Optional logging function
    
    Returns:
        bool: True if successful
    """
    if log_callback:
        log_callback('⚠️ Forcing HDFS to leave safe mode...', 'warning')
        log_callback('   (This should only be done in development!)', 'warning')
    
    try:
        result = subprocess.run(
            ['docker', 'exec', container, 'hdfs', 'dfsadmin', '-safemode', 'leave'],
            capture_output=True,
            timeout=10,
            text=True
        )
        
        if result.returncode == 0:
            if log_callback:
                log_callback('✅ Safe mode left successfully', 'success')
            
            # Wait a bit for HDFS to stabilize
            time.sleep(2)
            return True
        else:
            if log_callback:
                log_callback(f'❌ Failed to leave safe mode: {result.stderr}', 'error')
            return False
    
    except Exception as e:
        if log_callback:
            log_callback(f'❌ Error leaving safe mode: {e}', 'error')
        return False


def install_package_in_container(
    container: str,
    package: str,
    log_callback: Optional[Callable] = None
) -> bool:
    """
    Install package in container with better error handling
    
    Args:
        container: Container name
        package: Package name to install
        log_callback: Optional logging function
    
    Returns:
        bool: True if successful
    """
    if log_callback:
        log_callback(f'📦 Installing {package} in {container}...', 'info')
    
    # Try different package managers
    package_managers = [
        # Debian/Ubuntu
        ['apt-get', 'update', '&&', 'apt-get', 'install', '-y', package],
        # Alpine
        ['apk', 'add', package],
        # RedHat/CentOS
        ['yum', 'install', '-y', package],
    ]
    
    for pm_cmd in package_managers:
        try:
            # Build command
            cmd = ['docker', 'exec', container, 'sh', '-c', ' '.join(pm_cmd)]
            
            if log_callback:
                log_callback(f'   Trying: {" ".join(pm_cmd[:2])}...', 'info')
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=120,  # 2 minutes for package installation
                text=True
            )
            
            if result.returncode == 0:
                if log_callback:
                    log_callback(f'   ✅ {package} installed successfully', 'success')
                return True
            else:
                # Try next package manager
                continue
        
        except subprocess.TimeoutExpired:
            if log_callback:
                log_callback(f'   ⏱️ Installation timeout', 'warning')
            continue
        
        except Exception as e:
            if log_callback:
                log_callback(f'   ⚠️ Error: {e}', 'warning')
            continue
    
    # All attempts failed
    if log_callback:
        log_callback(f'❌ Could not install {package} (tried multiple package managers)', 'error')
        log_callback(f'💡 You may need to install {package} manually in the container', 'info')
    
    return False


def verify_hdfs_file(
    container: str,
    hdfs_path: str,
    log_callback: Optional[Callable] = None
) -> Tuple[bool, str]:
    """
    Verify file exists in HDFS with proper error handling
    
    Args:
        container: HDFS container name
        hdfs_path: Path to file in HDFS
        log_callback: Optional logging function
    
    Returns:
        Tuple of (exists: bool, message: str)
    """
    try:
        result = subprocess.run(
            ['docker', 'exec', container, 'hdfs', 'dfs', '-test', '-e', hdfs_path],
            capture_output=True,
            timeout=10,
            text=True
        )
        
        if result.returncode == 0:
            # File exists, get size
            size_result = subprocess.run(
                ['docker', 'exec', container, 'hdfs', 'dfs', '-du', '-h', hdfs_path],
                capture_output=True,
                timeout=10,
                text=True
            )
            
            size_info = size_result.stdout.strip() if size_result.returncode == 0 else "unknown size"
            
            if log_callback:
                log_callback(f'✅ File verified in HDFS: {hdfs_path}', 'success')
                log_callback(f'   Size: {size_info}', 'info')
            
            return True, f"File exists: {size_info}"
        
        else:
            if log_callback:
                log_callback(f'❌ File NOT found in HDFS: {hdfs_path}', 'error')
            
            return False, "File does not exist in HDFS"
    
    except subprocess.TimeoutExpired:
        return False, "Timeout verifying file"
    
    except Exception as e:
        return False, f"Error verifying file: {e}"


def handle_hdfs_error(error_output: str) -> HDFSError:
    """
    Parse HDFS error message and return appropriate exception
    
    Args:
        error_output: Error message from HDFS command
    
    Returns:
        HDFSError: Appropriate exception type
    """
    error_lower = error_output.lower()
    
    if 'safe mode' in error_lower:
        return HDFSSafeModeError(
            "HDFS is in safe mode. Wait for it to exit or use force leave safe mode."
        )
    
    elif 'permission denied' in error_lower or 'access denied' in error_lower:
        return HDFSPermissionError(
            f"Permission denied: {error_output}"
        )
    
    elif 'no such file' in error_lower or 'file does not exist' in error_lower:
        return HDFSNotFoundException(
            f"File or directory not found: {error_output}"
        )
    
    else:
        return HDFSError(f"HDFS error: {error_output}")


def upload_to_hdfs_with_retry(
    container: str,
    local_file: str,
    hdfs_path: str,
    max_retries: int = 3,
    log_callback: Optional[Callable] = None
) -> Tuple[bool, str]:
    """
    Upload file to HDFS with retry logic and safe mode handling
    
    Args:
        container: HDFS container name
        local_file: Path to local file (in container /tmp/)
        hdfs_path: Destination path in HDFS
        max_retries: Maximum retry attempts
        log_callback: Optional logging function
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    for attempt in range(max_retries):
        try:
            # Check safe mode before upload
            is_safe, safe_msg = check_hdfs_safe_mode(container, log_callback)
            
            if is_safe:
                if log_callback:
                    log_callback(f'⚠️ HDFS in safe mode (attempt {attempt+1}/{max_retries})', 'warning')
                
                # Try to wait for safe mode to end
                if wait_for_hdfs_ready(container, max_wait=30, log_callback=log_callback):
                    # Safe mode ended, continue with upload
                    pass
                else:
                    # Still in safe mode, offer to force leave
                    if attempt == max_retries - 1:  # Last attempt
                        if log_callback:
                            log_callback('❓ Would you like to force leave safe mode? (Development only)', 'warning')
                        # For now, just return error
                        return False, "HDFS stuck in safe mode. Manual intervention required."
                    else:
                        # Wait and retry
                        time.sleep(5)
                        continue
            
            # Perform upload
            if log_callback:
                log_callback(f'📤 Uploading to HDFS (attempt {attempt+1}/{max_retries})...', 'info')
            
            result = subprocess.run(
                ['docker', 'exec', container, 'hdfs', 'dfs', '-put', '-f', local_file, hdfs_path],
                capture_output=True,
                timeout=300,  # 5 minutes
                text=True
            )
            
            if result.returncode == 0:
                # Verify upload
                exists, verify_msg = verify_hdfs_file(container, hdfs_path, log_callback)
                
                if exists:
                    return True, "Upload successful and verified"
                else:
                    return False, f"Upload appeared successful but file not found: {verify_msg}"
            
            else:
                # Parse error
                error = result.stderr.strip()
                
                if 'safe mode' in error.lower() and attempt < max_retries - 1:
                    # Retry for safe mode
                    if log_callback:
                        log_callback(f'⚠️ Safe mode error, retrying...', 'warning')
                    time.sleep(5)
                    continue
                else:
                    # Other error or last attempt
                    hdfs_error = handle_hdfs_error(error)
                    return False, str(hdfs_error)
        
        except subprocess.TimeoutExpired:
            if log_callback:
                log_callback(f'⏱️ Upload timeout (attempt {attempt+1}/{max_retries})', 'warning')
            
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            else:
                return False, "Upload timeout after multiple retries"
        
        except Exception as e:
            if log_callback:
                log_callback(f'❌ Upload error: {e}', 'error')
            
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            else:
                return False, f"Upload failed: {e}"
    
    return False, "Upload failed after all retries"


# Example usage and tests
if __name__ == '__main__':
    print("=" * 80)
    print("HDFS UTILITIES TEST")
    print("=" * 80)
    
    def test_log(msg, tag):
        print(f"[{tag.upper()}] {msg}")
    
    container = 'namenode'
    
    # Test 1: Check safe mode
    print("\n1. Checking HDFS safe mode...")
    is_safe, msg = check_hdfs_safe_mode(container, test_log)
    print(f"   Result: {msg}")
    
    # Test 2: Verify a file (example)
    print("\n2. Verifying HDFS file...")
    exists, msg = verify_hdfs_file(container, '/input', test_log)
    print(f"   Result: {msg}")
    
    print("\n" + "=" * 80)
    print("✅ HDFS utilities test complete!")
    print("=" * 80)
