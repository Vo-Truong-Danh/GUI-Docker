# Hướng dẫn Nâng cấp lên Version 5.0.0

## 🎯 Tổng quan

Version 5.0.0 là bản cập nhật lớn với nhiều cải tiến về **error handling**, **validation**, **logging**, và **health monitoring**. Tài liệu này hướng dẫn chi tiết cách nâng cấp từ v4.x lên v5.0.0.

---

## ✅ Checklist Trước khi Nâng cấp

### 1. Backup dữ liệu quan trọng
```bash
# Backup configuration
copy spark_runner_config.json spark_runner_config.json.backup

# Backup database
copy spark_runner.db spark_runner.db.backup

# Backup logs (if any)
xcopy /E /I logs logs_backup
```

### 2. Kiểm tra phiên bản hiện tại
```python
# Mở main.py và kiểm tra VERSION
VERSION = "4.x.x"  # Phiên bản cũ
```

### 3. Đảm bảo Python version
```bash
python --version
# Cần: Python 3.8 trở lên
```

---

## 📥 Nâng cấp Từng bước

### Bước 1: Pull code mới từ repository
```bash
cd "d:\BaiTapSinhVien\TH BigData\GUI-Docker"
git pull origin main
```

### Bước 2: Kiểm tra files mới
**Files mới được thêm vào**:
- ✅ `logging_config.py` - Hệ thống logging
- ✅ `validation.py` - Input validation
- ✅ `health_check.py` - System health monitoring
- ✅ `CHANGELOG_V5.md` - Chi tiết cập nhật
- ✅ `UPGRADE_GUIDE.md` - Tài liệu này

**Files đã được cập nhật**:
- 🔄 `main.py` - Tích hợp modules mới
- 🔄 `spark_backend.py` - Enhanced error handling
- 🔄 `docker_utils.py` - Better Docker management
- 🔄 `database.py` - Retry logic và WAL mode

### Bước 3: Không cần install dependencies
Version 5.0.0 không thêm dependencies mới. Tất cả modules đều dùng pure Python standard library.

```bash
# Kiểm tra dependencies hiện tại vẫn đủ
pip install -r requirements.txt
```

### Bước 4: Test configuration
```bash
# Chạy script test
cd run_spark_gui
python validation.py
```

**Output mong đợi**:
```
================================================================================
VALIDATION MODULE TESTS
================================================================================

1. Container Name Validation:
  ✅ 'spark-worker': True - OK
  ✅ 'namenode': True - OK
  ...

✅ All validation tests completed!
```

### Bước 5: Test logging
```bash
python logging_config.py
```

**Output mong đợi**:
```
[2025-10-13 10:30:00] INFO     | test                 | This is an info message
[2025-10-13 10:30:00] WARNING  | test                 | This is a warning message
...
Logs written to: d:\...\run_spark_gui\logs
```

### Bước 6: Test health check
```bash
python health_check.py
```

**Output mong đợi**:
```
================================================================================
HEALTH CHECK SYSTEM TESTS
================================================================================

1. Checking Docker Daemon...
   ✅ Docker Daemon: Docker is running and responsive

...

📊 Overall Health: healthy - All systems operational
✅ All health check tests completed!
```

### Bước 7: Khởi động ứng dụng
```bash
# Windows
START.bat

# Hoặc
python main.py
```

---

## 🔍 Kiểm tra sau Nâng cấp

### 1. Kiểm tra Version
Mở ứng dụng và xem title bar:
```
Spark Runner GUI V5.0
```

### 2. Kiểm tra Logs folder
```bash
dir logs
```

Nên thấy:
```
logs/
  main_app.log
  main_app.json.log
```

### 3. Kiểm tra Configuration validation
1. Mở Settings tab
2. Nhập invalid container name (e.g., `-invalid`)
3. Lưu cấu hình
4. Kiểm tra console log:
```
⚠️ Configuration validation errors:
  - container: Container name must start with alphanumeric...
✅ Configuration automatically fixed
```

### 4. Kiểm tra Health Check
1. Stop Docker Desktop
2. Chạy Spark job
3. Kiểm tra logs:
```
⚠️ Docker is not running
🚀 Attempting to start Docker Desktop...
⏳ Waiting for Docker to start...
✅ Docker is now running!
```

### 5. Kiểm tra Database
```bash
sqlite3 spark_runner.db ".tables"
```

Output:
```
ai_code_history        performance_metrics  
job_history            upload_history       
user_preferences
```

---

## ⚙️ Configuration Changes

### Old Config (v4.x)
```json
{
  "container": "spark-worker",
  "master": "spark://spark-master:7077",
  "hdfs_host": "hdfs://namenode:8020",
  "hdfs_default_path": "/user/spark/data"
}
```

### New Config (v5.0) - Tương thích 100%
```json
{
  "container": "spark-worker",
  "master": "spark://spark-master:7077",
  "hdfs_host": "hdfs://namenode:8020",
  "hdfs_default_path": "/user/spark/data",
  "hdfs_container": "namenode",
  "auto_extract_archives": true,
  "delete_archive_after_extract": true,
  "compose_file": "d:\\...\\docker-compose.yml",
  "history": []
}
```

**Lưu ý**: Config cũ vẫn hoạt động. Các field mới sẽ được thêm tự động.

---

## 🐛 Troubleshooting

### Lỗi: "validation module not available"
**Nguyên nhân**: File `validation.py` không tồn tại hoặc có lỗi import

**Giải pháp**:
```bash
# Kiểm tra file tồn tại
dir run_spark_gui\validation.py

# Test import
python -c "from validation import Validator; print('OK')"
```

### Lỗi: "logging_config module not available"
**Nguyên nhân**: File `logging_config.py` không tồn tại

**Giải pháp**:
```bash
# Kiểm tra file
dir run_spark_gui\logging_config.py

# Test import
python -c "from logging_config import get_logger; print('OK')"
```

### Lỗi: Database locked
**Nguyên nhân**: Database đang được sử dụng bởi process khác

**Giải pháp**:
```bash
# Đóng tất cả instances của app
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Spark Runner*"

# Hoặc restart máy
```

### Logs không được tạo
**Nguyên nhân**: Permission issues hoặc disk full

**Giải pháp**:
```bash
# Kiểm tra quyền
icacls run_spark_gui\logs

# Kiểm tra disk space
wmic logicaldisk get caption,freespace
```

---

## 🔄 Rollback (Nếu cần)

Nếu gặp vấn đề với v5.0.0, bạn có thể rollback về v4.x:

### Bước 1: Restore từ backup
```bash
# Restore config
copy spark_runner_config.json.backup spark_runner_config.json

# Restore database
copy spark_runner.db.backup spark_runner.db
```

### Bước 2: Checkout v4.x branch
```bash
git checkout v4.x
```

### Bước 3: Restart application
```bash
START.bat
```

---

## 📊 Features Comparison

| Feature | v4.x | v5.0 |
|---------|------|------|
| **Basic Functionality** | ✅ | ✅ |
| **Docker Auto-start** | ✅ | ✅ Enhanced |
| **Error Handling** | ⚠️ Basic | ✅ Comprehensive |
| **Input Validation** | ⚠️ Limited | ✅ Complete |
| **Logging** | ❌ Prints only | ✅ Structured logs |
| **Health Monitoring** | ❌ Manual | ✅ Automatic |
| **Database Retry** | ❌ No | ✅ Yes |
| **Config Auto-fix** | ❌ No | ✅ Yes |
| **Error Messages** | ⚠️ Generic | ✅ Specific + Suggestions |
| **Performance** | ✅ Good | ✅ Better (WAL mode) |

---

## 🎓 Learning New Features

### 1. Using Logging
```python
from logging_config import get_logger

# Create logger for your module
logger = get_logger('my_script', level=logging.DEBUG)

# Log messages
logger.debug("Debug info")
logger.info("Normal operation")
logger.warning("Something unusual")
logger.error("Error occurred", exc_info=True)

# With context
from logging_config import LogContext
with LogContext(logger, user_id=123, action='upload'):
    logger.info("File uploaded")
```

### 2. Using Validation
```python
from validation import Validator, ConfigValidator

# Validate inputs
valid, error = Validator.is_valid_container_name(user_input)
if not valid:
    print(f"Invalid: {error}")

# Validate config
is_valid, errors = ConfigValidator.validate_config(my_config)
if not is_valid:
    for error in errors:
        print(error)
    
    # Auto-fix
    fixed = ConfigValidator.fix_config(my_config)
```

### 3. Using Health Check
```python
from health_check import health_checker

# Check specific component
result = health_checker.check_docker_daemon()
print(result)  # ✅ Docker Daemon: Docker is running

# Run all checks
results = health_checker.run_all_checks(config)
for name, result in results.items():
    print(f"{name}: {result}")

# Export report
health_checker.export_results('health_report.json')
```

---

## 📚 Additional Resources

### Documentation
- 📖 [CHANGELOG_V5.md](CHANGELOG_V5.md) - Chi tiết các thay đổi
- 📖 [README.md](README.md) - Hướng dẫn sử dụng tổng quan
- 📖 [USER_GUIDE.md](USER_GUIDE.md) - Hướng dẫn chi tiết cho người dùng
- 📖 [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Giải quyết vấn đề

### Code Examples
```bash
# Xem ví dụ validation
python run_spark_gui/validation.py

# Xem ví dụ logging
python run_spark_gui/logging_config.py

# Xem ví dụ health check
python run_spark_gui/health_check.py
```

---

## ✅ Post-Upgrade Tasks

### 1. Clean up old files (Optional)
```bash
# Xóa files không cần thiết
del run_spark_gui\quick_fix.py
del run_spark_gui\comprehensive_test.py
```

### 2. Update documentation
Nếu bạn có custom documentation, update để reflect các features mới.

### 3. Train team members
- Share CHANGELOG_V5.md với team
- Demo các features mới (logging, validation, health check)
- Update runbooks nếu có

### 4. Monitor for issues
- Check logs folder daily trong tuần đầu
- Monitor database size
- Review health check reports

---

## 🚀 Next Steps

Sau khi nâng cấp thành công:

1. **Explore new features**
   - Try validation với invalid inputs
   - Check logs folder
   - Run health checks

2. **Customize logging**
   - Adjust log levels nếu cần
   - Configure log rotation
   - Setup log monitoring

3. **Setup monitoring**
   - Schedule health checks
   - Setup alerts for unhealthy states
   - Monitor disk usage for logs

4. **Provide feedback**
   - Report bugs trên GitHub Issues
   - Suggest improvements
   - Share your experience

---

## 📞 Support

Nếu gặp vấn đề khi nâng cấp:

1. **Check logs**: `logs/main_app.log`
2. **Check health**: Run health check
3. **Search issues**: GitHub Issues
4. **Ask for help**: Create new issue

**GitHub**: https://github.com/Vo-Truong-Danh/GUI-Docker/issues

---

## 🎉 Kết luận

Chúc mừng! Bạn đã nâng cấp thành công lên v5.0.0.

Phiên bản này mang lại:
- ✅ Better reliability với enhanced error handling
- ✅ Better observability với comprehensive logging
- ✅ Better quality với input validation
- ✅ Better monitoring với health checks

Enjoy the new features! 🚀

---

**Last Updated**: 2025-10-13
**Version**: 5.0.0
