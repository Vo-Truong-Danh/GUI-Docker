"""
Enhanced Error Handler - Version 3.0
Hệ thống xử lý lỗi nâng cao với recovery và tracking
"""

import sys
import traceback
import logging
from enum import Enum
from typing import Callable, Any, Optional, Dict, List
from datetime import datetime
from functools import wraps
from pathlib import Path
import json


class ErrorSeverity(Enum):
    """Mức độ nghiêm trọng của lỗi"""
    DEBUG = "debug"
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Danh mục lỗi"""
    SYSTEM = "system"
    NETWORK = "network"
    DATABASE = "database"
    FILE_IO = "file_io"
    VALIDATION = "validation"
    SECURITY = "security"
    DOCKER = "docker"
    SPARK = "spark"
    USER_INPUT = "user_input"
    UNKNOWN = "unknown"


class ErrorContext:
    """Ngữ cảnh lỗi chi tiết"""
    
    def __init__(self, operation: str, details: Dict = None):
        self.operation = operation
        self.details = details or {}
        self.timestamp = datetime.now()
        self.stack_trace = traceback.format_exc()
    
    def to_dict(self) -> Dict:
        """Chuyển thành dictionary"""
        return {
            'operation': self.operation,
            'details': self.details,
            'timestamp': self.timestamp.isoformat(),
            'stack_trace': self.stack_trace
        }


class EnhancedErrorHandler:
    """
    Hệ thống xử lý lỗi nâng cao
    
    Features:
    - Automatic error categorization
    - Error recovery suggestions
    - Detailed logging with context
    - Error statistics and reporting
    - Integration with monitoring systems
    """
    
    def __init__(self, logger: logging.Logger = None, log_dir: str = None):
        self.logger = logger or self._create_default_logger()
        self.log_dir = Path(log_dir) if log_dir else Path(__file__).parent / 'logs'
        self.log_dir.mkdir(exist_ok=True)
        
        # Error tracking
        self.error_count = 0
        self.errors_by_severity = {severity: [] for severity in ErrorSeverity}
        self.errors_by_category = {category: [] for category in ErrorCategory}
        self.max_errors_stored = 200
        
        # Recovery strategies
        self.recovery_strategies = {}
        self._register_default_recovery_strategies()
    
    def _create_default_logger(self) -> logging.Logger:
        """Tạo logger mặc định"""
        logger = logging.getLogger('EnhancedErrorHandler')
        logger.setLevel(logging.DEBUG)
        
        # Console handler
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console.setFormatter(formatter)
        logger.addHandler(console)
        
        # File handler
        log_file = self.log_dir / f'errors_{datetime.now().strftime("%Y%m%d")}.log'
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def handle_error(
        self,
        error: Exception,
        context: ErrorContext = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        show_dialog: bool = False,
        attempt_recovery: bool = True
    ) -> Optional[Any]:
        """
        Xử lý lỗi toàn diện
        
        Args:
            error: Exception object
            context: Error context with operation details
            severity: Error severity level
            category: Error category
            show_dialog: Show GUI dialog
            attempt_recovery: Try to recover from error
            
        Returns:
            Recovery result if successful, None otherwise
        """
        self.error_count += 1
        
        # Build error info
        error_info = {
            'id': self.error_count,
            'timestamp': datetime.now().isoformat(),
            'type': type(error).__name__,
            'message': str(error),
            'severity': severity.value,
            'category': category.value,
            'context': context.to_dict() if context else None,
            'traceback': traceback.format_exc()
        }
        
        # Store error
        self._store_error(error_info, severity, category)
        
        # Log error
        self._log_error(error_info)
        
        # Show dialog if requested
        if show_dialog:
            self._show_error_dialog(error_info)
        
        # Attempt recovery
        recovery_result = None
        if attempt_recovery:
            recovery_result = self._attempt_recovery(error, category, context)
            if recovery_result:
                self.logger.info(f"✅ Recovered from error: {type(error).__name__}")
                error_info['recovered'] = True
                error_info['recovery_result'] = str(recovery_result)
        
        return recovery_result
    
    def safe_execute(
        self,
        func: Callable,
        *args,
        default: Any = None,
        context: ErrorContext = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        **kwargs
    ) -> Any:
        """
        Thực thi hàm an toàn với error handling
        
        Args:
            func: Function to execute
            args: Positional arguments
            default: Default value if error occurs
            context: Error context
            severity: Error severity
            category: Error category
            kwargs: Keyword arguments
            
        Returns:
            Function result or default value
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if context is None:
                context = ErrorContext(
                    operation=f"Executing {func.__name__}",
                    details={'args': str(args), 'kwargs': str(kwargs)}
                )
            
            recovery_result = self.handle_error(
                e, context=context, severity=severity, category=category
            )
            
            return recovery_result if recovery_result is not None else default
    
    def decorator(
        self,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        default: Any = None,
        show_dialog: bool = False
    ):
        """
        Decorator để tự động xử lý lỗi
        
        Usage:
            @error_handler.decorator(severity=ErrorSeverity.HIGH)
            def my_function():
                # code here
                pass
        """
        def decorator_wrapper(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    context = ErrorContext(
                        operation=f"Function {func.__name__}",
                        details={
                            'module': func.__module__,
                            'args': str(args)[:100],
                            'kwargs': str(kwargs)[:100]
                        }
                    )
                    
                    recovery_result = self.handle_error(
                        e,
                        context=context,
                        severity=severity,
                        category=category,
                        show_dialog=show_dialog
                    )
                    
                    return recovery_result if recovery_result is not None else default
            
            return wrapper
        return decorator_wrapper
    
    def _store_error(self, error_info: Dict, severity: ErrorSeverity, category: ErrorCategory):
        """Lưu trữ error info"""
        # Store by severity
        severity_list = self.errors_by_severity[severity]
        severity_list.append(error_info)
        if len(severity_list) > self.max_errors_stored:
            severity_list.pop(0)
        
        # Store by category
        category_list = self.errors_by_category[category]
        category_list.append(error_info)
        if len(category_list) > self.max_errors_stored:
            category_list.pop(0)
    
    def _log_error(self, error_info: Dict):
        """Log error với format đẹp"""
        severity = error_info['severity']
        message = (
            f"\n{'='*80}\n"
            f"ERROR #{error_info['id']} - {severity.upper()}\n"
            f"{'='*80}\n"
            f"Type: {error_info['type']}\n"
            f"Message: {error_info['message']}\n"
            f"Category: {error_info['category']}\n"
            f"Timestamp: {error_info['timestamp']}\n"
        )
        
        if error_info.get('context'):
            message += f"Operation: {error_info['context']['operation']}\n"
            if error_info['context'].get('details'):
                message += f"Details: {error_info['context']['details']}\n"
        
        message += f"{'='*80}\n"
        
        # Log according to severity
        if severity == 'critical':
            self.logger.critical(message)
        elif severity == 'high':
            self.logger.error(message)
        elif severity in ['medium', 'low']:
            self.logger.warning(message)
        else:
            self.logger.info(message)
        
        # Log traceback at debug level
        self.logger.debug(f"Traceback:\n{error_info['traceback']}")
    
    def _show_error_dialog(self, error_info: Dict):
        """Hiển thị dialog lỗi (nếu có GUI)"""
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            title = f"Error - {error_info['severity'].upper()}"
            message = (
                f"{error_info['type']}: {error_info['message']}\n\n"
                f"Category: {error_info['category']}\n"
            )
            
            if error_info.get('context'):
                message += f"Operation: {error_info['context']['operation']}\n"
            
            messagebox.showerror(title, message)
        except:
            pass  # GUI not available
    
    def _register_default_recovery_strategies(self):
        """Đăng ký các chiến lược recovery mặc định"""
        
        # File not found recovery
        def recover_file_not_found(error, context):
            """Try to find file in common locations"""
            if context and 'file_path' in context.details:
                file_path = Path(context.details['file_path'])
                # Try common locations
                common_dirs = ['.', 'data', 'config', 'resources']
                for dir_name in common_dirs:
                    alternative = Path(dir_name) / file_path.name
                    if alternative.exists():
                        return str(alternative)
            return None
        
        self.register_recovery_strategy(FileNotFoundError, recover_file_not_found)
        
        # Connection error recovery
        def recover_connection_error(error, context):
            """Suggest retry with backoff"""
            return {
                'action': 'retry',
                'suggestion': 'Retry with exponential backoff',
                'max_retries': 3
            }
        
        self.register_recovery_strategy(ConnectionError, recover_connection_error)
    
    def register_recovery_strategy(self, error_type: type, strategy: Callable):
        """Đăng ký strategy recovery cho loại lỗi cụ thể"""
        self.recovery_strategies[error_type] = strategy
    
    def _attempt_recovery(self, error: Exception, category: ErrorCategory, context: ErrorContext) -> Optional[Any]:
        """Thử recovery từ error"""
        error_type = type(error)
        
        # Try specific recovery strategy
        if error_type in self.recovery_strategies:
            try:
                strategy = self.recovery_strategies[error_type]
                return strategy(error, context)
            except Exception as recovery_error:
                self.logger.warning(f"Recovery failed: {recovery_error}")
        
        return None
    
    def get_statistics(self) -> Dict:
        """Lấy thống kê lỗi"""
        stats = {
            'total_errors': self.error_count,
            'by_severity': {},
            'by_category': {},
            'recent_errors': []
        }
        
        # Count by severity
        for severity, errors in self.errors_by_severity.items():
            stats['by_severity'][severity.value] = len(errors)
        
        # Count by category
        for category, errors in self.errors_by_category.items():
            stats['by_category'][category.value] = len(errors)
        
        # Recent errors (last 10)
        all_errors = []
        for errors in self.errors_by_severity.values():
            all_errors.extend(errors)
        
        # Sort by timestamp
        all_errors.sort(key=lambda x: x['timestamp'], reverse=True)
        stats['recent_errors'] = all_errors[:10]
        
        return stats
    
    def export_report(self, output_path: str = None) -> str:
        """Export báo cáo lỗi"""
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = self.log_dir / f'error_report_{timestamp}.json'
        
        stats = self.get_statistics()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Error report exported to: {output_path}")
        return str(output_path)
    
    def clear_errors(self, severity: ErrorSeverity = None, category: ErrorCategory = None):
        """Xóa errors đã lưu"""
        if severity:
            self.errors_by_severity[severity].clear()
        elif category:
            self.errors_by_category[category].clear()
        else:
            for errors in self.errors_by_severity.values():
                errors.clear()
            for errors in self.errors_by_category.values():
                errors.clear()
            self.error_count = 0


# Global instance
_global_error_handler = None


def get_error_handler(logger: logging.Logger = None) -> EnhancedErrorHandler:
    """Lấy hoặc tạo global error handler"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = EnhancedErrorHandler(logger)
    return _global_error_handler


# Convenience functions
def handle_error(error: Exception, **kwargs):
    """Convenience function để xử lý lỗi"""
    handler = get_error_handler()
    return handler.handle_error(error, **kwargs)


def safe_execute(func: Callable, *args, **kwargs):
    """Convenience function để execute an toàn"""
    handler = get_error_handler()
    return handler.safe_execute(func, *args, **kwargs)


def error_handler_decorator(**decorator_kwargs):
    """Convenience decorator"""
    handler = get_error_handler()
    return handler.decorator(**decorator_kwargs)


if __name__ == '__main__':
    # Demo
    handler = get_error_handler()
    
    # Test error handling
    @handler.decorator(severity=ErrorSeverity.HIGH, category=ErrorCategory.FILE_IO)
    def test_function():
        raise FileNotFoundError("Test file not found")
    
    test_function()
    
    # Print statistics
    stats = handler.get_statistics()
    print("\nError Statistics:")
    print(json.dumps(stats, indent=2))
