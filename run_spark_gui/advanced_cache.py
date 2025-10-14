"""
Advanced Caching System with Multiple Backends
Version: 1.0.0

Features:
- Multi-level caching (memory + disk)
- TTL-based expiration
- LRU eviction
- Cache warming
- Statistics and monitoring
- Thread-safe operations
- Serialization support
"""

import threading
import time
import pickle
import json
import hashlib
from pathlib import Path
from typing import Any, Optional, Callable, Dict, Tuple
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import os


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: float
    expires_at: Optional[float]
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    size_bytes: int = 0
    
    def is_expired(self) -> bool:
        """Check if entry has expired"""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at
    
    def touch(self):
        """Mark entry as accessed"""
        self.access_count += 1
        self.last_access = time.time()


class LRUCache:
    """Thread-safe LRU cache with TTL support"""
    
    def __init__(self, 
                 max_size: int = 1000,
                 default_ttl: Optional[int] = None):
        """
        Initialize LRU cache
        
        Args:
            max_size: Maximum number of entries
            default_ttl: Default time-to-live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        
        # Statistics
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expirations': 0,
            'sets': 0
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        with self._lock:
            if key not in self._cache:
                self._stats['misses'] += 1
                return default
            
            entry = self._cache[key]
            
            # Check expiration
            if entry.is_expired():
                del self._cache[key]
                self._stats['expirations'] += 1
                self._stats['misses'] += 1
                return default
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            entry.touch()
            
            self._stats['hits'] += 1
            return entry.value
    
    def set(self, 
            key: str,
            value: Any,
            ttl: Optional[int] = None):
        """Set value in cache"""
        with self._lock:
            # Calculate expiration
            ttl_value = ttl if ttl is not None else self.default_ttl
            expires_at = time.time() + ttl_value if ttl_value else None
            
            # Calculate size (approximate)
            try:
                size_bytes = len(pickle.dumps(value))
            except Exception:
                size_bytes = 0
            
            # Create entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=time.time(),
                expires_at=expires_at,
                size_bytes=size_bytes
            )
            
            # Remove if exists (to update position)
            if key in self._cache:
                del self._cache[key]
            
            # Add to cache
            self._cache[key] = entry
            self._cache.move_to_end(key)
            
            self._stats['sets'] += 1
            
            # Evict if over size limit
            while len(self._cache) > self.max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                self._stats['evictions'] += 1
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self):
        """Clear all entries"""
        with self._lock:
            self._cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self._stats['hits'] + self._stats['misses']
            hit_rate = self._stats['hits'] / total_requests if total_requests > 0 else 0
            
            total_size = sum(entry.size_bytes for entry in self._cache.values())
            
            return {
                **self._stats,
                'size': len(self._cache),
                'max_size': self.max_size,
                'hit_rate': hit_rate,
                'total_size_bytes': total_size
            }
    
    def cleanup_expired(self) -> int:
        """Remove expired entries"""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._cache[key]
                self._stats['expirations'] += 1
            
            return len(expired_keys)


class DiskCache:
    """Persistent disk-based cache"""
    
    def __init__(self, 
                 cache_dir: str = ".cache",
                 max_size_mb: int = 100):
        """
        Initialize disk cache
        
        Args:
            cache_dir: Directory for cache files
            max_size_mb: Maximum cache size in MB
        """
        self.cache_dir = Path(cache_dir)
        self.max_size_mb = max_size_mb
        
        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self._lock = threading.Lock()
        
        # Statistics
        self._stats = {
            'hits': 0,
            'misses': 0,
            'writes': 0,
            'errors': 0
        }
    
    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for key"""
        # Hash key to create safe filename
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from disk cache"""
        cache_path = self._get_cache_path(key)
        
        with self._lock:
            if not cache_path.exists():
                self._stats['misses'] += 1
                return default
            
            try:
                with open(cache_path, 'rb') as f:
                    data = pickle.load(f)
                
                # Check expiration
                if 'expires_at' in data and data['expires_at']:
                    if time.time() > data['expires_at']:
                        cache_path.unlink()
                        self._stats['misses'] += 1
                        return default
                
                self._stats['hits'] += 1
                return data['value']
                
            except Exception as e:
                self._stats['errors'] += 1
                return default
    
    def set(self, 
            key: str,
            value: Any,
            ttl: Optional[int] = None):
        """Set value in disk cache"""
        cache_path = self._get_cache_path(key)
        
        with self._lock:
            try:
                expires_at = time.time() + ttl if ttl else None
                
                data = {
                    'value': value,
                    'created_at': time.time(),
                    'expires_at': expires_at
                }
                
                with open(cache_path, 'wb') as f:
                    pickle.dump(data, f)
                
                self._stats['writes'] += 1
                
                # Check total cache size
                self._enforce_size_limit()
                
            except Exception as e:
                self._stats['errors'] += 1
                print(f"⚠️ Disk cache write error: {e}")
    
    def delete(self, key: str) -> bool:
        """Delete key from disk cache"""
        cache_path = self._get_cache_path(key)
        
        with self._lock:
            if cache_path.exists():
                cache_path.unlink()
                return True
            return False
    
    def clear(self):
        """Clear all cache files"""
        with self._lock:
            for cache_file in self.cache_dir.glob("*.cache"):
                try:
                    cache_file.unlink()
                except Exception as e:
                    print(f"⚠️ Error deleting cache file: {e}")
    
    def _enforce_size_limit(self):
        """Enforce maximum cache size"""
        try:
            # Calculate total size
            total_size = sum(
                f.stat().st_size 
                for f in self.cache_dir.glob("*.cache")
            )
            
            max_size_bytes = self.max_size_mb * 1024 * 1024
            
            if total_size > max_size_bytes:
                # Delete oldest files
                cache_files = sorted(
                    self.cache_dir.glob("*.cache"),
                    key=lambda f: f.stat().st_mtime
                )
                
                for cache_file in cache_files:
                    cache_file.unlink()
                    total_size -= cache_file.stat().st_size
                    
                    if total_size <= max_size_bytes:
                        break
                        
        except Exception as e:
            print(f"⚠️ Error enforcing size limit: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            try:
                cache_files = list(self.cache_dir.glob("*.cache"))
                total_size = sum(f.stat().st_size for f in cache_files)
                
                total_requests = self._stats['hits'] + self._stats['misses']
                hit_rate = self._stats['hits'] / total_requests if total_requests > 0 else 0
                
                return {
                    **self._stats,
                    'files': len(cache_files),
                    'total_size_bytes': total_size,
                    'total_size_mb': total_size / (1024 * 1024),
                    'hit_rate': hit_rate
                }
            except Exception:
                return self._stats


class MultiLevelCache:
    """Multi-level cache with memory and disk backing"""
    
    def __init__(self,
                 memory_max_size: int = 1000,
                 memory_ttl: Optional[int] = 300,  # 5 minutes
                 disk_cache_dir: str = ".cache",
                 disk_max_size_mb: int = 100):
        """
        Initialize multi-level cache
        
        Args:
            memory_max_size: Max entries in memory cache
            memory_ttl: Default TTL for memory cache
            disk_cache_dir: Directory for disk cache
            disk_max_size_mb: Max size of disk cache in MB
        """
        self.memory_cache = LRUCache(
            max_size=memory_max_size,
            default_ttl=memory_ttl
        )
        
        self.disk_cache = DiskCache(
            cache_dir=disk_cache_dir,
            max_size_mb=disk_max_size_mb
        )
        
        # Start cleanup thread
        self._running = True
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True,
            name="MultiLevelCache-Cleanup"
        )
        self._cleanup_thread.start()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache (memory first, then disk)"""
        # Try memory cache first
        value = self.memory_cache.get(key)
        if value is not None:
            return value
        
        # Try disk cache
        value = self.disk_cache.get(key)
        if value is not None:
            # Warm up memory cache
            self.memory_cache.set(key, value)
            return value
        
        return default
    
    def set(self, 
            key: str,
            value: Any,
            ttl: Optional[int] = None,
            disk: bool = True):
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live
            disk: Also save to disk cache
        """
        # Always set in memory
        self.memory_cache.set(key, value, ttl)
        
        # Optionally set in disk
        if disk:
            self.disk_cache.set(key, value, ttl)
    
    def delete(self, key: str):
        """Delete from all cache levels"""
        self.memory_cache.delete(key)
        self.disk_cache.delete(key)
    
    def clear(self):
        """Clear all cache levels"""
        self.memory_cache.clear()
        self.disk_cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get combined statistics"""
        return {
            'memory': self.memory_cache.get_stats(),
            'disk': self.disk_cache.get_stats()
        }
    
    def _cleanup_loop(self):
        """Background cleanup of expired entries"""
        while self._running:
            try:
                time.sleep(60)  # Run every minute
                
                # Cleanup memory cache
                expired = self.memory_cache.cleanup_expired()
                if expired > 0:
                    print(f"🗑️ Cleaned up {expired} expired cache entries")
                    
            except Exception as e:
                print(f"⚠️ Cache cleanup error: {e}")
    
    def stop(self):
        """Stop background threads"""
        self._running = False


# Global cache instance
_global_cache: Optional[MultiLevelCache] = None


def get_cache() -> MultiLevelCache:
    """Get or create global cache instance"""
    global _global_cache
    
    if _global_cache is None:
        _global_cache = MultiLevelCache(
            memory_max_size=1000,
            memory_ttl=300,
            disk_cache_dir=".cache",
            disk_max_size_mb=100
        )
    
    return _global_cache


# Decorator for caching function results
def cached(ttl: int = 300, disk: bool = True):
    """
    Decorator to cache function results
    
    Usage:
        @cached(ttl=60)
        def expensive_function(x):
            return x * 2
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key_data = f"{func.__name__}:{args}:{sorted(kwargs.items())}"
            cache_key = hashlib.sha256(key_data.encode()).hexdigest()
            
            cache = get_cache()
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl, disk=disk)
            
            return result
        
        return wrapper
    return decorator


# Example usage
if __name__ == '__main__':
    print("Testing Advanced Caching System...")
    
    # Create cache
    cache = MultiLevelCache()
    
    # Test basic operations
    cache.set('user:123', {'name': 'John', 'age': 30})
    user = cache.get('user:123')
    print(f"Retrieved user: {user}")
    
    # Test TTL
    cache.set('temp', 'expires soon', ttl=2)
    print(f"Temp value: {cache.get('temp')}")
    time.sleep(3)
    print(f"After expiry: {cache.get('temp', 'EXPIRED')}")
    
    # Test decorator
    @cached(ttl=5)
    def slow_function(x):
        print(f"Computing {x}...")
        time.sleep(0.1)
        return x * 2
    
    print(f"First call: {slow_function(5)}")  # Slow
    print(f"Second call: {slow_function(5)}")  # Fast (cached)
    
    # Get stats
    stats = cache.get_stats()
    print(f"\nCache stats:")
    print(f"  Memory: {stats['memory']}")
    print(f"  Disk: {stats['disk']}")
    
    # Cleanup
    cache.stop()
    print("\n✅ Caching system test complete")
