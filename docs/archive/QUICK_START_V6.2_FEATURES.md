# 🚀 QUICK START GUIDE - New Features V6.2.0

## 📋 Tổng quan

Version 6.2.0 đã thêm 3 modules mới quan trọng để cải thiện độ tin cậy và hiệu suất của hệ thống:

1. **`resource_cleanup.py`** - Quản lý tài nguyên tự động
2. **`error_recovery_v2.py`** - Xử lý lỗi thông minh
3. **`connection_pool_v2.py`** - Connection pooling nâng cao

---

## 1️⃣ Resource Cleanup - Quản lý Tài nguyên

### 🎯 Mục đích:
- Tự động theo dõi và dọn dẹp resources (files, sockets, processes)
- Ngăn chặn resource leaks
- Cleanup tự động khi app thoát

### 📝 Sử dụng cơ bản:

#### A. Context Manager cho Files:
```python
from resource_cleanup import managed_file

# Tự động đóng file ngay cả khi có exception
with managed_file('data.txt', 'r') as f:
    content = f.read()
    # Xử lý data...
# ✅ File tự động đóng ở đây
```

#### B. Context Manager cho Processes:
```python
from resource_cleanup import managed_process
import subprocess

proc = subprocess.Popen(['python', 'long_script.py'])
with managed_process(proc) as p:
    output, error = p.communicate(timeout=60)
# ✅ Process tự động terminate nếu timeout hoặc exception
```

#### C. Context Manager cho Sockets:
```python
from resource_cleanup import managed_socket
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
with managed_socket(sock) as s:
    s.connect(('localhost', 8080))
    s.send(b'Hello')
# ✅ Socket tự động đóng
```

#### D. Xem Resource Statistics:
```python
from resource_cleanup import get_resource_registry

# Lấy thống kê
registry = get_resource_registry()
stats = registry.get_stats()

print(f"Total resources tracked: {stats['total_registered']}")
print(f"Total cleaned: {stats['total_cleaned']}")

# Chi tiết theo loại
for resource_type, type_stats in stats['by_type'].items():
    print(f"{resource_type}:")
    print(f"  - Alive: {type_stats['alive']}")
    print(f"  - GC collected: {type_stats['gc_collected']}")
```

#### E. Manual Registration (Advanced):
```python
from resource_cleanup import get_resource_registry

registry = get_resource_registry()

# Register một resource với custom cleanup
my_resource = create_custom_resource()
resource_id = registry.register_resource(
    my_resource, 
    'custom',
    cleanup_func=lambda res: res.shutdown()
)

# Sử dụng resource...

# Manual cleanup (optional)
registry.unregister_resource(my_resource, 'custom')
```

### ⚠️ Lưu ý:
- Cleanup tự động chạy khi app exit (atexit)
- Signal handlers đã được đăng ký (SIGINT, SIGTERM)
- Sử dụng weak references để tránh circular dependencies

---

## 2️⃣ Error Recovery - Xử lý Lỗi Thông minh

### 🎯 Mục đích:
- Tự động retry cho transient errors
- Circuit breaker ngăn cascading failures
- Phân loại và xử lý lỗi thông minh

### 📝 Sử dụng cơ bản:

#### A. Retry Decorator:
```python
from error_recovery_v2 import retry, RetryStrategy

# Retry với exponential backoff
@retry(max_attempts=3, strategy=RetryStrategy.EXPONENTIAL, base_delay=1.0)
def unstable_network_call():
    """Tự động retry nếu có network/timeout error"""
    response = requests.get('https://api.example.com/data')
    return response.json()

# Sử dụng
try:
    data = unstable_network_call()
    print(f"Success: {data}")
except Exception as e:
    print(f"Failed after 3 attempts: {e}")
```

#### B. Các Retry Strategies:
```python
from error_recovery_v2 import retry, RetryStrategy

# 1. Exponential backoff: 1s, 2s, 4s, 8s...
@retry(max_attempts=5, strategy=RetryStrategy.EXPONENTIAL)
def func1(): ...

# 2. Linear backoff: 1s, 2s, 3s, 4s...
@retry(max_attempts=5, strategy=RetryStrategy.LINEAR)
def func2(): ...

# 3. Fibonacci backoff: 1s, 1s, 2s, 3s, 5s...
@retry(max_attempts=5, strategy=RetryStrategy.FIBONACCI)
def func3(): ...

# 4. Fixed delay: 1s, 1s, 1s, 1s...
@retry(max_attempts=5, strategy=RetryStrategy.FIXED, base_delay=1.0)
def func4(): ...
```

#### C. Custom Retry Callback:
```python
from error_recovery_v2 import retry

def on_retry_callback(attempt, error, delay):
    """Được gọi mỗi khi retry"""
    print(f"Attempt {attempt+1} failed: {error}")
    print(f"Waiting {delay}s before retry...")
    # Ghi log, send metrics, etc.

@retry(max_attempts=3, on_retry=on_retry_callback)
def my_function():
    # Your code here
    pass
```

#### D. Circuit Breaker:
```python
from error_recovery_v2 import CircuitBreaker

# Tạo circuit breaker
breaker = CircuitBreaker(
    failure_threshold=5,    # Mở circuit sau 5 lỗi
    success_threshold=2,    # Đóng circuit sau 2 thành công
    timeout=60.0           # Thử lại sau 60s
)

# Sử dụng
try:
    result = breaker.call(risky_operation, arg1, arg2)
except RuntimeError as e:
    if "Circuit breaker is OPEN" in str(e):
        print("Service is down, circuit is open")
except Exception as e:
    print(f"Operation failed: {e}")

# Check state
state = breaker.get_state()
print(f"Circuit state: {state['state']}")  # CLOSED/OPEN/HALF_OPEN
print(f"Failure count: {state['failure_count']}")
```

#### E. Recovery Manager (All-in-One):
```python
from error_recovery_v2 import get_recovery_manager

manager = get_recovery_manager()

# Execute với retry + circuit breaker
result = manager.execute_with_recovery(
    'docker_operation',      # Operation name
    run_docker_command,      # Function
    ['docker', 'ps'],        # Args
    max_attempts=3,
    use_circuit_breaker=True
)

# Xem error statistics
stats = manager.get_error_stats()
print(f"Total errors: {stats['total_errors']}")
print(f"By category: {stats['by_category']}")
print(f"By operation: {stats['by_operation']}")
print(f"Recent errors: {stats['recent_errors'][:5]}")
```

#### F. Error Classification:
```python
from error_recovery_v2 import ErrorClassifier

# Phân loại lỗi tự động
errors = [
    ConnectionError("Connection refused"),
    TimeoutError("Timeout"),
    PermissionError("Access denied")
]

for error in errors:
    category = ErrorClassifier.classify(error)
    retryable = ErrorClassifier.is_retryable(error)
    print(f"{type(error).__name__}: {category.value} (retry: {retryable})")
```

### ⚠️ Lưu ý:
- Chỉ retry cho transient errors (network, timeout, resource)
- Không retry cho validation/permission errors
- Circuit breaker tự động recover sau timeout

---

## 3️⃣ Connection Pool V2 - Pooling Nâng cao

### 🎯 Mục đích:
- Quản lý connections hiệu quả
- Health checks tự động
- Connection rotation và cleanup

### 📝 Sử dụng cơ bản:

#### A. Tạo Connection Pool:
```python
from connection_pool_v2 import ConnectionPool

# Factory function để tạo connection
def create_db_connection():
    import sqlite3
    return sqlite3.connect('database.db')

# Health check function
def check_db_health(conn):
    try:
        conn.execute('SELECT 1')
        return True
    except:
        return False

# Tạo pool
pool = ConnectionPool(
    factory=create_db_connection,
    min_size=2,                # Minimum connections
    max_size=10,               # Maximum connections
    health_check=check_db_health,
    max_idle_time=300.0,       # 5 minutes
    max_lifetime=3600.0,       # 1 hour
    timeout=30.0               # Timeout khi acquire
)
```

#### B. Sử dụng Connection (Context Manager):
```python
# Cách đơn giản nhất - context manager
with pool.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    results = cursor.fetchall()
# ✅ Connection tự động return về pool
```

#### C. Sử dụng Connection (Manual):
```python
# Manual acquire/release
pooled_conn = pool.acquire(timeout=30.0)
try:
    conn = pooled_conn.connection
    # Use connection...
    result = conn.execute(query)
except Exception as e:
    # Connection được mark là có lỗi
    print(f"Error: {e}")
finally:
    # Luôn release connection
    pool.release(pooled_conn)
```

#### D. Pool Statistics:
```python
# Xem thống kê pool
stats = pool.get_stats()

print(f"Available connections: {stats['available']}")
print(f"In-use connections: {stats['in_use']}")
print(f"Total connections: {stats['total']}")
print(f"Pool limits: min={stats['min_size']}, max={stats['max_size']}")

# Statistics về operations
print(f"Created: {stats['total_created']}")
print(f"Destroyed: {stats['total_destroyed']}")
print(f"Acquired: {stats['total_acquired']}")
print(f"Released: {stats['total_released']}")
print(f"Errors: {stats['total_errors']}")
```

#### E. Cleanup Pool:
```python
# Context manager (recommended)
with ConnectionPool(factory=create_connection, ...) as pool:
    # Use pool
    with pool.get_connection() as conn:
        result = conn.query()
# ✅ Pool tự động đóng

# Manual cleanup
pool = ConnectionPool(...)
# ... use pool ...
pool.close()  # Cleanup all connections
```

### ⚠️ Lưu ý:
- Pool tự động cleanup stale connections
- Health checks chạy định kỳ
- Connection rotation theo max_lifetime
- Thread-safe implementation

---

## 🔧 Integration Examples

### Example 1: Docker Command với Retry
```python
from error_recovery_v2 import retry, RetryStrategy

@retry(max_attempts=3, strategy=RetryStrategy.EXPONENTIAL)
def run_docker_ps():
    result = subprocess.run(
        ['docker', 'ps'],
        capture_output=True,
        text=True,
        timeout=10
    )
    if result.returncode != 0:
        raise RuntimeError(f"Docker command failed: {result.stderr}")
    return result.stdout

# Sử dụng
try:
    output = run_docker_ps()
    print(output)
except Exception as e:
    print(f"Failed after retries: {e}")
```

### Example 2: Database Operations với Pool
```python
from connection_pool_v2 import ConnectionPool

# Setup pool
db_pool = ConnectionPool(
    factory=lambda: sqlite3.connect('app.db'),
    min_size=2,
    max_size=5
)

# Sử dụng trong function
def get_user(user_id):
    with db_pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        return cursor.fetchone()

def save_user(user_data):
    with db_pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (name, email) VALUES (?, ?)',
            (user_data['name'], user_data['email'])
        )
        conn.commit()
```

### Example 3: File Processing với Resource Management
```python
from resource_cleanup import managed_file
from error_recovery_v2 import retry

@retry(max_attempts=3)
def process_large_file(filepath):
    with managed_file(filepath, 'r') as f:
        for line in f:
            process_line(line)
    # ✅ File tự động đóng ngay cả khi có lỗi
```

### Example 4: Full Stack Integration
```python
from resource_cleanup import managed_process
from error_recovery_v2 import get_recovery_manager
from connection_pool_v2 import ConnectionPool

class AppService:
    def __init__(self):
        self.recovery_manager = get_recovery_manager()
        self.db_pool = ConnectionPool(
            factory=self.create_db_connection,
            min_size=2,
            max_size=10
        )
    
    def create_db_connection(self):
        # Factory cho connection pool
        return sqlite3.connect('app.db')
    
    def run_spark_job(self, script_path):
        """Chạy Spark job với full protection"""
        
        # Execute với recovery manager
        result = self.recovery_manager.execute_with_recovery(
            'spark_job',
            self._execute_spark,
            script_path,
            max_attempts=3,
            use_circuit_breaker=True
        )
        
        # Save kết quả vào database
        with self.db_pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO job_results (script, result) VALUES (?, ?)',
                (script_path, result)
            )
            conn.commit()
        
        return result
    
    def _execute_spark(self, script_path):
        """Internal execution logic"""
        proc = subprocess.Popen(
            ['spark-submit', script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        with managed_process(proc) as p:
            stdout, stderr = p.communicate(timeout=300)
            
            if p.returncode != 0:
                raise RuntimeError(f"Spark job failed: {stderr}")
            
            return stdout.decode()
```

---

## 🧪 Testing

### Test Resource Cleanup:
```bash
cd run_spark_gui
python resource_cleanup.py
```

**Expected Output:**
```
Testing Resource Cleanup Manager
======================================================================

1. Testing file resource management:
  ✓ File opened and registered
  ✓ File closed and unregistered

2. Testing manual registration:
  ✓ Resource registered with ID: 1

3. Resource statistics:
  • Total registered: 1
  • Total cleaned: 0
  • By type:
    - files: 1 alive, 0 GC'd

4. Triggering cleanup...
======================================================================
🧹 STARTING RESOURCE CLEANUP
======================================================================

📦 Cleaning up files (1 items)...

======================================================================
✅ CLEANUP COMPLETED
  • Success: 1
  • Failed: 0
  • Skipped (GC'd): 0
  • Total registered: 1
  • Total cleaned: 1
======================================================================

✅ Resource Cleanup Manager test completed!
```

### Test Error Recovery:
```bash
python error_recovery_v2.py
```

### Test Connection Pool:
```bash
python connection_pool_v2.py
```

---

## 📊 Monitoring & Debugging

### 1. Monitor Resources:
```python
import time
from resource_cleanup import get_resource_registry

# Monitoring loop
while True:
    stats = get_resource_registry().get_stats()
    print(f"[{time.strftime('%H:%M:%S')}] Resources: {stats['total_registered']}")
    
    # Alert nếu quá nhiều resources
    if stats['total_registered'] > 100:
        print("⚠️ WARNING: Too many resources!")
    
    time.sleep(60)
```

### 2. Monitor Errors:
```python
from error_recovery_v2 import get_recovery_manager

# Error monitoring
manager = get_recovery_manager()
stats = manager.get_error_stats()

# Alert nếu error rate cao
if stats['total_errors'] > 100:
    print("⚠️ HIGH ERROR RATE!")
    print(f"By category: {stats['by_category']}")
    print(f"Recent errors: {stats['recent_errors'][:5]}")
```

### 3. Monitor Connection Pool:
```python
# Pool health check
stats = pool.get_stats()

# Check pool health
health = {
    'healthy': stats['available'] > 0,
    'utilization': stats['in_use'] / stats['max_size'],
    'errors': stats['total_errors']
}

if health['utilization'] > 0.8:
    print("⚠️ Pool is near capacity!")
```

---

## 🚨 Troubleshooting

### Problem 1: Resources Not Cleaned
**Symptom:** Resource count keeps growing
**Solution:**
```python
# Kiểm tra resource stats
stats = get_resource_registry().get_stats()
print(stats)

# Force cleanup
registry = get_resource_registry()
cleanup_stats = registry.cleanup_all(verbose=True)
print(f"Cleaned: {cleanup_stats['success']}")
```

### Problem 2: Circuit Breaker Stuck OPEN
**Symptom:** All operations fail with "Circuit breaker is OPEN"
**Solution:**
```python
# Reset circuit breaker
from error_recovery_v2 import get_recovery_manager

manager = get_recovery_manager()
breaker = manager.get_or_create_circuit_breaker('operation_name')
breaker.reset()
print("Circuit breaker reset")
```

### Problem 3: Connection Pool Exhausted
**Symptom:** Timeout waiting for connection
**Solution:**
```python
# Check pool stats
stats = pool.get_stats()
print(f"Available: {stats['available']}")
print(f"In use: {stats['in_use']}")

# Options:
# 1. Increase max_size
# 2. Decrease max_idle_time
# 3. Check for connection leaks (connections not returned)
```

---

## 📚 References

- **Full Documentation:** `OPTIMIZATION_REPORT_V6.2.md`
- **Source Code:**
  - `resource_cleanup.py`
  - `error_recovery_v2.py`
  - `connection_pool_v2.py`
- **Examples:** Tất cả files có `if __name__ == '__main__'` block với examples

---

## 🎓 Best Practices

### ✅ DO:
- Luôn sử dụng context managers (`with` statement)
- Sử dụng retry cho network operations
- Monitor resource usage định kỳ
- Use connection pooling cho database operations

### ❌ DON'T:
- Đừng manually close resources khi dùng context manager
- Đừng retry cho validation errors
- Đừng giữ connection quá lâu
- Đừng ignore cleanup errors

---

**Version:** 6.2.0
**Last Updated:** 2025-10-13
**Status:** Production Ready ✅
