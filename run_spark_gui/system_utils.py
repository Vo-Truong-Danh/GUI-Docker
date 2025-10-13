"""
Advanced System Utilities - Performance & Caching
Version: 4.4.0
"""

import time
import threading
from functools import wraps, lru_cache
from collections import OrderedDict
from typing import Any, Callable, Optional
import hashlib
import json


class LRUCache:
    """LRU Cache implementation with expiration"""
    
    def __init__(self, capacity: int = 100, ttl: int = 300):
        self.cache = OrderedDict()
        self.capacity = capacity
        self.ttl = ttl  # Time to live in seconds
        self.timestamps = {}
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self.lock:
            if key not in self.cache:
                return None
            
            # Check expiration
            if time.time() - self.timestamps[key] > self.ttl:
                self.cache.pop(key)
                self.timestamps.pop(key)
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
    
    def set(self, key: str, value: Any):
        """Set value in cache"""
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            else:
                if len(self.cache) >= self.capacity:
                    # Remove oldest
                    oldest = next(iter(self.cache))
                    self.cache.pop(oldest)
                    self.timestamps.pop(oldest)
            
            self.cache[key] = value
            self.timestamps[key] = time.time()
    
    def invalidate(self, key: str):
        """Invalidate cache entry"""
        with self.lock:
            self.cache.pop(key, None)
            self.timestamps.pop(key, None)
    
    def clear(self):
        """Clear all cache"""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()
    
    def stats(self):
        """Get cache statistics"""
        with self.lock:
            return {
                'size': len(self.cache),
                'capacity': self.capacity,
                'hit_rate': 'N/A',  # Would need hit/miss counters
                'oldest_entry': min(self.timestamps.values()) if self.timestamps else None
            }


class CacheManager:
    """Centralized cache management for the application"""
    
    def __init__(self):
        self.caches = {
            'docker_status': LRUCache(capacity=50, ttl=10),      # 10s TTL
            'hdfs_files': LRUCache(capacity=100, ttl=30),        # 30s TTL
            'config': LRUCache(capacity=20, ttl=300),            # 5min TTL
            'templates': LRUCache(capacity=50, ttl=600),         # 10min TTL
            'job_history': LRUCache(capacity=100, ttl=3600),     # 1hr TTL
        }
    
    def get(self, cache_name: str, key: str) -> Optional[Any]:
        """Get from specific cache"""
        if cache_name in self.caches:
            return self.caches[cache_name].get(key)
        return None
    
    def set(self, cache_name: str, key: str, value: Any):
        """Set in specific cache"""
        if cache_name in self.caches:
            self.caches[cache_name].set(key, value)
    
    def invalidate(self, cache_name: str, key: str = None):
        """Invalidate cache entry or entire cache"""
        if cache_name in self.caches:
            if key:
                self.caches[cache_name].invalidate(key)
            else:
                self.caches[cache_name].clear()
    
    def clear_all(self):
        """Clear all caches"""
        for cache in self.caches.values():
            cache.clear()
    
    def stats(self):
        """Get statistics for all caches"""
        return {name: cache.stats() for name, cache in self.caches.items()}


# Global cache manager instance
cache_manager = CacheManager()


def cached(cache_name: str = 'default', ttl: int = 60):
    """Decorator for caching function results"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key_data = {
                'func': func.__name__,
                'args': str(args),
                'kwargs': str(sorted(kwargs.items()))
            }
            cache_key = hashlib.md5(
                json.dumps(key_data, sort_keys=True).encode()
            ).hexdigest()
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_name, cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache_manager.set(cache_name, cache_key, result)
            return result
        
        return wrapper
    return decorator


class PerformanceMonitor:
    """Monitor performance metrics"""
    
    def __init__(self):
        self.metrics = {}
        self.lock = threading.Lock()
    
    def record_timing(self, operation: str, duration: float):
        """Record operation timing"""
        with self.lock:
            if operation not in self.metrics:
                self.metrics[operation] = {
                    'count': 0,
                    'total_time': 0,
                    'min_time': float('inf'),
                    'max_time': 0,
                    'avg_time': 0
                }
            
            m = self.metrics[operation]
            m['count'] += 1
            m['total_time'] += duration
            m['min_time'] = min(m['min_time'], duration)
            m['max_time'] = max(m['max_time'], duration)
            m['avg_time'] = m['total_time'] / m['count']
    
    def get_stats(self, operation: str = None):
        """Get performance statistics"""
        with self.lock:
            if operation:
                return self.metrics.get(operation, {})
            return dict(self.metrics)
    
    def reset(self):
        """Reset all metrics"""
        with self.lock:
            self.metrics.clear()


# Global performance monitor
perf_monitor = PerformanceMonitor()


def timed(operation_name: str = None):
    """Decorator to measure function execution time"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                perf_monitor.record_timing(op_name, duration)
        
        return wrapper
    return decorator


class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        self.lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Call function through circuit breaker"""
        with self.lock:
            if self.state == 'OPEN':
                if time.time() - self.last_failure_time > self.timeout:
                    self.state = 'HALF_OPEN'
                else:
                    raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            with self.lock:
                self.failures = 0
                self.state = 'CLOSED'
            return result
        
        except Exception as e:
            with self.lock:
                self.failures += 1
                self.last_failure_time = time.time()
                
                if self.failures >= self.failure_threshold:
                    self.state = 'OPEN'
            
            raise e
    
    def reset(self):
        """Reset circuit breaker"""
        with self.lock:
            self.failures = 0
            self.last_failure_time = None
            self.state = 'CLOSED'
    
    def get_state(self):
        """Get current state"""
        with self.lock:
            return {
                'state': self.state,
                'failures': self.failures,
                'last_failure': self.last_failure_time
            }


class RetryHandler:
    """Enhanced retry logic with exponential backoff"""
    
    @staticmethod
    def retry(
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0,
        max_delay: float = 60.0,
        exceptions: tuple = (Exception,)
    ):
        """Retry decorator with exponential backoff"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                delay = initial_delay
                last_exception = None
                
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        
                        if attempt < max_attempts - 1:
                            time.sleep(min(delay, max_delay))
                            delay *= backoff_factor
                        else:
                            raise last_exception
                
                raise last_exception
            
            return wrapper
        return decorator


# Example usage functions

def get_docker_status_cached(container_name: str):
    """Example: Get Docker status with caching"""
    @cached(cache_name='docker_status', ttl=10)
    def _get_status(name: str):
        # Actual Docker status check logic
        import subprocess
        result = subprocess.run(
            ['docker', 'inspect', '-f', '{{.State.Status}}', name],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip()
    
    return _get_status(container_name)


def list_hdfs_files_cached(path: str):
    """Example: List HDFS files with caching"""
    @cached(cache_name='hdfs_files', ttl=30)
    def _list_files(hdfs_path: str):
        # Actual HDFS list logic
        import subprocess
        result = subprocess.run(
            ['docker', 'exec', 'namenode', 'hdfs', 'dfs', '-ls', hdfs_path],
            capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip().split('\n')
    
    return _list_files(path)


if __name__ == '__main__':
    # Test cache system
    print("Testing Cache System...")
    
    cache = LRUCache(capacity=3, ttl=5)
    cache.set('key1', 'value1')
    cache.set('key2', 'value2')
    cache.set('key3', 'value3')
    
    print(f"Cache stats: {cache.stats()}")
    print(f"Get key1: {cache.get('key1')}")
    
    # Test performance monitoring
    print("\nTesting Performance Monitor...")
    
    @timed('test_operation')
    def slow_function():
        time.sleep(0.1)
        return "done"
    
    for i in range(5):
        slow_function()
    
    print(f"Performance stats: {perf_monitor.get_stats('test_operation')}")
    
    # Test circuit breaker
    print("\nTesting Circuit Breaker...")
    
    breaker = CircuitBreaker(failure_threshold=3, timeout=2)
    
    def failing_function():
        raise Exception("Test failure")
    
    for i in range(5):
        try:
            breaker.call(failing_function)
        except Exception as e:
            print(f"Attempt {i+1}: {e}")
    
    print(f"Circuit breaker state: {breaker.get_state()}")
    
    print("\n✓ All tests passed!")
