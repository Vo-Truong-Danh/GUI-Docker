"""
Input Sanitizer & Validator Module
Version: 1.0.0

Features:
- Sanitize user inputs
- Prevent injection attacks
- Validate file paths, URLs, container names
- Type conversion with validation
"""

import re
import os
from pathlib import Path
from typing import Any, Optional, Union, List
from urllib.parse import urlparse, quote


class InputSanitizer:
    """Sanitize and validate user inputs"""
    
    # Dangerous characters that could cause command injection
    DANGEROUS_CHARS = ['&', '|', ';', '$', '`', '\n', '\r', '(', ')', '<', '>', '"', "'", '\\']
    
    # Safe filename characters
    SAFE_FILENAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\.]+$')
    
    # Docker container name pattern
    CONTAINER_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,254}$')
    
    @classmethod
    def sanitize_string(cls, value: str, allow_spaces: bool = True, max_length: int = 1000) -> str:
        """
        Sanitize a general string input
        
        Args:
            value: Input string
            allow_spaces: Whether to allow spaces
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            value = str(value)
        
        # Trim whitespace
        value = value.strip()
        
        # Enforce max length
        if len(value) > max_length:
            value = value[:max_length]
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Remove dangerous characters for shell execution
        for char in cls.DANGEROUS_CHARS:
            if char != ' ' or not allow_spaces:
                value = value.replace(char, '')
        
        return value
    
    @classmethod
    def sanitize_filename(cls, filename: str, allow_extensions: List[str] = None) -> Optional[str]:
        """
        Sanitize filename to prevent directory traversal
        
        Args:
            filename: Input filename
            allow_extensions: List of allowed extensions (e.g., ['.py', '.txt'])
            
        Returns:
            Sanitized filename or None if invalid
        """
        if not filename:
            return None
        
        # Get basename to prevent directory traversal
        filename = os.path.basename(filename)
        
        # Remove dangerous characters
        filename = filename.strip()
        
        # Check if contains only safe characters
        if not cls.SAFE_FILENAME_PATTERN.match(filename):
            # Replace unsafe characters
            filename = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)
        
        # Check extension if specified
        if allow_extensions:
            ext = Path(filename).suffix.lower()
            if ext not in allow_extensions:
                return None
        
        # Prevent empty filename
        if not filename or filename == '.' or filename == '..':
            return None
        
        return filename
    
    @classmethod
    def sanitize_path(cls, path: str, base_dir: Optional[str] = None) -> Optional[str]:
        """
        Sanitize file path to prevent directory traversal
        
        Args:
            path: Input path
            base_dir: Base directory to restrict access (optional)
            
        Returns:
            Sanitized absolute path or None if invalid
        """
        if not path:
            return None
        
        try:
            # Convert to Path object
            path_obj = Path(path)
            
            # Resolve to absolute path (follows symlinks)
            abs_path = path_obj.resolve()
            
            # If base_dir specified, ensure path is within base_dir
            if base_dir:
                base_path = Path(base_dir).resolve()
                try:
                    abs_path.relative_to(base_path)
                except ValueError:
                    # Path is outside base_dir
                    return None
            
            return str(abs_path)
        
        except (OSError, ValueError, RuntimeError) as e:
            # OSError: File system errors
            # ValueError: Path manipulation errors
            # RuntimeError: Symlink resolution errors
            return None
    
    @classmethod
    def sanitize_url(cls, url: str, allowed_schemes: List[str] = None) -> Optional[str]:
        """
        Sanitize and validate URL
        
        Args:
            url: Input URL
            allowed_schemes: List of allowed schemes (e.g., ['http', 'https'])
            
        Returns:
            Sanitized URL or None if invalid
        """
        if not url:
            return None
        
        try:
            parsed = urlparse(url)
            
            # Check scheme
            if allowed_schemes and parsed.scheme not in allowed_schemes:
                return None
            
            # Reconstruct URL (this sanitizes it)
            sanitized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            
            if parsed.query:
                sanitized += f"?{parsed.query}"
            
            return sanitized
        
        except (ValueError, AttributeError) as e:
            # ValueError: Invalid URL format
            # AttributeError: urlparse issues
            return None
    
    @classmethod
    def sanitize_container_name(cls, name: str) -> Optional[str]:
        """
        Sanitize Docker container name
        
        Args:
            name: Container name
            
        Returns:
            Sanitized name or None if invalid
        """
        if not name:
            return None
        
        name = name.strip()
        
        # Check pattern
        if not cls.CONTAINER_NAME_PATTERN.match(name):
            return None
        
        return name
    
    @classmethod
    def sanitize_port(cls, port: Union[str, int]) -> Optional[int]:
        """
        Sanitize and validate port number
        
        Args:
            port: Port number (string or int)
            
        Returns:
            Valid port number or None if invalid
        """
        try:
            port_num = int(port)
            
            # Valid port range: 1-65535
            if 1 <= port_num <= 65535:
                return port_num
            
            return None
        
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def sanitize_integer(
        cls,
        value: Union[str, int, float],
        min_value: Optional[int] = None,
        max_value: Optional[int] = None
    ) -> Optional[int]:
        """
        Sanitize and validate integer input
        
        Args:
            value: Input value
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            Valid integer or None if invalid
        """
        try:
            int_value = int(value)
            
            if min_value is not None and int_value < min_value:
                return None
            
            if max_value is not None and int_value > max_value:
                return None
            
            return int_value
        
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def sanitize_boolean(cls, value: Union[str, bool, int]) -> bool:
        """
        Convert various inputs to boolean
        
        Args:
            value: Input value
            
        Returns:
            Boolean value
        """
        if isinstance(value, bool):
            return value
        
        if isinstance(value, (int, float)):
            return value != 0
        
        if isinstance(value, str):
            value = value.lower().strip()
            return value in ['true', '1', 'yes', 'y', 'on', 'enabled']
        
        return False
    
    @classmethod
    def sanitize_list(
        cls,
        value: Union[str, list],
        separator: str = ',',
        sanitizer: Optional[callable] = None
    ) -> List[str]:
        """
        Sanitize list input
        
        Args:
            value: Input value (string or list)
            separator: Separator for string input
            sanitizer: Optional function to sanitize each item
            
        Returns:
            List of sanitized items
        """
        if isinstance(value, list):
            items = value
        elif isinstance(value, str):
            items = value.split(separator)
        else:
            return []
        
        # Strip whitespace and remove empty items
        items = [item.strip() for item in items if item.strip()]
        
        # Apply sanitizer if provided
        if sanitizer:
            items = [sanitizer(item) for item in items]
            items = [item for item in items if item is not None]
        
        return items


class InputValidator:
    """Additional input validation utilities"""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email format"""
        pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        return bool(pattern.match(email))
    
    @staticmethod
    def is_valid_ipv4(ip: str) -> bool:
        """Validate IPv4 address"""
        pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
        if not pattern.match(ip):
            return False
        
        parts = ip.split('.')
        return all(0 <= int(part) <= 255 for part in parts)
    
    @staticmethod
    def is_valid_hostname(hostname: str) -> bool:
        """Validate hostname"""
        if len(hostname) > 253:
            return False
        
        pattern = re.compile(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$')
        return bool(pattern.match(hostname))
    
    @staticmethod
    def is_safe_for_shell(value: str) -> bool:
        """Check if string is safe for shell execution"""
        dangerous = ['&', '|', ';', '$', '`', '\n', '\r', '(', ')', '<', '>', '"', "'"]
        return not any(char in value for char in dangerous)


if __name__ == "__main__":
    # Test input sanitizer
    print("Testing Input Sanitizer\n" + "=" * 50)
    
    # Test filename sanitization
    print("\n1. Filename Sanitization:")
    test_filenames = [
        "test.py",
        "../../../etc/passwd",
        "file; rm -rf /",
        "normal_file.txt",
        "bad<>file.py"
    ]
    for filename in test_filenames:
        sanitized = InputSanitizer.sanitize_filename(filename)
        print(f"  '{filename}' -> '{sanitized}'")
    
    # Test path sanitization
    print("\n2. Path Sanitization:")
    test_paths = [
        "../../etc/passwd",
        "/valid/path/file.txt",
        "relative/path.py"
    ]
    for path in test_paths:
        sanitized = InputSanitizer.sanitize_path(path)
        print(f"  '{path}' -> '{sanitized}'")
    
    # Test container name
    print("\n3. Container Name Sanitization:")
    test_containers = [
        "spark-master",
        "invalid name",
        "valid_container-1",
        "123invalid"
    ]
    for container in test_containers:
        sanitized = InputSanitizer.sanitize_container_name(container)
        print(f"  '{container}' -> '{sanitized}'")
    
    # Test port sanitization
    print("\n4. Port Sanitization:")
    test_ports = ["8080", "99999", "abc", 3000, -1]
    for port in test_ports:
        sanitized = InputSanitizer.sanitize_port(port)
        print(f"  '{port}' -> {sanitized}")
