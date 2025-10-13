"""
Comprehensive Logging System
Version: 5.0.0
Features:
- Multi-level logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- File rotation with size and time-based limits
- Structured logging with JSON support
- Thread-safe operations
- Performance metrics integration
"""

import logging
import logging.handlers
import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import threading


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging with JSON support"""
    
    def __init__(self, include_json=False):
        super().__init__()
        self.include_json = include_json
    
    def format(self, record: logging.LogRecord) -> str:
        if self.include_json:
            log_data = {
                'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno
            }
            
            # Add exception info if present
            if record.exc_info:
                log_data['exception'] = self.formatException(record.exc_info)
            
            # Add extra fields
            if hasattr(record, 'extra_data'):
                log_data['extra'] = record.extra_data
            
            return json.dumps(log_data, ensure_ascii=False)
        else:
            # Human-readable format
            timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
            level_color = self._get_level_color(record.levelname)
            reset_color = '\033[0m' if sys.platform != 'win32' else ''
            
            base_msg = f"[{timestamp}] {level_color}{record.levelname:8s}{reset_color} | {record.name:20s} | {record.getMessage()}"
            
            if record.exc_info:
                base_msg += '\n' + self.formatException(record.exc_info)
            
            return base_msg
    
    def _get_level_color(self, level: str) -> str:
        """Get ANSI color code for log level"""
        if sys.platform == 'win32':
            return ''  # Windows console doesn't support ANSI colors by default
        
        colors = {
            'DEBUG': '\033[36m',     # Cyan
            'INFO': '\033[32m',      # Green
            'WARNING': '\033[33m',   # Yellow
            'ERROR': '\033[31m',     # Red
            'CRITICAL': '\033[35m'   # Magenta
        }
        return colors.get(level, '\033[0m')


class LoggerManager:
    """Centralized logger management"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.loggers: Dict[str, logging.Logger] = {}
            self.log_dir = Path(__file__).parent / 'logs'
            self.log_dir.mkdir(exist_ok=True)
            self.initialized = True
    
    def get_logger(
        self,
        name: str,
        level: int = logging.INFO,
        log_to_file: bool = True,
        log_to_console: bool = True,
        json_format: bool = False
    ) -> logging.Logger:
        """
        Get or create a logger with specified configuration
        
        Args:
            name: Logger name
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_file: Enable file logging
            log_to_console: Enable console logging
            json_format: Use JSON format for structured logging
        
        Returns:
            Configured logger instance
        """
        if name in self.loggers:
            return self.loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.propagate = False
        
        # Remove existing handlers
        logger.handlers.clear()
        
        # Console handler
        if log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_handler.setFormatter(StructuredFormatter(include_json=False))
            logger.addHandler(console_handler)
        
        # File handler with rotation
        if log_to_file:
            # Regular log file (human-readable)
            log_file = self.log_dir / f"{name}.log"
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(StructuredFormatter(include_json=False))
            logger.addHandler(file_handler)
            
            # JSON log file (for parsing/analysis)
            if json_format:
                json_log_file = self.log_dir / f"{name}.json.log"
                json_handler = logging.handlers.RotatingFileHandler(
                    json_log_file,
                    maxBytes=10 * 1024 * 1024,
                    backupCount=3,
                    encoding='utf-8'
                )
                json_handler.setLevel(level)
                json_handler.setFormatter(StructuredFormatter(include_json=True))
                logger.addHandler(json_handler)
        
        self.loggers[name] = logger
        return logger
    
    def set_level(self, name: str, level: int):
        """Change logging level for a logger"""
        if name in self.loggers:
            self.loggers[name].setLevel(level)
            for handler in self.loggers[name].handlers:
                handler.setLevel(level)
    
    def cleanup_old_logs(self, days: int = 7):
        """Remove log files older than specified days"""
        import time
        current_time = time.time()
        max_age = days * 24 * 60 * 60
        
        for log_file in self.log_dir.glob('*.log*'):
            if log_file.is_file():
                file_age = current_time - log_file.stat().st_mtime
                if file_age > max_age:
                    try:
                        log_file.unlink()
                        print(f"Removed old log file: {log_file.name}")
                    except Exception as e:
                        print(f"Failed to remove {log_file.name}: {e}")


# Global logger manager instance
logger_manager = LoggerManager()


def get_logger(name: str, level: int = logging.INFO, **kwargs) -> logging.Logger:
    """Convenience function to get a logger"""
    return logger_manager.get_logger(name, level, **kwargs)


class LogContext:
    """Context manager for adding extra context to logs"""
    
    def __init__(self, logger: logging.Logger, **context):
        self.logger = logger
        self.context = context
        self.old_factory = None
    
    def __enter__(self):
        self.old_factory = logging.getLogRecordFactory()
        
        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            record.extra_data = self.context
            return record
        
        logging.setLogRecordFactory(record_factory)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.old_factory:
            logging.setLogRecordFactory(self.old_factory)


def log_exception(logger: logging.Logger, exception: Exception, extra_context: Optional[Dict[str, Any]] = None):
    """
    Log an exception with full context
    
    Args:
        logger: Logger instance
        exception: Exception to log
        extra_context: Additional context information
    """
    error_info = {
        'exception_type': type(exception).__name__,
        'exception_message': str(exception),
        'extra_context': extra_context or {}
    }
    
    logger.error(f"Exception occurred: {error_info}", exc_info=True)


def log_performance(logger: logging.Logger, operation: str, duration: float, **metrics):
    """
    Log performance metrics
    
    Args:
        logger: Logger instance
        operation: Operation name
        duration: Duration in seconds
        **metrics: Additional metrics
    """
    perf_data = {
        'operation': operation,
        'duration_seconds': round(duration, 4),
        **metrics
    }
    
    logger.info(f"Performance: {operation} completed in {duration:.4f}s", extra={'extra_data': perf_data})


# Cleanup old logs on module import
logger_manager.cleanup_old_logs(days=7)


# Example usage
if __name__ == '__main__':
    # Create test logger
    test_logger = get_logger('test', level=logging.DEBUG, json_format=True)
    
    test_logger.debug("This is a debug message")
    test_logger.info("This is an info message")
    test_logger.warning("This is a warning message")
    test_logger.error("This is an error message")
    
    # Test context logging
    with LogContext(test_logger, user_id=123, operation='test_op'):
        test_logger.info("Message with context")
    
    # Test exception logging
    try:
        raise ValueError("Test exception")
    except Exception as e:
        log_exception(test_logger, e, extra_context={'step': 'testing'})
    
    # Test performance logging
    import time
    start = time.time()
    time.sleep(0.1)
    log_performance(test_logger, 'test_operation', time.time() - start, records_processed=100)
    
    print(f"\nLogs written to: {logger_manager.log_dir}")
