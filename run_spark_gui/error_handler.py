"""
Enhanced Error Handler Module
Version: 1.0.0

Features:
- Centralized error handling
- Error recovery strategies
- User-friendly error messages
- Error logging and tracking
"""

import traceback
import sys
from typing import Optional, Callable, Any, Dict
from datetime import datetime
from pathlib import Path


class ErrorSeverity:
    """Error severity levels"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ErrorHandler:
    """Centralized error handling with recovery strategies and circuit breaker"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.error_history = []
        self.max_history = 100
        self.error_counts = {}  # Track error frequency by type
        self.circuit_breakers = {}  # Circuit breakers for specific operations
        
    def get_or_create_circuit_breaker(self, operation_name: str, 
                                     failure_threshold: int = 5, 
                                     timeout: int = 60):
        """Get or create circuit breaker for an operation"""
        if operation_name not in self.circuit_breakers:
            try:
                from system_utils import CircuitBreaker
                self.circuit_breakers[operation_name] = CircuitBreaker(
                    failure_threshold=failure_threshold,
                    timeout=timeout
                )
            except ImportError:
                # Circuit breaker not available, return None
                return None
        return self.circuit_breakers[operation_name]
        
    def handle_error(
        self,
        error: Exception,
        context: str = "",
        severity: str = ErrorSeverity.ERROR,
        recovery_callback: Optional[Callable] = None,
        user_callback: Optional[Callable] = None
    ) -> bool:
        """
        Handle an error with optional recovery
        
        Args:
            error: The exception to handle
            context: Context where error occurred
            severity: Error severity level
            recovery_callback: Optional recovery function
            user_callback: Optional callback to notify user
            
        Returns:
            bool: True if recovered, False otherwise
        """
        # Create error record
        error_record = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'severity': severity,
            'traceback': traceback.format_exc()
        }
        
        # Add to history
        self.error_history.append(error_record)
        if len(self.error_history) > self.max_history:
            self.error_history.pop(0)
        
        # Track error frequency
        error_type = type(error).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Log error
        if self.logger:
            log_method = {
                ErrorSeverity.INFO: self.logger.info,
                ErrorSeverity.WARNING: self.logger.warning,
                ErrorSeverity.ERROR: self.logger.error,
                ErrorSeverity.CRITICAL: self.logger.critical
            }.get(severity, self.logger.error)
            
            log_method(f"{context}: {type(error).__name__}: {str(error)}")
            if severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]:
                self.logger.debug(error_record['traceback'])
        
        # Notify user with friendly message
        if user_callback:
            user_message = self._get_user_friendly_message(error, context)
            user_callback(user_message, severity.lower())
        
        # Attempt recovery
        if recovery_callback:
            try:
                recovery_callback(error)
                if self.logger:
                    self.logger.info(f"Successfully recovered from error in {context}")
                return True
            except Exception as recovery_error:
                if self.logger:
                    self.logger.error(f"Recovery failed: {recovery_error}")
                return False
        
        return False
    
    def _get_user_friendly_message(self, error: Exception, context: str) -> str:
        """Convert technical error to user-friendly message"""
        error_type = type(error).__name__
        error_msg = str(error)
        
        # Common error patterns and friendly messages
        patterns = {
            'FileNotFoundError': f"📁 File not found: {self._extract_path(error_msg)}",
            'PermissionError': f"🔒 Permission denied. Please check file/folder permissions.",
            'ConnectionError': f"🌐 Connection failed. Please check your network connection.",
            'TimeoutError': f"⏱️ Operation timed out. The system might be slow or unresponsive.",
            'ValueError': f"❌ Invalid value provided. Please check your input.",
            'KeyError': f"❌ Missing required configuration: {error_msg}",
            'ImportError': f"📦 Missing module: {error_msg}. Please install required dependencies.",
            'subprocess.CalledProcessError': f"⚠️ Command failed: {error_msg}",
            'json.JSONDecodeError': f"📄 Invalid JSON format. Please check your configuration file.",
        }
        
        # Check for specific patterns
        for pattern, message in patterns.items():
            if pattern in error_type:
                return f"{message}\n\nContext: {context}"
        
        # Generic message
        return f"❌ {error_type} in {context}: {error_msg}"
    
    def _extract_path(self, error_msg: str) -> str:
        """Extract file path from error message"""
        # Simple extraction - can be improved
        parts = error_msg.split("'")
        if len(parts) >= 2:
            return parts[1]
        return error_msg
    
    def get_error_history(self, limit: int = 10) -> list:
        """Get recent error history"""
        return self.error_history[-limit:]
    
    def clear_history(self):
        """Clear error history"""
        self.error_history.clear()
    
    def export_error_log(self, filepath: str) -> bool:
        """Export error history to file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("ERROR HISTORY REPORT\n")
                f.write("=" * 80 + "\n\n")
                
                for i, error in enumerate(self.error_history, 1):
                    f.write(f"Error #{i}\n")
                    f.write(f"Timestamp: {error['timestamp']}\n")
                    f.write(f"Severity: {error['severity']}\n")
                    f.write(f"Type: {error['error_type']}\n")
                    f.write(f"Message: {error['error_message']}\n")
                    f.write(f"Context: {error['context']}\n")
                    f.write(f"\nTraceback:\n{error['traceback']}\n")
                    f.write("-" * 80 + "\n\n")
            
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to export error log: {e}")
            return False


class ErrorRecoveryStrategies:
    """Common error recovery strategies"""
    
    @staticmethod
    def retry_operation(operation: Callable, max_attempts: int = 3, delay: float = 1.0, 
                       backoff_factor: float = 2.0) -> Any:
        """
        Retry operation with exponential backoff
        
        Args:
            operation: Callable to retry
            max_attempts: Maximum retry attempts
            delay: Initial delay in seconds
            backoff_factor: Exponential backoff multiplier
            
        Returns:
            Result of operation
            
        Raises:
            Last exception if all attempts fail
        """
        import time
        
        last_exception = None
        for attempt in range(max_attempts):
            try:
                return operation()
            except Exception as e:
                last_exception = e
                if attempt == max_attempts - 1:
                    raise last_exception
                
                wait_time = delay * (backoff_factor ** attempt)
                print(f"⚠️ Attempt {attempt + 1}/{max_attempts} failed. Retrying in {wait_time:.1f}s...")
                time.sleep(wait_time)
        
        raise last_exception
    
    @staticmethod
    def use_default_value(default: Any) -> Callable:
        """Return default value on error"""
        def recovery(error: Exception):
            return default
        return recovery
    
    @staticmethod
    def create_missing_directory(path: str) -> Callable:
        """Create directory if it doesn't exist"""
        def recovery(error: Exception):
            if isinstance(error, FileNotFoundError):
                from pathlib import Path
                Path(path).mkdir(parents=True, exist_ok=True)
                print(f"✅ Created missing directory: {path}")
        return recovery
    
    @staticmethod
    def restart_docker() -> Callable:
        """Attempt to restart Docker on connection errors"""
        def recovery(error: Exception):
            error_msg = str(error).lower()
            if any(keyword in error_msg for keyword in ['docker', 'connection', 'daemon']):
                try:
                    from docker_utils import start_docker_desktop, wait_for_docker
                    success, message = start_docker_desktop()
                    if success:
                        print(f"🔄 {message}")
                        if wait_for_docker(timeout=60):
                            print("✅ Docker restarted successfully")
                            return True
                except Exception as e:
                    print(f"❌ Failed to restart Docker: {e}")
            return False
        return recovery
    
    @staticmethod
    def clear_cache_and_retry() -> Callable:
        """Clear cache and retry operation"""
        def recovery(error: Exception):
            try:
                from system_utils import cache_manager
                cache_manager.clear_all()
                print("🗑️ Cache cleared, ready to retry")
                return True
            except Exception as e:
                print(f"⚠️ Failed to clear cache: {e}")
                return False
        return recovery
    
    @staticmethod
    def fallback_to_safe_mode(safe_operation: Callable) -> Callable:
        """Fallback to a safer alternative operation"""
        def recovery(error: Exception):
            try:
                print("⚠️ Primary operation failed, using fallback...")
                result = safe_operation()
                print("✅ Fallback operation succeeded")
                return result
            except Exception as e:
                print(f"❌ Fallback also failed: {e}")
                raise
        return recovery
    
    @staticmethod
    def reset_configuration() -> Callable:
        """Reset configuration to defaults"""
        def recovery(error: Exception):
            # Implementation depends on app configuration
            pass
        return recovery


# Global error handler instance
_global_error_handler = None


def get_error_handler(logger=None) -> ErrorHandler:
    """Get global error handler instance"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler(logger)
    return _global_error_handler


def safe_execute(
    operation: Callable,
    context: str = "",
    default_return: Any = None,
    user_callback: Optional[Callable] = None,
    logger=None
) -> Any:
    """
    Safely execute an operation with error handling
    
    Args:
        operation: Function to execute
        context: Description of operation
        default_return: Value to return on error
        user_callback: Callback to notify user of errors
        logger: Optional logger
        
    Returns:
        Result of operation or default_return on error
    """
    error_handler = get_error_handler(logger)
    
    try:
        return operation()
    except Exception as e:
        error_handler.handle_error(
            error=e,
            context=context,
            severity=ErrorSeverity.ERROR,
            user_callback=user_callback
        )
        return default_return


if __name__ == "__main__":
    # Test error handler
    handler = ErrorHandler()
    
    # Test file not found error
    try:
        open('nonexistent_file.txt', 'r')
    except Exception as e:
        handler.handle_error(
            error=e,
            context="Reading configuration file",
            severity=ErrorSeverity.ERROR,
            user_callback=lambda msg, sev: print(f"[{sev.upper()}] {msg}")
        )
    
    # Print error history
    print("\n" + "=" * 80)
    print("ERROR HISTORY:")
    for error in handler.get_error_history():
        print(f"- {error['timestamp']}: {error['error_type']} in {error['context']}")
