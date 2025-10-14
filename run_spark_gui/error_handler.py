"""
Enhanced Error Handler Module
Provides comprehensive error handling with logging, recovery, and tracking
"""
import sys
import traceback
from enum import Enum
from typing import Callable, Any, Optional, Dict
from datetime import datetime
from functools import wraps


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorHandler:
    """Enhanced error handler with logging and recovery"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.error_count = 0
        self.errors = []
        self.max_errors_stored = 100
    
    def handle_error(self, error: Exception, context: str = "", 
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    show_dialog: bool = False) -> None:
        """Handle an error with logging and optional user notification"""
        self.error_count += 1
        
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'type': type(error).__name__,
            'message': str(error),
            'context': context,
            'severity': severity.value,
            'traceback': traceback.format_exc()
        }
        
        # Store error (limit storage)
        self.errors.append(error_info)
        if len(self.errors) > self.max_errors_stored:
            self.errors.pop(0)
        
        # Log error
        if self.logger:
            log_message = f"{context}: {type(error).__name__}: {str(error)}"
            if severity == ErrorSeverity.CRITICAL:
                self.logger.critical(log_message)
            elif severity == ErrorSeverity.HIGH:
                self.logger.error(log_message)
            elif severity == ErrorSeverity.MEDIUM:
                self.logger.warning(log_message)
            else:
                self.logger.info(log_message)
        
        # Print to console
        print(f"❌ {severity.value.upper()}: {context}")
        print(f"   {type(error).__name__}: {str(error)}")
        
        if show_dialog:
            try:
                import tkinter as tk
                from tkinter import messagebox
                messagebox.showerror(
                    f"Error - {severity.value.upper()}",
                    f"{context}\n\n{type(error).__name__}: {str(error)}"
                )
            except:
                pass  # Ignore if GUI not available
    
    def safe_execute(self, func: Callable, *args, 
                    default=None, context: str = "",
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    **kwargs) -> Any:
        """Execute a function safely with error handling"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.handle_error(e, context=context or f"Executing {func.__name__}", 
                            severity=severity)
            return default
    
    def get_error_stats(self) -> Dict:
        """Get error statistics"""
        return {
            'total_errors': self.error_count,
            'stored_errors': len(self.errors),
            'recent_errors': self.errors[-10:] if self.errors else []
        }
    
    def clear_errors(self):
        """Clear stored errors"""
        self.errors.clear()
        self.error_count = 0


# Global error handler instance
_error_handler = None


def get_error_handler(logger=None) -> ErrorHandler:
    """Get or create global error handler instance"""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler(logger)
    return _error_handler


def safe_execute(func: Callable, *args, default=None, 
                context: str = "", **kwargs) -> Any:
    """Convenience function for safe execution"""
    handler = get_error_handler()
    return handler.safe_execute(func, *args, default=default, 
                               context=context, **kwargs)


def with_error_handling(context: str = "", 
                       severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                       default=None):
    """Decorator for error handling"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            handler = get_error_handler()
            return handler.safe_execute(
                func, *args, 
                context=context or f"Function {func.__name__}",
                severity=severity,
                default=default,
                **kwargs
            )
        return wrapper
    return decorator
