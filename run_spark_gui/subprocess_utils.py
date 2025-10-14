"""
Subprocess Utilities - Hide console windows on Windows
"""
import subprocess
import sys


def get_subprocess_params():
    """
    Get subprocess parameters to hide console window on Windows.
    
    Returns:
        dict: Parameters to pass to subprocess.Popen or subprocess.run
    """
    params = {}
    
    if sys.platform == 'win32':
        # Hide console window on Windows
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        
        params['startupinfo'] = startupinfo
        params['creationflags'] = subprocess.CREATE_NO_WINDOW
    
    return params


def run_hidden(*args, **kwargs):
    """
    Run subprocess.run() with hidden console window on Windows.
    
    Usage:
        result = run_hidden(['docker', 'ps'], capture_output=True, text=True)
    """
    params = get_subprocess_params()
    kwargs.update(params)
    return subprocess.run(*args, **kwargs)


def popen_hidden(*args, **kwargs):
    """
    Run subprocess.Popen() with hidden console window on Windows.
    
    Usage:
        process = popen_hidden(['docker', 'exec', ...], stdout=subprocess.PIPE)
    """
    params = get_subprocess_params()
    kwargs.update(params)
    return subprocess.Popen(*args, **kwargs)


# Convenience wrapper
def run_command(cmd, capture_output=True, text=True, timeout=None, check=False, **kwargs):
    """
    Run command with hidden console window (convenience wrapper).
    
    Args:
        cmd: Command list or string
        capture_output: Capture stdout/stderr (default: True)
        text: Text mode (default: True)
        timeout: Timeout in seconds (default: None)
        check: Raise exception on non-zero exit (default: False)
        **kwargs: Additional parameters for subprocess.run
    
    Returns:
        CompletedProcess instance
    
    Example:
        result = run_command(['docker', 'ps'], timeout=10)
        if result.returncode == 0:
            print(result.stdout)
    """
    return run_hidden(
        cmd,
        capture_output=capture_output,
        text=text,
        timeout=timeout,
        check=check,
        **kwargs
    )


# Backward compatibility aliases
def create_hidden_process(*args, **kwargs):
    """Alias for popen_hidden"""
    return popen_hidden(*args, **kwargs)
