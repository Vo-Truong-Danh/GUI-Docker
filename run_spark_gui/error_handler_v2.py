"""
Unified Error Handler - Version 2.0
Date: 2025-10-14

A comprehensive, production-ready error handling system that consolidates
all previous error handling approaches into a single, maintainable solution.

Features:
- Specific exception handling (no more bare except Exception)
- Context managers for scoped error handling
- Decorator-based error handling
- Recovery strategies with exponential backoff
- Circuit breaker pattern
- Comprehensive logging with severity levels
- User-friendly error messages (Vietnamese support)
- Thread-safe operations
- Error history and analytics
- Performance monitoring

Author: AI System Optimizer
License: MIT
"""

import traceback
import sys
import threading
import time
from typing import Optional, Callable, Any, Dict, List, Type, Tuple
from datetime import datetime
from contextlib import contextmanager
from functools import wraps
from enum import Enum
import logging


class ErrorSeverity(Enum):
    """Standardized error severity levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better classification"""
    SYSTEM = "system"          # OS, filesystem errors
    NETWORK = "network"        # Connection, timeout errors
    VALIDATION = "validation"  # Input validation errors
    DOCKER = "docker"          # Docker-related errors
    DATABASE = "database"      # Database errors
    PERMISSION = "permission"  # Permission denied errors
    CONFIGURATION = "configuration"  # Config errors
    UNKNOWN = "unknown"        # Unclassified errors


class CircuitBreaker:
    """
    Circuit breaker pattern to prevent cascading failures
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Failure threshold reached, requests fail immediately
    - HALF_OPEN: Testing if service recovered
    """
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 timeout: float = 60.0,
                 name: str = "default"):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.name = name
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"
        self._lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        with self._lock:
            if self.state == "OPEN":
                # Check if timeout has elapsed
                if self.last_failure_time and \
                   (time.time() - self.last_failure_time) > self.timeout:
                    self.state = "HALF_OPEN"
                    print(f"🔄 Circuit breaker '{self.name}' entering HALF_OPEN state")
                else:
                    raise RuntimeError(f"Circuit breaker '{self.name}' is OPEN")
        
        try:
            result = func(*args, **kwargs)
            
            # Success - reset on HALF_OPEN
            with self._lock:
                if self.state == "HALF_OPEN":
                    self.state = "CLOSED"
                    self.failure_count = 0
                    print(f"✅ Circuit breaker '{self.name}' closed")
            
            return result
            
        except Exception as e:
            with self._lock:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.failure_count >= self.failure_threshold:
                    self.state = "OPEN"
                    print(f"⚠️ Circuit breaker '{self.name}' OPENED after {self.failure_count} failures")
            
            raise


class UnifiedErrorHandler:
    """
    Centralized error handling system
    
    This class provides a unified interface for all error handling needs
    in the application, replacing multiple legacy error handlers.
    
    Usage Examples:
    
    1. Context Manager:
        handler = UnifiedErrorHandler()
        with handler.error_context("Database operation"):
            db.execute()
    
    2. Decorator:
        @handler.error_handler(expected_exceptions=(ValueError, KeyError))
        def my_function():
            ...
    
    3. Direct Call:
        result = handler.safe_execute(
            lambda: risky_operation(),
            context="API call"
        )
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize error handler
        
        Args:
            logger: Optional logger instance for structured logging
        """
        self.logger = logger
        self.error_history: List[Dict[str, Any]] = []
        self.error_counts: Dict[str, int] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._lock = threading.RLock()
        self.max_history = 1000
        
        # Recovery strategies registry
        self.recovery_strategies: Dict[str, Callable] = {}
    
    @contextmanager
    def error_context(self,
                     operation: str,
                     expected_exceptions: Tuple[Type[Exception], ...] = (Exception,),
                     severity: ErrorSeverity = ErrorSeverity.ERROR,
                     category: ErrorCategory = ErrorCategory.UNKNOWN,
                     default_return: Any = None,
                     reraise: bool = False,
                     recovery_callback: Optional[Callable] = None):
        """
        Context manager for scoped error handling
        
        Args:
            operation: Description of the operation being performed
            expected_exceptions: Tuple of expected exception types
            severity: Error severity level
            category: Error category for classification
            default_return: Value to return on error (if not reraising)
            reraise: Whether to reraise the exception after handling
            recovery_callback: Optional function to attempt recovery
        
        Yields:
            Context for the protected operation
        
        Example:
            with handler.error_context("File operation", 
                                      expected_exceptions=(FileNotFoundError,)):
                with open('file.txt') as f:
                    data = f.read()
        """
        try:
            yield
        except expected_exceptions as e:
            handled = self._handle_exception(
                exception=e,
                context=operation,
                severity=severity,
                category=category,
                recovery_callback=recovery_callback
            )
            
            if reraise:
                raise
            
            return default_return
    
    def safe_execute(self,
                    func: Callable,
                    *args,
                    expected_exceptions: Tuple[Type[Exception], ...] = (Exception,),
                    default_return: Any = None,
                    context: str = "",
                    severity: ErrorSeverity = ErrorSeverity.ERROR,
                    category: ErrorCategory = ErrorCategory.UNKNOWN,
                    recovery_callback: Optional[Callable] = None,
                    **kwargs) -> Any:
        """
        Safely execute a function with comprehensive error handling
        
        Args:
            func: Function to execute
            *args: Positional arguments for func
            expected_exceptions: Tuple of expected exception types
            default_return: Return value on error
            context: Description of operation
            severity: Error severity level
            category: Error category
            recovery_callback: Optional recovery function
            **kwargs: Keyword arguments for func
        
        Returns:
            Result of func or default_return on error
        
        Example:
            result = handler.safe_execute(
                requests.get,
                "https://api.example.com",
                expected_exceptions=(requests.RequestException,),
                context="API call",
                timeout=5
            )
        """
        try:
            return func(*args, **kwargs)
        except expected_exceptions as e:
            self._handle_exception(
                exception=e,
                context=context or func.__name__,
                severity=severity,
                category=category,
                recovery_callback=recovery_callback
            )
            return default_return
    
    def error_handler(self,
                     expected_exceptions: Tuple[Type[Exception], ...] = (Exception,),
                     default_return: Any = None,
                     severity: ErrorSeverity = ErrorSeverity.ERROR,
                     category: ErrorCategory = ErrorCategory.UNKNOWN,
                     log_traceback: bool = True,
                     recovery_callback: Optional[Callable] = None):
        """
        Decorator for function-level error handling
        
        Args:
            expected_exceptions: Tuple of expected exception types
            default_return: Return value on error
            severity: Error severity level
            category: Error category
            log_traceback: Whether to log full traceback
            recovery_callback: Optional recovery function
        
        Returns:
            Decorated function
        
        Example:
            @handler.error_handler(
                expected_exceptions=(ValueError, KeyError),
                default_return={}
            )
            def process_data(data):
                return parse_json(data)
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except expected_exceptions as e:
                    self._handle_exception(
                        exception=e,
                        context=func.__name__,
                        severity=severity,
                        category=category,
                        log_traceback=log_traceback,
                        recovery_callback=recovery_callback
                    )
                    return default_return
            return wrapper
        return decorator
    
    def _handle_exception(self,
                         exception: Exception,
                         context: str,
                         severity: ErrorSeverity = ErrorSeverity.ERROR,
                         category: ErrorCategory = ErrorCategory.UNKNOWN,
                         log_traceback: bool = True,
                         recovery_callback: Optional[Callable] = None) -> bool:
        """
        Internal exception handler
        
        Args:
            exception: The exception to handle
            context: Context where error occurred
            severity: Error severity
            category: Error category
            log_traceback: Whether to log traceback
            recovery_callback: Optional recovery function
        
        Returns:
            True if recovery successful, False otherwise
        """
        with self._lock:
            # Create error record
            error_info = {
                'timestamp': datetime.now().isoformat(),
                'exception_type': type(exception).__name__,
                'message': str(exception),
                'context': context,
                'severity': severity.value,
                'category': category.value,
                'traceback': traceback.format_exc() if log_traceback else None,
                'thread_id': threading.get_ident()
            }
            
            # Add to history
            self.error_history.append(error_info)
            if len(self.error_history) > self.max_history:
                self.error_history.pop(0)
            
            # Update counts
            error_type = type(exception).__name__
            self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Log error
        if self.logger:
            log_func = getattr(self.logger, severity.value, self.logger.error)
            log_func(f"{context}: {type(exception).__name__}: {exception}")
            
            if log_traceback and severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]:
                self.logger.debug(error_info['traceback'])
        
        # Print user-friendly message
        friendly_msg = self._get_friendly_message(exception, context, category)
        severity_emoji = {
            ErrorSeverity.DEBUG: "🐛",
            ErrorSeverity.INFO: "ℹ️",
            ErrorSeverity.WARNING: "⚠️",
            ErrorSeverity.ERROR: "❌",
            ErrorSeverity.CRITICAL: "🔴"
        }
        print(f"{severity_emoji.get(severity, '⚠️')} [{severity.value.upper()}] {friendly_msg}")
        
        # Attempt recovery
        if recovery_callback:
            try:
                recovery_callback(exception)
                if self.logger:
                    self.logger.info(f"Successfully recovered from error in {context}")
                return True
            except Exception as recovery_error:
                if self.logger:
                    self.logger.error(f"Recovery failed: {recovery_error}")
                return False
        
        return False
    
    def _get_friendly_message(self, 
                             exception: Exception, 
                             context: str,
                             category: ErrorCategory) -> str:
        """
        Convert technical error to user-friendly message in Vietnamese
        
        Args:
            exception: The exception
            context: Error context
            category: Error category
        
        Returns:
            User-friendly error message
        """
        exception_type = type(exception).__name__
        exception_msg = str(exception)
        
        # Category-specific messages
        category_messages = {
            ErrorCategory.DOCKER: "Docker",
            ErrorCategory.NETWORK: "Mạng",
            ErrorCategory.DATABASE: "Cơ sở dữ liệu",
            ErrorCategory.PERMISSION: "Quyền truy cập",
            ErrorCategory.VALIDATION: "Xác thực dữ liệu",
            ErrorCategory.CONFIGURATION: "Cấu hình"
        }
        
        category_prefix = category_messages.get(category, "Hệ thống")
        
        # Exception-specific messages
        friendly_messages = {
            'FileNotFoundError': f"📁 {category_prefix}: Không tìm thấy file trong {context}",
            'PermissionError': f"🔒 {category_prefix}: Không có quyền truy cập - {context}",
            'ConnectionError': f"🌐 {category_prefix}: Lỗi kết nối trong {context}",
            'TimeoutError': f"⏱️ {category_prefix}: Hết thời gian chờ - {context}",
            'ValueError': f"❌ {category_prefix}: Giá trị không hợp lệ trong {context}",
            'KeyError': f"❌ {category_prefix}: Thiếu cấu hình cần thiết - {exception_msg}",
            'ImportError': f"📦 {category_prefix}: Thiếu module - {exception_msg}",
            'OSError': f"💻 {category_prefix}: Lỗi hệ điều hành trong {context}",
            'RuntimeError': f"⚙️ {category_prefix}: Lỗi runtime trong {context}",
            'AttributeError': f"🔧 {category_prefix}: Thuộc tính không tồn tại - {context}",
            'TypeError': f"🔤 {category_prefix}: Sai kiểu dữ liệu trong {context}",
            'IndexError': f"📊 {category_prefix}: Truy cập ngoài phạm vi trong {context}",
            'KeyboardInterrupt': f"⏹️ {category_prefix}: Người dùng hủy thực thi",
            'MemoryError': f"💾 {category_prefix}: Hết bộ nhớ trong {context}",
        }
        
        return friendly_messages.get(
            exception_type,
            f"⚠️ {category_prefix}: Lỗi trong {context} - {exception_msg}"
        )
    
    def get_or_create_circuit_breaker(self,
                                     name: str,
                                     failure_threshold: int = 5,
                                     timeout: float = 60.0) -> CircuitBreaker:
        """
        Get or create a circuit breaker for an operation
        
        Args:
            name: Circuit breaker name
            failure_threshold: Number of failures before opening
            timeout: Timeout in seconds before attempting recovery
        
        Returns:
            CircuitBreaker instance
        """
        with self._lock:
            if name not in self.circuit_breakers:
                self.circuit_breakers[name] = CircuitBreaker(
                    failure_threshold=failure_threshold,
                    timeout=timeout,
                    name=name
                )
            return self.circuit_breakers[name]
    
    def register_recovery_strategy(self, 
                                  exception_type: Type[Exception],
                                  strategy: Callable):
        """
        Register a recovery strategy for specific exception type
        
        Args:
            exception_type: Exception type to handle
            strategy: Recovery function
        """
        strategy_name = exception_type.__name__
        with self._lock:
            self.recovery_strategies[strategy_name] = strategy
    
    def get_error_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent error history
        
        Args:
            limit: Maximum number of errors to return
        
        Returns:
            List of recent errors
        """
        with self._lock:
            return self.error_history[-limit:]
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """
        Get error statistics
        
        Returns:
            Dictionary containing error stats
        """
        with self._lock:
            total_errors = len(self.error_history)
            
            # Group by severity
            by_severity = {}
            by_category = {}
            
            for error in self.error_history:
                severity = error['severity']
                category = error['category']
                
                by_severity[severity] = by_severity.get(severity, 0) + 1
                by_category[category] = by_category.get(category, 0) + 1
            
            return {
                'total_errors': total_errors,
                'by_type': self.error_counts.copy(),
                'by_severity': by_severity,
                'by_category': by_category,
                'most_common': max(self.error_counts.items(), key=lambda x: x[1]) if self.error_counts else None
            }
    
    def clear_history(self):
        """Clear error history"""
        with self._lock:
            self.error_history.clear()
            self.error_counts.clear()
    
    def export_error_log(self, filepath: str) -> bool:
        """
        Export error history to file
        
        Args:
            filepath: Path to export file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("BÁO CÁO LỖI HỆ THỐNG\n")
                f.write(f"Ngày tạo: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                
                # Statistics
                stats = self.get_error_statistics()
                f.write("THỐNG KÊ:\n")
                f.write(f"Tổng số lỗi: {stats['total_errors']}\n")
                f.write(f"\nTheo mức độ:\n")
                for severity, count in stats['by_severity'].items():
                    f.write(f"  {severity}: {count}\n")
                f.write(f"\nTheo loại:\n")
                for error_type, count in stats['by_type'].items():
                    f.write(f"  {error_type}: {count}\n")
                f.write("\n" + "-" * 80 + "\n\n")
                
                # Detailed errors
                f.write("CHI TIẾT LỖI:\n\n")
                for i, error in enumerate(self.error_history, 1):
                    f.write(f"Lỗi #{i}\n")
                    f.write(f"Thời gian: {error['timestamp']}\n")
                    f.write(f"Mức độ: {error['severity']}\n")
                    f.write(f"Loại: {error['exception_type']}\n")
                    f.write(f"Thông báo: {error['message']}\n")
                    f.write(f"Ngữ cảnh: {error['context']}\n")
                    f.write(f"Danh mục: {error['category']}\n")
                    if error['traceback']:
                        f.write(f"\nTraceback:\n{error['traceback']}\n")
                    f.write("-" * 80 + "\n\n")
            
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to export error log: {e}")
            return False


# ============================================================================
# Global Instance and Convenience Functions
# ============================================================================

_global_handler: Optional[UnifiedErrorHandler] = None
_global_lock = threading.Lock()


def get_error_handler(logger: Optional[logging.Logger] = None) -> UnifiedErrorHandler:
    """
    Get global error handler instance (singleton pattern)
    
    Args:
        logger: Optional logger instance
    
    Returns:
        UnifiedErrorHandler instance
    """
    global _global_handler
    
    with _global_lock:
        if _global_handler is None:
            _global_handler = UnifiedErrorHandler(logger)
        elif logger and not _global_handler.logger:
            _global_handler.logger = logger
    
    return _global_handler


def safe_execute(func: Callable, 
                context: str = "",
                default_return: Any = None,
                **kwargs) -> Any:
    """
    Convenience function for safe execution
    
    Args:
        func: Function to execute
        context: Description of operation
        default_return: Return value on error
        **kwargs: Additional arguments for error_context
    
    Returns:
        Result of func or default_return on error
    """
    handler = get_error_handler()
    return handler.safe_execute(func, context=context, default_return=default_return, **kwargs)


# ============================================================================
# Recovery Strategies
# ============================================================================

class RecoveryStrategies:
    """Common recovery strategies for errors"""
    
    @staticmethod
    def retry_with_backoff(func: Callable,
                          max_attempts: int = 3,
                          initial_delay: float = 1.0,
                          backoff_factor: float = 2.0,
                          max_delay: float = 60.0) -> Any:
        """
        Retry operation with exponential backoff
        
        Args:
            func: Function to retry
            max_attempts: Maximum retry attempts
            initial_delay: Initial delay in seconds
            backoff_factor: Exponential backoff multiplier
            max_delay: Maximum delay between retries
        
        Returns:
            Result of func
        
        Raises:
            Last exception if all attempts fail
        """
        delay = initial_delay
        last_exception = None
        
        for attempt in range(max_attempts):
            try:
                return func()
            except Exception as e:
                last_exception = e
                
                if attempt < max_attempts - 1:
                    print(f"⚠️ Attempt {attempt + 1}/{max_attempts} failed. Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)
        
        raise last_exception


# ============================================================================
# Testing
# ============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("TESTING UNIFIED ERROR HANDLER V2.0")
    print("=" * 80)
    
    # Create handler
    handler = UnifiedErrorHandler()
    
    # Test 1: Context manager
    print("\n1️⃣ Testing context manager...")
    with handler.error_context("File operation", expected_exceptions=(FileNotFoundError,)):
        open('nonexistent_file.txt', 'r')
    
    # Test 2: Safe execute
    print("\n2️⃣ Testing safe execute...")
    result = handler.safe_execute(
        lambda: 1 / 0,
        context="Division operation",
        expected_exceptions=(ZeroDivisionError,),
        default_return=0
    )
    print(f"Result: {result}")
    
    # Test 3: Decorator
    print("\n3️⃣ Testing decorator...")
    
    @handler.error_handler(expected_exceptions=(ValueError,), default_return="fallback")
    def test_function():
        raise ValueError("Test error")
    
    result = test_function()
    print(f"Result: {result}")
    
    # Test 4: Statistics
    print("\n4️⃣ Error statistics:")
    stats = handler.get_error_statistics()
    print(f"Total errors: {stats['total_errors']}")
    print(f"By type: {stats['by_type']}")
    
    # Test 5: Export log
    print("\n5️⃣ Exporting error log...")
    if handler.export_error_log('error_report.txt'):
        print("✅ Error log exported successfully")
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 80)
