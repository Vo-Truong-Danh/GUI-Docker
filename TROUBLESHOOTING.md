# 🛠️ Troubleshooting Guide - Spark Runner GUI v4.4.3

## 🚀 Quick Start (No Issues)

### Khởi động an toàn:
```bash
# Windows
START.bat

# hoặc
python safe_start.py
```

Nếu tất cả OK, ứng dụng sẽ mở ngay lập tức!

---

## ⚠️ Gặp lỗi? - Hướng dẫn khắc phục

### 🔧 Bước 1: Chạy Quick Fix
```bash
python quick_fix.py
```

Tool này sẽ **tự động sửa**:
- ✅ Missing configuration file
- ✅ Corrupted database
- ✅ Stale cache files
- ✅ Python bytecode cleanup

### 🧪 Bước 2: Chạy Comprehensive Test
```bash
python comprehensive_test.py
```

Kiểm tra toàn bộ hệ thống:
- ✅ All modules import correctly
- ✅ Database accessible
- ✅ Docker utilities working
- ✅ Enhanced features enabled

---

## 🐛 Lỗi thường gặp & Cách fix

### 1. ❌ "ModuleNotFoundError: No module named 'tkinter'"

**Nguyên nhân:** Thiếu tkinter

**Fix (Windows):**
```bash
# tkinter đi kèm Python, reinstall Python với tkinter option
# Download từ: https://www.python.org/
# Check "tcl/tk and IDLE" khi cài đặt
```

**Fix (Ubuntu/Debian):**
```bash
sudo apt-get install python3-tk
```

**Fix (macOS):**
```bash
brew install python-tk
```

---

### 2. ❌ "DatabaseError: database is locked"

**Nguyên nhân:** Database đang được process khác sử dụng

**Fix:**
```bash
# Đóng tất cả instances của app
# Xóa file lock
del spark_runner.db-journal  # Windows
rm spark_runner.db-journal   # Linux/Mac

# Hoặc dùng quick fix
python quick_fix.py
```

---

### 3. ❌ "Docker not found" hoặc "Docker not running"

**Fix tự động:** App sẽ tự động hỏi khởi động Docker Desktop!

**Fix thủ công:**
```bash
# Mở Docker Desktop
# Hoặc (Linux):
sudo systemctl start docker
```

**Verify:**
```bash
docker --version
docker info
```

---

### 4. ❌ "Configuration file corrupted"

**Fix tự động:**
```bash
python quick_fix.py
```

**Fix thủ công:**
```bash
# Xóa file cũ
del spark_runner_config.json  # Windows
rm spark_runner_config.json   # Linux/Mac

# Chạy app, nó sẽ tạo config mới
python main.py
```

---

### 5. ❌ "ImportError: cannot import name 'xxx'"

**Nguyên nhân:** Module files bị thiếu hoặc outdated

**Check files exist:**
```bash
dir *.py  # Windows
ls *.py   # Linux/Mac
```

**Required files:**
- ✅ main.py
- ✅ spark_backend.py
- ✅ docker_utils.py
- ✅ system_utils.py
- ✅ database.py
- ✅ spark_runner_tab_v4_clean.py
- ✅ hdfs_upload_tab_v4_clean.py
- ✅ (và các tab khác...)

**Fix:** Re-download missing files từ repository

---

### 6. ❌ "Permission denied" hoặc "Access is denied"

**Nguyên nhân:** Không có quyền write vào thư mục

**Fix (Windows - Run as Administrator):**
```bash
# Right-click START.bat → Run as Administrator
```

**Fix (Linux/Mac):**
```bash
chmod +x START.bat
sudo chown -R $USER:$USER .
```

---

### 7. ❌ "Port already in use"

**Nguyên nhân:** Port đã được sử dụng bởi process khác

**Check ports:**
```bash
# Windows
netstat -ano | findstr :8080
netstat -ano | findstr :9870

# Linux/Mac
lsof -i :8080
lsof -i :9870
```

**Fix trong Settings Tab:**
1. Mở Settings tab
2. Thay đổi ports
3. Click "Save Configuration"

---

### 8. ❌ "Docker compose not found"

**Fix (Windows/Mac):** Docker Desktop đã bao gồm docker-compose

**Fix (Linux):**
```bash
# Install docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker-compose --version
```

---

### 9. ❌ "Memory Error" hoặc "Out of Memory"

**Nguyên nhân:** Spark job quá lớn

**Fix trong Settings:**
1. Mở Settings tab
2. Tăng memory limits:
   - Executor Memory: 2g → 4g
   - Driver Memory: 1g → 2g
3. Save và restart containers

---

### 10. ❌ "Connection refused" hoặc "Container not found"

**Nguyên nhân:** Docker containers chưa start

**Fix:**
1. Mở Docker Compose tab
2. Click "Up" button
3. Đợi containers start (~30s)
4. Verify status = "running"

---

## 🔍 Advanced Diagnostics

### Check System Health:
```bash
python comprehensive_test.py
```

### Check Docker Status:
```bash
python docker_utils.py
```

### Check Database:
```bash
python -c "from database import db; print(db.get_job_stats())"
```

### Check Cache:
```bash
python -c "from system_utils import cache_manager; print(cache_manager.get_stats())"
```

---

## 📝 Log Files Location

### Application Logs:
- Windows: `%USERPROFILE%\.spark_runner\logs\`
- Linux/Mac: `~/.spark_runner/logs/`

### Docker Logs:
```bash
docker logs spark-master
docker logs spark-worker
docker logs namenode
```

---

## 🆘 Still Having Issues?

### 1. Collect Diagnostic Info:
```bash
python comprehensive_test.py > test_results.txt
docker ps -a > docker_status.txt
docker-compose logs > docker_logs.txt
```

### 2. Check Versions:
```bash
python --version
docker --version
docker-compose --version
```

### 3. Common Solutions:
- ✅ Restart computer
- ✅ Reinstall Docker Desktop
- ✅ Update Python to 3.8+
- ✅ Clear all Docker volumes: `docker system prune -a`
- ✅ Fresh install of app

### 4. Manual Reset (Nuclear Option):
```bash
# Backup data first!
python quick_fix.py

# Stop everything
docker-compose down -v

# Clean database
del spark_runner.db  # Windows
rm spark_runner.db   # Linux/Mac

# Clean config
del spark_runner_config.json

# Restart fresh
python safe_start.py
```

---

## ✅ Prevention Tips

### Daily:
- ✅ Close app properly (not force kill)
- ✅ Keep Docker Desktop running
- ✅ Regular database backups

### Weekly:
- ✅ Run `python quick_fix.py`
- ✅ Clean Docker images: `docker system prune`
- ✅ Check disk space

### Monthly:
- ✅ Update Docker Desktop
- ✅ Update Python packages
- ✅ Review logs and metrics

---

## 📞 Support Checklist

Trước khi báo lỗi, hãy chạy:

```bash
# 1. Quick fix
python quick_fix.py

# 2. Comprehensive test
python comprehensive_test.py

# 3. Docker test
python docker_utils.py

# 4. Collect info
python --version > system_info.txt
docker --version >> system_info.txt
docker ps -a >> system_info.txt
```

Gửi kết quả các files: `test_results.txt`, `system_info.txt`

---

## 🎯 Quick Reference

| Problem | Solution |
|---------|----------|
| Import error | `python quick_fix.py` |
| Database locked | Close all instances, delete `.db-journal` |
| Docker not found | Check Docker Desktop running |
| Port conflict | Change ports in Settings tab |
| Memory error | Increase memory in Settings |
| Config corrupted | `python quick_fix.py` |
| Can't start | `python safe_start.py` |

---

**Version:** 4.4.3  
**Last Updated:** October 13, 2025  
**Status:** Production Ready
