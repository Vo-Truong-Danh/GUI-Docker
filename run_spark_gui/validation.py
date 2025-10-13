"""
Comprehensive Input Validation Module
Version: 5.0.0
Features:
- Type validation
- Format validation (URLs, paths, container names)
- Range validation
- Custom validators
- Error reporting with suggestions
"""

import re
import os
from pathlib import Path
from typing import Any, List, Tuple, Optional, Callable
from urllib.parse import urlparse


class ValidationError(Exception):
    """Custom exception for validation errors"""
    
    def __init__(self, message: str, field: str = None, suggestion: str = None):
        self.message = message
        self.field = field
        self.suggestion = suggestion
        super().__init__(self.format_message())
    
    def format_message(self) -> str:
        msg = self.message
        if self.field:
            msg = f"{self.field}: {msg}"
        if self.suggestion:
            msg += f" | Suggestion: {self.suggestion}"
        return msg


class Validator:
    """Base validator class"""
    
    @staticmethod
    def is_non_empty_string(value: Any) -> Tuple[bool, Optional[str]]:
        """Validate non-empty string"""
        if not isinstance(value, str):
            return False, f"Expected string, got {type(value).__name__}"
        if not value or not value.strip():
            return False, "Value cannot be empty"
        return True, None
    
    @staticmethod
    def is_valid_url(value: str, schemes: List[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate URL format
        
        Args:
            value: URL to validate
            schemes: List of allowed schemes (e.g., ['http', 'https', 'spark', 'hdfs'])
        """
        if not value:
            return False, "URL cannot be empty"
        
        try:
            parsed = urlparse(value)
            
            # Check if scheme exists
            if not parsed.scheme:
                return False, "URL must include a scheme (e.g., http://, spark://)"
            
            # Check allowed schemes
            if schemes and parsed.scheme not in schemes:
                return False, f"URL scheme must be one of: {', '.join(schemes)}"
            
            # Check if netloc exists for network URLs
            if parsed.scheme in ['http', 'https', 'spark', 'hdfs', 'ftp']:
                if not parsed.netloc:
                    return False, f"URL must include a host (e.g., {parsed.scheme}://hostname)"
            
            return True, None
        
        except Exception as e:
            return False, f"Invalid URL format: {str(e)}"
    
    @staticmethod
    def is_valid_path(value: str, must_exist: bool = False, must_be_file: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Validate file system path
        
        Args:
            value: Path to validate
            must_exist: Path must exist on filesystem
            must_be_file: Path must be a file (not directory)
        """
        if not value:
            return False, "Path cannot be empty"
        
        try:
            path = Path(value)
            
            if must_exist:
                if not path.exists():
                    return False, f"Path does not exist: {value}"
                
                if must_be_file and not path.is_file():
                    return False, f"Path must be a file: {value}"
            
            return True, None
        
        except Exception as e:
            return False, f"Invalid path: {str(e)}"
    
    @staticmethod
    def is_valid_container_name(value: str) -> Tuple[bool, Optional[str]]:
        """
        Validate Docker container name
        
        Docker naming rules:
        - Must start with alphanumeric
        - Can contain: letters, digits, underscore, period, hyphen
        - Length: 1-255 characters
        """
        if not value:
            return False, "Container name cannot be empty"
        
        if len(value) > 255:
            return False, "Container name too long (max 255 characters)"
        
        # Docker container name pattern
        pattern = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_.-]*$')
        
        if not pattern.match(value):
            return False, "Container name must start with alphanumeric and contain only letters, digits, underscore, period, or hyphen"
        
        return True, None
    
    @staticmethod
    def is_valid_hdfs_path(value: str) -> Tuple[bool, Optional[str]]:
        """
        Validate HDFS path format
        
        Valid formats:
        - hdfs://namenode:8020/path
        - /path (relative to HDFS root)
        """
        if not value:
            return False, "HDFS path cannot be empty"
        
        if value.startswith('hdfs://'):
            # Full HDFS URL
            return Validator.is_valid_url(value, schemes=['hdfs'])
        elif value.startswith('/'):
            # Relative path (valid)
            return True, None
        else:
            return False, "HDFS path must start with 'hdfs://' or '/'"
    
    @staticmethod
    def is_valid_spark_master(value: str) -> Tuple[bool, Optional[str]]:
        """
        Validate Spark master URL
        
        Valid formats:
        - spark://host:port
        - local[*]
        - local[N]
        - yarn
        - mesos://host:port
        """
        if not value:
            return False, "Spark master URL cannot be empty"
        
        # Local mode
        if value.startswith('local'):
            pattern = re.compile(r'^local(\[\*\]|\[\d+\])?$')
            if pattern.match(value):
                return True, None
            return False, "Local mode must be 'local', 'local[*]', or 'local[N]' where N is a number"
        
        # YARN mode
        if value == 'yarn':
            return True, None
        
        # Spark standalone or Mesos
        if value.startswith('spark://') or value.startswith('mesos://'):
            return Validator.is_valid_url(value, schemes=['spark', 'mesos'])
        
        return False, "Spark master must be: 'spark://host:port', 'local[*]', 'yarn', or 'mesos://host:port'"
    
    @staticmethod
    def is_in_range(value: Any, min_val: Any = None, max_val: Any = None) -> Tuple[bool, Optional[str]]:
        """Validate value is within range"""
        try:
            if min_val is not None and value < min_val:
                return False, f"Value must be >= {min_val}"
            if max_val is not None and value > max_val:
                return False, f"Value must be <= {max_val}"
            return True, None
        except TypeError:
            return False, f"Cannot compare {type(value).__name__} with range limits"
    
    @staticmethod
    def is_valid_port(value: Any) -> Tuple[bool, Optional[str]]:
        """Validate network port number"""
        try:
            port = int(value)
            return Validator.is_in_range(port, 1, 65535)
        except (ValueError, TypeError):
            return False, "Port must be an integer between 1 and 65535"
    
    @staticmethod
    def is_valid_python_file(value: str) -> Tuple[bool, Optional[str]]:
        """Validate Python file path"""
        # Check path validity
        valid_path, error = Validator.is_valid_path(value, must_exist=True, must_be_file=True)
        if not valid_path:
            return False, error
        
        # Check extension
        if not value.endswith('.py'):
            return False, "File must have .py extension"
        
        return True, None


class ConfigValidator:
    """Validator for application configuration"""
    
    REQUIRED_FIELDS = {
        'container': Validator.is_valid_container_name,
        'master': Validator.is_valid_spark_master,
        'hdfs_host': lambda v: Validator.is_valid_url(v, schemes=['hdfs']),
        'hdfs_default_path': Validator.is_valid_hdfs_path,
    }
    
    OPTIONAL_FIELDS = {
        'hdfs_container': Validator.is_valid_container_name,
        'auto_extract_archives': lambda v: (isinstance(v, bool), "Must be boolean"),
        'delete_archive_after_extract': lambda v: (isinstance(v, bool), "Must be boolean"),
        'compose_file': lambda v: Validator.is_valid_path(v, must_exist=False),
    }
    
    @classmethod
    def validate_config(cls, config: dict) -> Tuple[bool, List[ValidationError]]:
        """
        Validate entire configuration dictionary
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        for field, validator in cls.REQUIRED_FIELDS.items():
            if field not in config:
                errors.append(ValidationError(
                    f"Required field missing",
                    field=field,
                    suggestion="Add this field to configuration"
                ))
                continue
            
            valid, error_msg = validator(config[field])
            if not valid:
                errors.append(ValidationError(
                    error_msg,
                    field=field,
                    suggestion=cls._get_suggestion(field)
                ))
        
        # Check optional fields (if present)
        for field, validator in cls.OPTIONAL_FIELDS.items():
            if field in config:
                valid, error_msg = validator(config[field])
                if not valid:
                    errors.append(ValidationError(
                        error_msg,
                        field=field,
                        suggestion=cls._get_suggestion(field)
                    ))
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _get_suggestion(field: str) -> str:
        """Get helpful suggestion for field"""
        suggestions = {
            'container': "Example: 'spark-worker' or 'spark-master'",
            'master': "Example: 'spark://spark-master:7077' or 'local[*]'",
            'hdfs_host': "Example: 'hdfs://namenode:8020'",
            'hdfs_default_path': "Example: '/user/spark/data'",
            'hdfs_container': "Example: 'namenode'",
            'compose_file': "Example: './docker-compose.yml'",
        }
        return suggestions.get(field, "Check documentation for valid format")
    
    @classmethod
    def fix_config(cls, config: dict) -> dict:
        """
        Attempt to fix common configuration issues
        
        Returns:
            Fixed configuration dictionary
        """
        fixed = config.copy()
        
        # Fix container name
        if 'container' in fixed:
            # Remove invalid characters
            fixed['container'] = re.sub(r'[^a-zA-Z0-9_.-]', '', fixed['container'])
            # Ensure starts with alphanumeric
            if fixed['container'] and not fixed['container'][0].isalnum():
                fixed['container'] = 'container-' + fixed['container']
        
        # Fix HDFS path
        if 'hdfs_default_path' in fixed:
            path = fixed['hdfs_default_path']
            # Ensure starts with /
            if not path.startswith('/') and not path.startswith('hdfs://'):
                fixed['hdfs_default_path'] = '/' + path
        
        # Fix boolean values
        for bool_field in ['auto_extract_archives', 'delete_archive_after_extract']:
            if bool_field in fixed and not isinstance(fixed[bool_field], bool):
                # Convert string to boolean
                str_val = str(fixed[bool_field]).lower()
                fixed[bool_field] = str_val in ('true', '1', 'yes', 'on')
        
        return fixed


def validate_and_sanitize_input(value: str, validator_func: Callable, field_name: str) -> str:
    """
    Validate and sanitize user input
    
    Args:
        value: Input value
        validator_func: Validation function
        field_name: Name of field for error messages
    
    Returns:
        Sanitized value
    
    Raises:
        ValidationError: If validation fails
    """
    # Sanitize: remove leading/trailing whitespace
    sanitized = value.strip() if isinstance(value, str) else value
    
    # Validate
    valid, error_msg = validator_func(sanitized)
    if not valid:
        raise ValidationError(error_msg, field=field_name)
    
    return sanitized


# Example usage and tests
if __name__ == '__main__':
    print("=" * 80)
    print("VALIDATION MODULE TESTS")
    print("=" * 80)
    
    # Test container names
    test_containers = [
        ('spark-worker', True),
        ('namenode', True),
        ('my_container-1.0', True),
        ('-invalid', False),
        ('', False),
        ('a' * 300, False),
    ]
    
    print("\n1. Container Name Validation:")
    for name, should_pass in test_containers:
        valid, error = Validator.is_valid_container_name(name)
        status = "✅" if valid == should_pass else "❌"
        print(f"  {status} '{name}': {valid} - {error or 'OK'}")
    
    # Test Spark master URLs
    test_masters = [
        ('spark://spark-master:7077', True),
        ('local[*]', True),
        ('local[4]', True),
        ('yarn', True),
        ('invalid', False),
        ('', False),
    ]
    
    print("\n2. Spark Master URL Validation:")
    for url, should_pass in test_masters:
        valid, error = Validator.is_valid_spark_master(url)
        status = "✅" if valid == should_pass else "❌"
        print(f"  {status} '{url}': {valid} - {error or 'OK'}")
    
    # Test configuration validation
    print("\n3. Configuration Validation:")
    
    valid_config = {
        'container': 'spark-worker',
        'master': 'spark://spark-master:7077',
        'hdfs_host': 'hdfs://namenode:8020',
        'hdfs_default_path': '/user/spark/data',
        'auto_extract_archives': True
    }
    
    is_valid, errors = ConfigValidator.validate_config(valid_config)
    print(f"  Valid config: {is_valid}")
    
    invalid_config = {
        'container': '-invalid',
        'master': 'invalid-url',
        'hdfs_host': 'not-a-url',
        'hdfs_default_path': 'no-leading-slash',
    }
    
    is_valid, errors = ConfigValidator.validate_config(invalid_config)
    print(f"  Invalid config: {is_valid}")
    for error in errors:
        print(f"    - {error}")
    
    # Test config fixing
    print("\n4. Configuration Auto-Fix:")
    fixed = ConfigValidator.fix_config(invalid_config)
    print(f"  Original: {invalid_config}")
    print(f"  Fixed: {fixed}")
    
    print("\n" + "=" * 80)
    print("✅ All validation tests completed!")
    print("=" * 80)
