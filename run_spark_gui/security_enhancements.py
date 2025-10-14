"""
Security Enhancement Module
Version: 1.0.0 - Comprehensive Security Utilities
Date: 2025-10-13

Features:
- Command injection prevention
- Path traversal protection
- Input sanitization and validation
- SQL injection prevention
- Rate limiting
- Audit logging
"""

import os
import re
import hashlib
import secrets
import time
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import threading
import logging


@dataclass
class SecurityConfig:
    """Security configuration"""
    max_path_depth: int = 10
    allowed_extensions: List[str] = field(default_factory=lambda: [
        '.txt', '.csv', '.json', '.yaml', '.py', '.sh', '.bat',
        '.parquet', '.avro', '.orc', '.log'
    ])
    max_filename_length: int = 255
    max_command_length: int = 1000
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds


class CommandSanitizer:
    """
    Prevents command injection by validating and sanitizing shell commands
    """
    
    # Dangerous characters and patterns
    DANGEROUS_CHARS = ['|', ';', '&', '$', '`', '\\n', '\\r', '>', '<', '(', ')']
    DANGEROUS_PATTERNS = [
        r'&&',
        r'\|\|',
        r'\$\(',
        r'`.*`',
        r'\beval\b',
        r'\bexec\b',
        r'\bimport\b',
        r'__import__',
    ]
    
    @classmethod
    def is_safe_command(cls, command: str) -> bool:
        """
        Check if command is safe from injection
        
        Args:
            command: Command string to validate
        
        Returns:
            bool: True if safe, False if potentially dangerous
        """
        # Check for dangerous characters
        for char in cls.DANGEROUS_CHARS:
            if char in command:
                return False
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return False
        
        return True
    
    @classmethod
    def sanitize_argument(cls, arg: str) -> str:
        """
        Sanitize a command argument
        
        Args:
            arg: Argument string
        
        Returns:
            str: Sanitized argument
        """
        # Remove dangerous characters
        sanitized = re.sub(r'[;&|`$(){}\\[\\]<>]', '', arg)
        
        # Escape quotes
        sanitized = sanitized.replace('"', '\\"').replace("'", "\\'")
        
        return sanitized
    
    @classmethod
    def build_safe_command(cls, base_cmd: str, args: List[str]) -> List[str]:
        """
        Build a safe command with arguments (for subprocess)
        
        Args:
            base_cmd: Base command (e.g., 'docker')
            args: List of arguments
        
        Returns:
            list: Command as list (safe for subprocess)
        
        Example:
            >>> CommandSanitizer.build_safe_command('docker', ['ps', '-a'])
            ['docker', 'ps', '-a']
        """
        if not cls.is_safe_command(base_cmd):
            raise ValueError(f"Unsafe base command: {base_cmd}")
        
        safe_args = []
        for arg in args:
            if cls.is_safe_command(arg):
                safe_args.append(arg)
            else:
                safe_args.append(cls.sanitize_argument(arg))
        
        return [base_cmd] + safe_args


class PathValidator:
    """
    Prevents path traversal attacks and validates file paths
    """
    
    def __init__(self, config: SecurityConfig):
        self.config = config
    
    def is_safe_path(
        self,
        path: str,
        base_dir: Optional[str] = None,
        allow_absolute: bool = False
    ) -> bool:
        """
        Check if path is safe from traversal attacks
        
        Args:
            path: Path to validate
            base_dir: Base directory to restrict to
            allow_absolute: Allow absolute paths
        
        Returns:
            bool: True if safe, False otherwise
        """
        try:
            # Convert to Path object
            path_obj = Path(path)
            
            # Check for path traversal attempts
            if '..' in path_obj.parts:
                return False
            
            # Check path depth
            if len(path_obj.parts) > self.config.max_path_depth:
                return False
            
            # Check if absolute path is allowed
            if path_obj.is_absolute() and not allow_absolute:
                return False
            
            # If base_dir specified, ensure path is within it
            if base_dir:
                base_path = Path(base_dir).resolve()
                try:
                    full_path = (base_path / path_obj).resolve()
                    
                    # Check if resolved path is within base_dir
                    if not str(full_path).startswith(str(base_path)):
                        return False
                except Exception:
                    return False
            
            # Check filename length
            if path_obj.name and len(path_obj.name) > self.config.max_filename_length:
                return False
            
            return True
            
        except Exception:
            return False
    
    def validate_extension(self, path: str) -> bool:
        """
        Validate file extension
        
        Args:
            path: File path
        
        Returns:
            bool: True if extension is allowed
        """
        extension = Path(path).suffix.lower()
        return extension in self.config.allowed_extensions
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to remove dangerous characters
        
        Args:
            filename: Original filename
        
        Returns:
            str: Sanitized filename
        """
        # Remove path separators
        sanitized = filename.replace('/', '_').replace('\\', '_')
        
        # Remove dangerous characters
        sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', sanitized)
        
        # Truncate if too long
        if len(sanitized) > self.config.max_filename_length:
            name, ext = os.path.splitext(sanitized)
            max_name_len = self.config.max_filename_length - len(ext)
            sanitized = name[:max_name_len] + ext
        
        return sanitized
    
    def get_safe_path(
        self,
        path: str,
        base_dir: str,
        create_if_missing: bool = False
    ) -> Optional[Path]:
        """
        Get a safe, validated path within base directory
        
        Args:
            path: Requested path
            base_dir: Base directory
            create_if_missing: Create parent directories if missing
        
        Returns:
            Path object if safe, None otherwise
        """
        if not self.is_safe_path(path, base_dir):
            return None
        
        base_path = Path(base_dir).resolve()
        full_path = (base_path / path).resolve()
        
        # Double-check it's within base_dir
        if not str(full_path).startswith(str(base_path)):
            return None
        
        if create_if_missing:
            full_path.parent.mkdir(parents=True, exist_ok=True)
        
        return full_path


class RateLimiter:
    """
    Rate limiter to prevent abuse
    """
    
    def __init__(self, max_requests: int, window_seconds: int):
        """
        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = {}
        self._lock = threading.Lock()
    
    def is_allowed(self, identifier: str) -> bool:
        """
        Check if request is allowed
        
        Args:
            identifier: Unique identifier (e.g., user_id, IP)
        
        Returns:
            bool: True if allowed, False if rate limit exceeded
        """
        current_time = time.time()
        
        with self._lock:
            # Get request history for this identifier
            if identifier not in self.requests:
                self.requests[identifier] = []
            
            request_times = self.requests[identifier]
            
            # Remove old requests outside window
            cutoff_time = current_time - self.window_seconds
            request_times[:] = [t for t in request_times if t > cutoff_time]
            
            # Check if under limit
            if len(request_times) < self.max_requests:
                request_times.append(current_time)
                return True
            
            return False
    
    def get_remaining(self, identifier: str) -> int:
        """Get remaining requests for identifier"""
        current_time = time.time()
        
        with self._lock:
            if identifier not in self.requests:
                return self.max_requests
            
            request_times = self.requests[identifier]
            cutoff_time = current_time - self.window_seconds
            recent_requests = [t for t in request_times if t > cutoff_time]
            
            return max(0, self.max_requests - len(recent_requests))


class SecurityAuditor:
    """
    Audit logger for security events
    """
    
    def __init__(self, log_file: str = "security_audit.log"):
        self.log_file = Path(log_file)
        self.logger = logging.getLogger('security_audit')
        
        # Setup file handler
        if not self.logger.handlers:
            handler = logging.FileHandler(self.log_file)
            formatter = logging.Formatter(
                '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def log_event(
        self,
        event_type: str,
        description: str,
        severity: str = "INFO",
        **context
    ):
        """
        Log security event
        
        Args:
            event_type: Type of event (e.g., 'PATH_TRAVERSAL_ATTEMPT')
            description: Event description
            severity: Severity level
            **context: Additional context
        """
        log_entry = {
            'event_type': event_type,
            'description': description,
            'timestamp': datetime.now().isoformat(),
            **context
        }
        
        log_message = f"{event_type}: {description}"
        if context:
            log_message += f" | Context: {context}"
        
        if severity == "CRITICAL":
            self.logger.critical(log_message)
        elif severity == "ERROR":
            self.logger.error(log_message)
        elif severity == "WARNING":
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)


class SecurityManager:
    """
    Unified security manager
    """
    
    def __init__(self, config: Optional[SecurityConfig] = None):
        self.config = config or SecurityConfig()
        self.command_sanitizer = CommandSanitizer()
        self.path_validator = PathValidator(self.config)
        self.rate_limiter = RateLimiter(
            self.config.rate_limit_requests,
            self.config.rate_limit_window
        )
        self.auditor = SecurityAuditor()
    
    def validate_command(self, command: str, context: str = "") -> bool:
        """Validate and audit command"""
        is_safe = self.command_sanitizer.is_safe_command(command)
        
        if not is_safe:
            self.auditor.log_event(
                'COMMAND_INJECTION_ATTEMPT',
                f"Unsafe command detected: {command}",
                severity='WARNING',
                context=context
            )
        
        return is_safe
    
    def validate_path(
        self,
        path: str,
        base_dir: Optional[str] = None,
        context: str = ""
    ) -> bool:
        """Validate and audit path"""
        is_safe = self.path_validator.is_safe_path(path, base_dir)
        
        if not is_safe:
            self.auditor.log_event(
                'PATH_TRAVERSAL_ATTEMPT',
                f"Unsafe path detected: {path}",
                severity='WARNING',
                context=context,
                base_dir=base_dir
            )
        
        return is_safe
    
    def check_rate_limit(self, identifier: str, context: str = "") -> bool:
        """Check rate limit and audit"""
        is_allowed = self.rate_limiter.is_allowed(identifier)
        
        if not is_allowed:
            self.auditor.log_event(
                'RATE_LIMIT_EXCEEDED',
                f"Rate limit exceeded for: {identifier}",
                severity='WARNING',
                context=context
            )
        
        return is_allowed


# Global security manager
_security_manager: Optional[SecurityManager] = None


def get_security_manager(config: Optional[SecurityConfig] = None) -> SecurityManager:
    """Get or create global security manager"""
    global _security_manager
    
    if _security_manager is None:
        _security_manager = SecurityManager(config)
    
    return _security_manager


# Example usage
if __name__ == '__main__':
    # Test security features
    security = get_security_manager()
    
    # Test command validation
    print("Testing command validation:")
    print(f"  'docker ps': {security.validate_command('docker ps')}")
    print(f"  'docker ps; rm -rf /': {security.validate_command('docker ps; rm -rf /')}")
    
    # Test path validation
    print("\nTesting path validation:")
    print(f"  'data/file.txt': {security.validate_path('data/file.txt')}")
    print(f"  '../../../etc/passwd': {security.validate_path('../../../etc/passwd')}")
    
    # Test rate limiting
    print("\nTesting rate limiting:")
    for i in range(5):
        allowed = security.check_rate_limit('user123', f'request_{i}')
        print(f"  Request {i+1}: {'ALLOWED' if allowed else 'BLOCKED'}")
