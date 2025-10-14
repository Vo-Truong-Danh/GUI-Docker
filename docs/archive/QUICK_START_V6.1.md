# 🚀 QUICK START GUIDE - V6.1.0

**Hướng dẫn nhanh sử dụng các tính năng mới**

---

## 📦 CÀI ĐẶT NHANH

```bash
# 1. Update dependencies
cd run_spark_gui
pip install --upgrade -r requirements.txt

# 2. Install optional testing tools
pip install pytest pytest-cov

# 3. Verify installation
python security_validator.py
python performance_optimizer_advanced.py
python constants.py

# 4. Run tests
pytest test_suite.py -v
```

---

## 🔐 BẢO MẬT (Security Validator)

### Import
```python
from security_validator import SecurityValidator, ensure_safe_path, ensure_safe_container_name
```

### Validate Container Name
```python
# Method 1: Check and handle
is_valid, error = SecurityValidator.validate_container_name('spark-worker')
if not is_valid:
    print(f"Invalid: {error}")

# Method 2: Raise exception if invalid (recommended)
container = ensure_safe_container_name(user_input)
```

### Validate Path (with traversal protection)
```python
# Validate within base directory
path = ensure_safe_path('/tmp/file.txt', base_dir='/tmp')

# Or check manually
is_valid, error = SecurityValidator.validate_path(
    path='/tmp/file.txt',
    base_dir='/tmp',
    must_exist=True
)
```

### Sanitize Input
```python
# Remove dangerous characters
clean = SecurityValidator.sanitize_string(user_input, max_length=1000)

# Generate safe filename
safe_name = SecurityValidator.generate_safe_filename(user_filename)
```

### Validate Command
```python
is_valid, error = SecurityValidator.validate_command('ls -la')
if not is_valid:
    print(f"Dangerous command: {error}")
```

---

## ⚡ HIỆU SUẤT (Performance Optimizer)

### Advanced Caching
```python
from performance_optimizer_advanced import cached, AdvancedCache

# Decorator (easiest)
@cached(ttl=300)  # Cache 5 minutes
def expensive_function(param):
    # Your expensive code
    return result

# Manual cache
cache = AdvancedCache(max_size=1000, default_ttl=3600)
cache.set('key', value, ttl=600)
result = cache.get('key')

# Cache stats
stats = cache.get_stats()
print(f"Hit rate: {stats['hit_rate']}")
```

### Connection Pooling
```python
from performance_optimizer_advanced import ConnectionPool

# Create pool
def create_db_connection():
    return sqlite3.connect('database.db')

pool = ConnectionPool(
    factory=create_db_connection,
    max_size=5,
    validate=lambda conn: conn is not None
)

# Use connection
conn = pool.acquire()
try:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM table")
    results = cursor.fetchall()
finally:
    pool.release(conn)
```

### Background Tasks
```python
from performance_optimizer_advanced import (
    background_task, 
    start_background_workers,
    get_task_queue_stats
)

# Start workers (do this once at startup)
start_background_workers()

# Define background task
@background_task
def slow_operation():
    time.sleep(10)
    print("Done!")

# Execute (non-blocking)
slow_operation()

# Check stats
stats = get_task_queue_stats()
print(f"Pending: {stats['pending']}, Completed: {stats['completed']}")
```

### Memory Optimization
```python
from performance_optimizer_advanced import MemoryOptimizer

# Check memory usage
mem_bytes = MemoryOptimizer.get_memory_usage()
print(f"Memory: {mem_bytes / 1024 / 1024:.2f} MB")

# Optimize dictionary (remove None, empty strings)
data = {'a': 1, 'b': None, 'c': '', 'd': 2}
optimized = MemoryOptimizer.optimize_dict(data)
# Result: {'a': 1, 'd': 2}

# Force garbage collection
MemoryOptimizer.force_garbage_collection()
```

### Rate Limiting
```python
from performance_optimizer_advanced import TokenBucketRateLimiter

# Create limiter (2 requests per second, max 5 in bucket)
limiter = TokenBucketRateLimiter(rate=2.0, capacity=5)

# Check if allowed
if limiter.acquire(tokens=1, timeout=1.0):
    # Process request
    process_request()
else:
    print("Rate limit exceeded")
```

---

## 📏 CONSTANTS

### Import và Sử dụng
```python
from constants import (
    DOCKER_COMMAND_TIMEOUT,
    SPARK_SUBMIT_TIMEOUT,
    MAX_RETRY_ATTEMPTS,
    DEFAULT_CONTAINER,
    get_timeout,
    is_valid_port
)

# Use constants instead of magic numbers
timeout = DOCKER_COMMAND_TIMEOUT  # Instead of timeout = 30

# Get timeout by operation name
timeout = get_timeout('spark_submit')

# Validate port
if is_valid_port(8080):
    print("Valid port")
```

### Common Constants
```python
# Timeouts (seconds)
DOCKER_COMMAND_TIMEOUT = 30
SPARK_SUBMIT_TIMEOUT = 300
HDFS_PUT_TIMEOUT = 120

# Retry
MAX_RETRY_ATTEMPTS = 3
RETRY_BACKOFF_BASE = 0.1

# Limits
MAX_HISTORY_SIZE = 10
MAX_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# Defaults
DEFAULT_CONTAINER = 'spark-worker'
DEFAULT_MASTER = 'spark://spark-master:7077'
```

---

## 🧪 TESTING

### Run Tests
```bash
# All tests
pytest test_suite.py -v

# Specific test class
pytest test_suite.py::TestSecurityValidator -v

# With coverage
pytest test_suite.py --cov=. --cov-report=html

# Performance tests only
pytest test_suite.py::TestPerformance -v
```

### Write Custom Tests
```python
import pytest

class TestMyFeature:
    def test_basic(self):
        result = my_function('input')
        assert result == 'expected'
    
    def test_error(self):
        with pytest.raises(ValueError):
            my_function('invalid')
```

---

## 🔍 EXCEPTION HANDLING

### Pattern Cũ (Tránh)
```python
# ❌ BAD - Too broad
try:
    operation()
except Exception as e:
    print(f"Error: {e}")
    
# ❌ BAD - Bare except
try:
    operation()
except:
    pass
```

### Pattern Mới (Khuyến nghị)
```python
# ✅ GOOD - Specific exceptions
try:
    operation()
except FileNotFoundError as e:
    logger.error(f"File not found: {e}")
    # Handle file not found
except PermissionError as e:
    logger.error(f"Permission denied: {e}")
    # Handle permission error
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    # Handle invalid input
except Exception as e:
    # Unexpected errors with full logging
    logger.error(f"Unexpected: {type(e).__name__}: {e}", exc_info=True)
    raise  # Re-raise after logging
```

---

## 📊 MONITORING

### Cache Statistics
```python
from performance_optimizer_advanced import get_cache_stats, cleanup_expired_cache

# Get stats
stats = get_cache_stats()
print(f"Cache size: {stats['size']}/{stats['max_size']}")
print(f"Hit rate: {stats['hit_rate']}")
print(f"Evictions: {stats['evictions']}")

# Cleanup expired entries
cleanup_expired_cache()
```

### Task Queue Statistics
```python
from performance_optimizer_advanced import get_task_queue_stats

stats = get_task_queue_stats()
print(f"Pending: {stats['pending']}")
print(f"Completed: {stats['completed']}")
print(f"Failed: {stats['failed']}")
print(f"Workers: {stats['workers']}")
```

### Memory Usage
```python
from performance_optimizer_advanced import MemoryOptimizer

mem = MemoryOptimizer.get_memory_usage()
print(f"Memory usage: {mem / 1024 / 1024:.2f} MB")
```

---

## 🎯 INTEGRATION EXAMPLES

### Secure File Copy
```python
from security_validator import ensure_safe_path, ensure_safe_container_name
from constants import DOCKER_COPY_TIMEOUT

def copy_file_secure(filepath, container):
    """Copy file with validation"""
    try:
        # Validate inputs
        safe_path = ensure_safe_path(filepath, must_exist=True)
        safe_container = ensure_safe_container_name(container)
        
        # Execute copy with timeout
        cmd = ['docker', 'cp', safe_path, f'{safe_container}:/tmp']
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=DOCKER_COPY_TIMEOUT
        )
        
        return result.returncode == 0
        
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return False
    except SecurityValidationError as e:
        print(f"Security validation failed: {e}")
        return False
    except subprocess.TimeoutExpired:
        print(f"Copy timed out after {DOCKER_COPY_TIMEOUT}s")
        return False
```

### Cached Database Query
```python
from performance_optimizer_advanced import cached, ConnectionPool

# Setup connection pool
db_pool = ConnectionPool(
    factory=lambda: sqlite3.connect('app.db'),
    max_size=5
)

@cached(ttl=300)  # Cache for 5 minutes
def get_user_data(user_id):
    """Get user data with caching and pooling"""
    conn = db_pool.acquire()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return cursor.fetchone()
    finally:
        db_pool.release(conn)
```

### Background Log Processing
```python
from performance_optimizer_advanced import background_task

@background_task
def process_logs():
    """Process logs in background"""
    logs = read_logs()
    analyze_logs(logs)
    cleanup_old_logs()

# Execute without blocking
process_logs()
```

---

## 🐛 DEBUGGING & TROUBLESHOOTING

### Common Issues

**1. Import Error**
```bash
# Make sure you're in the right directory
cd run_spark_gui
python security_validator.py  # Should work
```

**2. pytest not found**
```bash
pip install pytest pytest-cov
```

**3. Tests failing**
```bash
# Check Python version (need 3.7+)
python --version

# Check dependencies
pip list

# Run with verbose output
pytest test_suite.py -v -s
```

---

## 📚 DOCUMENTATION LINKS

- 📄 **SYSTEM_ANALYSIS_REPORT.md** - Phân tích hệ thống chi tiết
- 📄 **IMPLEMENTATION_GUIDE_V6.1.md** - Hướng dẫn triển khai đầy đủ
- 📄 **OPTIMIZATION_COMPLETION_REPORT.md** - Báo cáo hoàn thành
- 🔐 **security_validator.py** - Source code với docstrings
- ⚡ **performance_optimizer_advanced.py** - Source code với docstrings
- 🧪 **test_suite.py** - Test examples

---

## ✅ CHECKLIST BẮT ĐẦU

- [ ] Đọc OPTIMIZATION_COMPLETION_REPORT.md
- [ ] Cài đặt dependencies: `pip install -r requirements.txt`
- [ ] Test modules: `python security_validator.py`
- [ ] Run test suite: `pytest test_suite.py -v`
- [ ] Đọc IMPLEMENTATION_GUIDE_V6.1.md
- [ ] Tích hợp security_validator vào code
- [ ] Thêm caching cho operations đắt
- [ ] Start background workers nếu cần
- [ ] Monitor performance metrics

---

## 🎯 TIP PRO

**Security:**
- Always validate user inputs
- Use ensure_safe_* functions
- Never trust external data

**Performance:**
- Cache expensive operations
- Use connection pooling
- Move slow tasks to background
- Monitor metrics regularly

**Testing:**
- Write tests as you code
- Run tests before commit
- Maintain coverage >80%

**Code Quality:**
- Use constants instead of magic numbers
- Specific exceptions > generic
- Add type hints
- Write docstrings

---

**Version:** 6.1.0  
**Last Updated:** 13/10/2025  
**Status:** Production Ready ✅
