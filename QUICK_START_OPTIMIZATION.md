# 🚀 HƯỚNG DẪN SỬ DỤNG NHANH - HỆ THỐNG TỐI ƯU HÓA

## 📦 Tổng Quan Nhanh

Hệ thống đã được **tối ưu hóa toàn diện** với 9 modules mới:

1. ✅ **error_handler.py** - Xử lý lỗi nâng cao
2. ✅ **auto_recovery.py** - Tự động phục hồi
3. ✅ **backup_manager.py** - Quản lý backup
4. ✅ **system_optimizer.py** - Tối ưu hệ thống
5. ✅ **security_auditor.py** - Kiểm tra bảo mật
6. ✅ **code_quality_checker.py** - Kiểm tra chất lượng code
7. ✅ **analyze_system.py** - Phân tích toàn diện
8. ✅ **auto_fixer.py** - Tự động sửa lỗi
9. ✅ **health_monitoring_dashboard.py** - Dashboard giám sát

---

## 🎯 Sử Dụng Nhanh

### 1. Khởi Chạy Ứng Dụng (Với Tối Ưu Hóa)

**Cách 1: Sử dụng batch file mới**
```bash
START_OPTIMIZED.bat
```

Batch file này sẽ:
- Hỏi có muốn chạy phân tích hệ thống không
- Hỏi có muốn mở dashboard giám sát không
- Tự động khởi chạy ứng dụng chính

**Cách 2: Khởi chạy thủ công**
```bash
cd run_spark_gui
python main.py
```

### 2. Chạy Phân Tích Hệ Thống Toàn Diện

```bash
cd run_spark_gui
python analyze_system.py
```

**Kết quả:**
- ✅ Phân tích CPU, Memory, Disk
- ✅ Quét bảo mật (6 loại vulnerability)
- ✅ Tối ưu memory tự động
- ✅ Dọn dẹp temp files
- ✅ Backup configuration
- ✅ Tạo báo cáo JSON trong `logs/`

### 3. Mở Health Monitoring Dashboard

```bash
cd run_spark_gui
python health_monitoring_dashboard.py
```

**Chức năng:**
- 📊 Hiển thị real-time: CPU, Memory, Disk
- 🔄 Cập nhật mỗi 5 giây
- ⚠️ Cảnh báo tự động khi tài nguyên cao
- 🔧 Nút "Optimize Now" để tối ưu ngay
- 📝 Activity log với timestamp
- 📊 Xem full report

### 4. Kiểm Tra Bảo Mật

**Trong Python:**
```python
from security_auditor import get_security_auditor

auditor = get_security_auditor()
report = auditor.generate_security_report('.')
print(auditor.get_vulnerability_summary(report))
```

**Hoặc chạy analyze_system.py** - bao gồm cả security audit

### 5. Tối Ưu Hóa Tự Động

```bash
cd run_spark_gui
python auto_fixer.py
```

**Sửa gì:**
- File permissions
- Error handling suggestions
- Code quality issues

### 6. Kiểm Tra Chất Lượng Code

**Trong Python:**
```python
from code_quality_checker import get_code_quality_checker

checker = get_code_quality_checker()
report = checker.analyze_directory('.')
print(checker.get_report_summary(report))
```

---

## 🔧 Tích Hợp Vào Code Hiện Tại

### Import Modules

```python
# Error handling
from error_handler import get_error_handler, with_error_handling, ErrorSeverity

# Recovery
from auto_recovery import get_auto_recovery_manager

# Backup
from backup_manager import get_backup_manager

# Optimization
from system_optimizer import get_system_optimizer

# Security
from security_auditor import get_security_auditor

# Code quality
from code_quality_checker import get_code_quality_checker
```

### Sử Dụng Error Handler

```python
# Cách 1: Decorator
@with_error_handling(context="Loading config", severity=ErrorSeverity.HIGH)
def load_config():
    # Your code
    pass

# Cách 2: Safe execute
from error_handler import safe_execute

result = safe_execute(
    risky_function,
    default="fallback_value",
    context="Database operation"
)

# Cách 3: Manual handling
handler = get_error_handler(logger)
try:
    # Your code
    pass
except Exception as e:
    handler.handle_error(e, context="Custom operation", severity=ErrorSeverity.HIGH)
```

### Sử Dụng Backup

```python
backup_mgr = get_backup_manager(max_backups=10)

# Tạo backup
backup_path = backup_mgr.create_backup('config.json', 'config')

# Restore
backup_mgr.restore_backup(backup_path)

# Liệt kê backups
backups = backup_mgr.list_backups()
for backup in backups:
    print(f"{backup['name']} - {backup['timestamp']}")
```

### Sử Dụng System Optimizer

```python
optimizer = get_system_optimizer(logger)

# Lấy metrics
metrics = optimizer.get_system_metrics()
print(f"CPU: {metrics['cpu']['percent']}%")
print(f"Memory: {metrics['memory']['percent']}%")

# Tối ưu memory
result = optimizer.optimize_memory()
print(f"Collected {result['objects_collected']} objects")

# Kiểm tra resource leaks
leaks = optimizer.check_resource_leaks()
if leaks['has_leaks']:
    for warning in leaks['warnings']:
        print(f"⚠️ {warning}")

# Bắt đầu monitoring (tự động optimize khi memory > 85%)
optimizer.start_monitoring(interval=60)  # Every 60 seconds
```

### Sử Dụng Auto Recovery

```python
recovery = get_auto_recovery_manager(logger)

# Register custom recovery strategy
def recover_database_connection(context):
    # Your recovery logic
    return True

recovery.register_strategy('db_connection_lost', recover_database_connection)

# Attempt recovery
success = recovery.attempt_recovery('db_connection_lost', context={'host': 'localhost'})
```

---

## 📊 Test Modules

```bash
cd run_spark_gui
python test_optimization_modules.py
```

**Kết quả mong đợi:** ✅ ALL TESTS PASSED!

---

## 📝 Các Files Quan Trọng

### Báo Cáo & Logs
- `logs/system_analysis_report_*.json` - Báo cáo phân tích hệ thống
- `logs/autofix_report_*.txt` - Báo cáo auto-fix
- `logs/*.log` - Application logs

### Backups
- `backups/` - Automatic backups (main directory)
- `backups_autofix/` - Backups từ auto-fixer

### Documentation
- `SYSTEM_OPTIMIZATION_COMPLETE_REPORT.md` - Báo cáo chi tiết đầy đủ
- `QUICK_START_OPTIMIZATION.md` - Hướng dẫn này

---

## ⚡ Quick Commands Cheat Sheet

```bash
# Phân tích toàn diện
python run_spark_gui/analyze_system.py

# Mở dashboard
python run_spark_gui/health_monitoring_dashboard.py

# Test modules
python run_spark_gui/test_optimization_modules.py

# Auto-fix issues
python run_spark_gui/auto_fixer.py

# Chạy ứng dụng chính
python run_spark_gui/main.py

# Hoặc dùng batch file
START_OPTIMIZED.bat
```

---

## 🔍 Kiểm Tra Nhanh

### 1. Kiểm Tra Modules Có Import Được Không?

```python
import sys
sys.path.insert(0, 'run_spark_gui')

try:
    from error_handler import get_error_handler
    from system_optimizer import get_system_optimizer
    from security_auditor import get_security_auditor
    print("✅ All modules imported successfully!")
except ImportError as e:
    print(f"❌ Import error: {e}")
```

### 2. Kiểm Tra System Metrics

```python
from system_optimizer import get_system_optimizer

optimizer = get_system_optimizer()
metrics = optimizer.get_system_metrics()

print(f"CPU: {metrics['cpu']['percent']:.1f}%")
print(f"Memory: {metrics['memory']['percent']:.1f}%")
print(f"Disk: {metrics['disk']['percent']:.1f}%")
```

### 3. Kiểm Tra Security Score

```python
from security_auditor import get_security_auditor

auditor = get_security_auditor()
report = auditor.generate_security_report('run_spark_gui')
print(f"Security Score: {report['overall_score']}/100")
```

---

## 🚨 Troubleshooting

### Lỗi: Module not found
```bash
# Đảm bảo đang ở đúng thư mục
cd run_spark_gui
python -c "import error_handler; print('OK')"
```

### Lỗi: psutil not found
```bash
pip install psutil
```

### Dashboard không mở được
- Kiểm tra tkinter: `python -m tkinter`
- Nếu lỗi, cài đặt: `pip install tk` (Linux) hoặc reinstall Python với tkinter

### Permission errors (Windows)
- Chạy as Administrator
- Hoặc bỏ qua file permission fixes

---

## 📈 Performance Benchmarks

### Before Optimization:
- Error handling: Basic
- Monitoring: Manual
- Security scanning: None
- Resource management: Limited

### After Optimization:
- ✅ Error handling: Advanced với recovery
- ✅ Monitoring: Real-time automated
- ✅ Security: Comprehensive scanning (6 vulnerability types)
- ✅ Resource: Automated optimization
- ✅ Code quality: Automated checking
- ✅ Backup: Automated với retention

---

## 🎓 Best Practices

1. **Chạy analyze_system.py định kỳ** (hàng tuần)
2. **Mở dashboard khi develop/debug** để theo dõi resources
3. **Backup trước khi deploy** (`backup_mgr.create_backup()`)
4. **Review security reports** và fix Critical/High vulnerabilities
5. **Sử dụng error handler** cho tất cả operations quan trọng
6. **Enable monitoring** trong production (`optimizer.start_monitoring()`)

---

## 📞 Support

Nếu gặp vấn đề:
1. Check logs trong `run_spark_gui/logs/`
2. Run test: `python test_optimization_modules.py`
3. Review báo cáo: `SYSTEM_OPTIMIZATION_COMPLETE_REPORT.md`
4. Check errors với dashboard

---

## ✅ Checklist Sau Khi Tối Ưu

- [ ] Chạy `test_optimization_modules.py` - All pass?
- [ ] Chạy `analyze_system.py` - Security score?
- [ ] Mở dashboard - Resources OK?
- [ ] Backup created?
- [ ] Main app vẫn chạy được?
- [ ] Error handling hoạt động?
- [ ] Monitoring dashboard mở được?

---

**🎉 Nếu tất cả checklist đều OK, hệ thống đã sẵn sàng production!**

---

*Tài liệu được tạo tự động - v1.0.0 - 14/10/2025*
