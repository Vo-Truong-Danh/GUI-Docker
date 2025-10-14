# 🚀 HƯỚNG DẪN SỬ DỤNG TÍNH NĂNG MỚI V6.4.0

## Comprehensive Guide for New Features

**Version:** 6.4.0  
**Date:** October 13, 2025

---

## 📋 MỤC LỤC

1. [Code Quality Checker](#1-code-quality-checker)
2. [Dependency Optimizer](#2-dependency-optimizer)
3. [Advanced Error Recovery](#3-advanced-error-recovery)
4. [System Health Dashboard](#4-system-health-dashboard)
5. [Best Practices](#5-best-practices)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. 📊 Code Quality Checker

### Giới thiệu

Tool phân tích chất lượng mã nguồn tự động, phát hiện lỗi, security issues, và code smells.

### Cài đặt

Không cần cài đặt thêm, sử dụng Python standard library.

### Sử dụng cơ bản

#### Command Line

```bash
# Phân tích thư mục hiện tại
cd run_spark_gui
python code_quality_checker.py .

# Phân tích thư mục cụ thể
python code_quality_checker.py /path/to/project

# View báo cáo chi tiết
cat code_quality_report.json
```

#### Trong Python Code

```python
from code_quality_checker import CodeQualityChecker

# Khởi tạo checker
checker = CodeQualityChecker(".")

# Chạy phân tích
report = checker.analyze_project()

# In báo cáo
checker.print_report()

# Export báo cáo
import json
with open('report.json', 'w') as f:
    json.dump(report, f, indent=2)
```

### Các loại issues được phát hiện

1. **Critical** 🔴
   - eval()/exec() usage
   - SQL injection risks
   - Command injection

2. **High** 🟠
   - Shell injection (shell=True)
   - Unsafe deserialization
   - Missing input validation

3. **Medium** 🟡
   - High code complexity
   - Generic exception handling
   - Missing error logging

4. **Low** 🟢
   - Long functions
   - Naming convention violations
   - Code organization

5. **Info** ℹ️
   - Missing docstrings
   - Wildcard imports
   - Style issues

### Hiểu kết quả

```python
{
  "summary": {
    "total_issues": 181,
    "critical": 2,
    "high": 9,
    "medium": 20,
    "low": 26,
    "info": 124
  },
  "issues": [
    {
      "severity": "high",
      "category": "Security",
      "message": "Shell injection vulnerability",
      "file": "example.py",
      "line": 42,
      "suggestion": "Use list arguments instead of shell=True"
    }
  ]
}
```

### Tích hợp vào CI/CD

```yaml
# .github/workflows/quality-check.yml
name: Code Quality Check

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run quality check
        run: |
          python code_quality_checker.py .
          # Exit with error if critical issues found
          if [ $(jq '.summary.critical' code_quality_report.json) -gt 0 ]; then
            exit 1
          fi
```

---

## 2. 📦 Dependency Optimizer

### Giới thiệu

Phân tích và tối ưu hóa dependencies, phát hiện packages không sử dụng và thiếu.

### Sử dụng

#### Command Line

```bash
# Phân tích dependencies
cd run_spark_gui
python dependency_optimizer.py .

# Xem báo cáo
cat dependency_report.json

# Sử dụng requirements tối ưu
pip install -r requirements_optimized.txt
```

#### Trong Python Code

```python
from dependency_optimizer import DependencyOptimizer

# Khởi tạo
optimizer = DependencyOptimizer(".")

# Chạy phân tích
report = optimizer.analyze()

# In báo cáo
optimizer.print_report(report)

# Tạo requirements tối ưu
optimizer.generate_optimized_requirements()
```

### Hiểu kết quả

```python
{
  "summary": {
    "total_imports": 77,
    "stdlib_imports": 41,
    "third_party_imports": 36,
    "unused_dependencies": 2,
    "missing_dependencies": 34
  },
  "details": {
    "unused_dependencies": ["pyspark", "pyyaml"],
    "missing_dependencies": ["pytest", ...],
    "potential_duplicates": []
  }
}
```

### Best Practices

1. **Chạy định kỳ**
   ```bash
   # Thêm vào cron job
   0 0 * * 0 cd /path/to/project && python dependency_optimizer.py .
   ```

2. **Review trước khi update**
   ```bash
   # So sánh requirements
   diff requirements.txt requirements_optimized.txt
   
   # Test với requirements mới
   pip install -r requirements_optimized.txt
   pytest
   ```

3. **Pin versions**
   ```
   # Thay vì
   psutil
   
   # Nên dùng
   psutil>=5.8.0,<6.0.0
   ```

---

## 3. 🔧 Advanced Error Recovery

### Giới thiệu

Hệ thống recovery tự động với khả năng học và tối ưu strategies.

### Sử dụng với Decorator

```python
from advanced_error_recovery import with_recovery

@with_recovery(max_retries=3)
def risky_operation():
    """Operation that might fail"""
    response = requests.get("https://api.example.com/data")
    return response.json()

# Sử dụng
try:
    data = risky_operation()
except Exception as e:
    print(f"All recovery attempts failed: {e}")
```

### Sử dụng Manual

```python
from advanced_error_recovery import get_recovery_system

recovery = get_recovery_system()

def my_operation():
    # Your code
    return result

try:
    # Original operation
    result = my_operation()
except Exception as e:
    # Attempt recovery
    success, result = recovery.recover(
        error=e,
        operation=my_operation,
        context="Data fetching",
        max_retries=3
    )
    
    if not success:
        raise  # Re-raise if can't recover
```

### Recovery Strategies

1. **RETRY** - Thử lại operation
   ```python
   # Tự động với exponential backoff
   # Wait: 1s, 2s, 4s, 8s, ...
   ```

2. **FALLBACK** - Sử dụng phương án dự phòng
   ```python
   def primary_source():
       return fetch_from_api()
   
   def fallback_source():
       return fetch_from_cache()
   
   success, data = recovery.recover(
       error=e,
       operation=primary_source,
       fallback=fallback_source
   )
   ```

3. **WAIT** - Đợi và retry
   ```python
   # Đợi lâu hơn trước khi retry
   # Useful cho timeout/rate limit errors
   ```

4. **SKIP** - Bỏ qua operation
   ```python
   # Continue execution
   # Return None hoặc default value
   ```

5. **ESCALATE** - Chuyển lên level cao hơn
   ```python
   # Re-raise exception
   # Để caller xử lý
   ```

### Monitoring Recovery

```python
# Xem statistics
stats = recovery.get_statistics()
print(f"Recovery rate: {stats['recovery_rate']:.1%}")

# Print dashboard
recovery.print_statistics()
```

### Tùy chỉnh Error Classification

```python
from advanced_error_recovery import AdvancedErrorRecovery, ErrorCategory, RecoveryStrategy

# Tạo custom recovery system
recovery = AdvancedErrorRecovery()

# Classify error
category = recovery.classify_error(exception)

# Determine strategy
strategy = recovery.determine_recovery_strategy(exception, category)
```

---

## 4. 🏥 System Health Dashboard

### Giới thiệu

Monitor real-time system health với alerting và analytics.

### Sử dụng cơ bản

#### Start Monitoring

```python
from system_health_dashboard import get_health_monitor

# Get global instance
monitor = get_health_monitor()

# Start monitoring (interval in seconds)
monitor.start_monitoring(interval=5)

# Monitor runs in background thread
```

#### Get Current Status

```python
# Get current health
status = monitor.get_current_status()

print(f"Health: {status['health_status']}")  # healthy/degraded/warning/critical
print(f"Score: {status['health_score']}/100")

# Get metrics
metrics = status['metrics']
print(f"CPU: {metrics['cpu_percent']}%")
print(f"Memory: {metrics['memory_percent']}%")
print(f"Disk: {metrics['disk_percent']}%")
```

#### Print Dashboard

```python
# Print formatted dashboard
monitor.print_dashboard()
```

Output:
```
================================================================================
🏥 SYSTEM HEALTH DASHBOARD
================================================================================

✅ Overall Health: HEALTHY (Score: 92.5/100)

📊 Current Metrics:
  🖥️  CPU: 45.2% 🟢
  💾 Memory: 62.8% (8.1 / 16.0 GB) 🟢
  💿 Disk: 73.4% (234.5 / 512.0 GB) 🟢
  🌐 Network: ↑ 1250.3 MB  ↓ 3421.7 MB
  📊 Processes: 234

📈 Statistics:
  Uptime: 3600 seconds
  Samples collected: 720
  Alerts generated: 3
  Max CPU: 78.5%
  Max Memory: 71.2%
  Max Disk: 73.4%

🚨 Recent Alerts:
  ⚠️ CPU usage high: 75.3%
  ⚠️ Memory usage high: 71.2%
================================================================================
```

#### Export Report

```python
# Export to JSON
monitor.export_report("health_report.json")

# Load and analyze
import json
with open("health_report.json") as f:
    report = json.load(f)
```

### Tùy chỉnh Thresholds

```python
# Customize alert thresholds
monitor.thresholds['cpu_warning'] = 60.0      # Default: 70.0
monitor.thresholds['cpu_critical'] = 80.0     # Default: 90.0
monitor.thresholds['memory_warning'] = 75.0   # Default: 70.0
monitor.thresholds['memory_critical'] = 90.0  # Default: 85.0
```

### Historical Data

```python
# Get historical data (last N minutes)
history = monitor.get_historical_data(minutes=10)

# Analyze trends
import pandas as pd
df = pd.DataFrame(history)

# Plot
import matplotlib.pyplot as plt
plt.plot(df['timestamp'], df['cpu_percent'])
plt.xlabel('Time')
plt.ylabel('CPU %')
plt.title('CPU Usage Over Time')
plt.show()
```

### Alerts và Callbacks

```python
# Custom alert handler (coming in future version)
def on_critical_alert(alert):
    print(f"CRITICAL: {alert.message}")
    send_email_alert(alert)
    restart_services()

monitor.on_alert_callback = on_critical_alert
```

### Stop Monitoring

```python
# Stop background monitoring
monitor.stop_monitoring()
```

### Tích hợp vào GUI

```python
import tkinter as tk
from system_health_dashboard import get_health_monitor

class HealthDashboardTab:
    def __init__(self, parent):
        self.monitor = get_health_monitor()
        self.monitor.start_monitoring(interval=5)
        
        # Create UI
        self.create_widgets(parent)
        
        # Update UI periodically
        self.update_ui()
    
    def create_widgets(self, parent):
        # CPU Label
        self.cpu_label = tk.Label(parent, text="CPU: ---%")
        self.cpu_label.pack()
        
        # Memory Label
        self.memory_label = tk.Label(parent, text="Memory: ---%")
        self.memory_label.pack()
        
        # Health Status
        self.status_label = tk.Label(parent, text="Status: --")
        self.status_label.pack()
    
    def update_ui(self):
        status = self.monitor.get_current_status()
        metrics = status['metrics']
        
        # Update labels
        self.cpu_label.config(text=f"CPU: {metrics['cpu_percent']:.1f}%")
        self.memory_label.config(text=f"Memory: {metrics['memory_percent']:.1f}%")
        self.status_label.config(text=f"Status: {status['health_status']}")
        
        # Color based on health
        if status['health_status'] == 'healthy':
            self.status_label.config(fg='green')
        elif status['health_status'] in ['degraded', 'warning']:
            self.status_label.config(fg='orange')
        else:
            self.status_label.config(fg='red')
        
        # Schedule next update
        self.status_label.after(5000, self.update_ui)  # Update every 5s
```

---

## 5. ✅ Best Practices

### Code Quality

1. **Chạy quality check trước commit**
   ```bash
   # Pre-commit hook
   python code_quality_checker.py .
   if [ $? -ne 0 ]; then
       echo "Quality check failed. Please fix issues."
       exit 1
   fi
   ```

2. **Fix theo priority**
   - Critical → High → Medium → Low → Info
   - Security issues first
   - High complexity functions next

3. **Document as you code**
   ```python
   def my_function(param1: str, param2: int) -> bool:
       """
       Short description.
       
       Args:
           param1: Description
           param2: Description
       
       Returns:
           Description
       
       Raises:
           ValueError: When ...
       """
       pass
   ```

### Error Handling

1. **Always use specific exceptions**
   ```python
   # ❌ Bad
   try:
       ...
   except:
       pass
   
   # ✅ Good
   try:
       ...
   except (FileNotFoundError, PermissionError) as e:
       logger.error(f"File error: {e}")
       raise
   ```

2. **Use recovery system for external calls**
   ```python
   @with_recovery(max_retries=3)
   def external_api_call():
       return requests.get(url).json()
   ```

3. **Log context information**
   ```python
   try:
       process_data(file_path)
   except Exception as e:
       logger.error(f"Failed to process {file_path}: {e}", exc_info=True)
   ```

### Dependency Management

1. **Pin versions in production**
   ```
   # requirements.txt
   psutil==5.9.0
   pyyaml>=6.0,<7.0
   ```

2. **Separate dev dependencies**
   ```
   # requirements-dev.txt
   pytest>=7.0.0
   black>=22.0.0
   mypy>=0.942
   ```

3. **Regular security audits**
   ```bash
   pip install safety
   safety check
   ```

### System Health

1. **Monitor continuously in production**
   ```python
   # In main application
   monitor = get_health_monitor()
   monitor.start_monitoring(interval=10)
   ```

2. **Set up alerts**
   ```python
   # Configure email/Slack alerts for critical issues
   ```

3. **Review metrics regularly**
   ```bash
   # Weekly report
   python -c "from system_health_dashboard import get_health_monitor; get_health_monitor().print_dashboard()"
   ```

---

## 6. 🔧 Troubleshooting

### Code Quality Checker

**Issue: SyntaxError when analyzing file**
```
Solution: File has actual syntax errors. Fix them first.
```

**Issue: Too many false positives**
```
Solution: Customize patterns in code_quality_checker.py
```

### Dependency Optimizer

**Issue: Missing dependencies reported as used**
```
Solution: These are local modules, not external packages. It's normal.
```

**Issue: False unused dependencies**
```
Solution: Check if package is used via different import name (e.g., yaml → pyyaml)
```

### Error Recovery

**Issue: Recovery not working**
```python
# Check if recovery is enabled
recovery = get_recovery_system()
print(recovery.stats)

# Verify operation is retryable
# Some operations (like file writes) may not be safely retryable
```

**Issue: Too many retries**
```python
# Reduce max_retries
@with_recovery(max_retries=1)
def operation():
    pass
```

### System Health Dashboard

**Issue: Permission denied errors**
```
Solution: Run with appropriate permissions or adjust monitored resources
```

**Issue: High CPU usage from monitoring**
```python
# Increase monitoring interval
monitor.start_monitoring(interval=30)  # 30 seconds instead of 5
```

**Issue: Alerts not triggered**
```python
# Check thresholds
print(monitor.thresholds)

# Lower thresholds if needed
monitor.thresholds['cpu_warning'] = 50.0
```

---

## 📚 Tài liệu bổ sung

- Main README: `README.md`
- Optimization Report: `SYSTEM_OPTIMIZATION_REPORT_V6.4.0.md`
- API Documentation: Docstrings in each module
- Code Quality Report: `code_quality_report.json`
- Dependency Report: `dependency_report.json`

---

## 🆘 Support

Nếu có vấn đề:
1. Check docstrings in module files
2. Review báo cáo chi tiết (JSON files)
3. Check logs in `run_spark_gui/logs/`
4. Contact development team

---

**Happy Coding! 🚀**

Version 6.4.0 - October 13, 2025
