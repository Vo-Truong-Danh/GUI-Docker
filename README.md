# 🚀 Spark Runner GUI V4.2.7 - Clean Professional Edition

![Version](https://img.shields.io/badge/version-4.2.7-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![UI](https://img.shields.io/badge/UI-Clean%20Professional-purple.svg)
![Status](https://img.shields.io/badge/status-production-success.svg)

**Modern, clean, and professional GUI for managing Apache Spark jobs on Docker containers.**

Inspired by GitHub, VS Code, and Notion - designed for developers who value simplicity and efficiency.

> **🔧 New in v4.2.7:** HDFS path fix - Files now upload to correct directory with verification!  
> **🔧 New in v4.2.4:** Enhanced logging & config management - See everything that's happening!  
> **🔧 New in v4.2.3:** HDFS Upload fixed - ThreadPoolExecutor for reliable uploads!  
> **🔥 New in v4.2.2:** Proactive cleanup - Always works in ONE attempt!

---

## 📑 Mục Lục

- [✨ Tính Năng](#-tính-năng)
- [📸 Screenshots](#-screenshots)
- [🔧 Yêu Cầu Hệ Thống](#-yêu-cầu-hệ-thống)
- [⚙️ Cài Đặt](#️-cài-đặt)
- [🚀 Sử Dụng](#-sử-dụng)
- [📖 Hướng Dẫn Chi Tiết](#-hướng-dẫn-chi-tiết)
- [⌨️ Phím Tắt](#️-phím-tắt)
- [🛠️ Cấu Hình](#️-cấu-hình)
- [❓ FAQ](#-faq)
- [🐛 Troubleshooting](#-troubleshooting)
- [📝 Changelog](#-changelog)
- [👨‍💻 Đóng Góp](#-đóng-góp)
- [📄 License](#-license)

---

## ✨ Tính Năng

### 🎯 Core Features

#### 🚀 **Spark Runner Tab**
- ✅ **Auto Run Mode**: Tự động copy file và submit Spark job
- ✅ **Step-by-Step Execution**: Chạy từng bước thủ công
- ✅ **Docker Management**: Start/Stop/Restart containers
- ✅ **Smart Conflict Detection**: Tự động phát hiện & giải quyết container name conflicts 🆕
- ✅ **Real-time Logs**: Xem output và errors trực tiếp
- ✅ **File History**: Lưu lịch sử 10 files gần nhất
- ✅ **Command Generation**: Tạo Docker commands tự động
- ✅ **Compose File Editor**: Chỉnh sửa docker-compose.yml với validation 🆕
- ✅ **Docker Status Monitor**: Kiểm tra trạng thái containers
- ✅ **Path Management**: Quản lý đường dẫn docker-compose file với browse button 🆕

#### 📤 **HDFS Upload Tab**
- ✅ Upload nhiều files cùng lúc
- ✅ Hỗ trợ đa dạng file types (CSV, JSON, Parquet, TXT, ZIP...)
- ✅ Auto-extract compressed files
- ✅ Batch operations với progress tracking
- ✅ File validation trước khi upload
- ✅ HDFS connection testing

#### 🤖 **AI Code Generator Tab**
- ✅ Tạo PySpark code từ mô tả văn bản
- ✅ Templates có sẵn (Word Count, CSV Analysis, Data Filter...)
- ✅ Syntax highlighting
- ✅ Code validation
- ✅ Export và chạy trực tiếp trong Spark Tab
- ✅ Custom templates

#### 📊 **Performance Monitor Tab** *(NEW in v3.0)*
- ✅ Real-time monitoring Docker containers
- ✅ Track CPU, Memory, Network I/O
- ✅ Multiple views: Table, Detail, History
- ✅ Auto-refresh với configurable interval
- ✅ Export statistics to JSON
- ✅ Alert cho high resource usage

### 🎨 **UI/UX Enhancements**

- 🎨 Modern Material Design interface
- 🌈 Color-coded logs (Success/Error/Warning/Info)
- 💡 Tooltips với hướng dẫn chi tiết
- 🖱️ Context menus (Right-click)
- ⌨️ Keyboard shortcuts
- 📱 Responsive layout
- 🔄 Auto-save configuration
- 💾 Backup/Restore settings
- 🎯 Drag & Drop support

### 🔧 **Advanced Features**

- 🔄 Retry logic với exponential backoff
- 🧵 Thread pool cho background operations
- 📝 Comprehensive logging system
- 🔍 Input validation và error handling
- 💪 Robust error recovery
- 📊 Statistics và analytics
- 🔐 Safe cleanup on exit

---

## 📸 Screenshots

### Main Interface
![Main UI](docs/screenshots/main.png)

### Spark Runner Tab
![Spark Runner](docs/screenshots/spark_runner.png)

### Performance Monitor
![Performance Monitor](docs/screenshots/performance.png)

---

## 🔧 Yêu Cầu Hệ Thống

### Phần Mềm

- **Python**: 3.7 trở lên
- **Docker Desktop**: Latest version
- **docker-compose**: v1.29+ hoặc Docker Compose V2
- **OS**: Windows 10/11, macOS, Linux

### Python Packages

```txt
pyspark
pyyaml
tkinter (built-in)
```

### Hardware Khuyến Nghị

- **RAM**: 8GB minimum, 16GB recommended
- **CPU**: Dual-core minimum, Quad-core recommended
- **Disk**: 10GB free space
- **Network**: Stable internet cho pulling Docker images

---

## ⚙️ Cài Đặt

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/GUI-Docker.git
cd GUI-Docker/run_spark_gui
```

### 2. Cài Đặt Python Dependencies

```bash
pip install -r requirements.txt
```

Hoặc:

```bash
pip install pyspark pyyaml
```

### 3. Cài Đặt Docker Desktop

**Windows:**
1. Download từ https://www.docker.com/products/docker-desktop
2. Chạy installer và follow hướng dẫn
3. Khởi động lại máy nếu cần
4. Mở Docker Desktop và đợi khởi động xong

**macOS:**
```bash
brew install --cask docker
```

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo systemctl start docker
sudo systemctl enable docker
```

### 4. Verify Installation

```bash
docker --version
docker-compose --version
python --version
```

---

## 🚀 Sử Dụng

### Quick Start

#### Windows:

```bash
# Cách 1: Double-click
run.bat

# Cách 2: Command line
python main.py
```

#### macOS/Linux:

```bash
python3 main.py
```

### Workflow Cơ Bản

#### 1️⃣ **Khởi Động Docker Containers**

1. Mở tab **🚀 Spark Runner**
2. Click **START CONTAINERS** trong phần Docker Management
3. Đợi containers khởi động (có thể mất 1-2 phút lần đầu)
4. Kiểm tra status: **CHECK STATUS**

#### 2️⃣ **Chạy Spark Job**

**Auto Mode (Khuyến Nghị):**
1. Click **📂 Browse** để chọn file Python
2. Click **RUN JOB NOW** (Ctrl+R)
3. Xem kết quả trong log

**Manual Mode:**
1. Chọn file Python
2. Click **GENERATE COMMANDS** (F5)
3. Chạy từng bước:
   - **1. COPY FILE**
   - **2. OPEN BASH** (optional)
   - **3. SUBMIT JOB**

#### 3️⃣ **Upload Files to HDFS**

1. Mở tab **📤 HDFS Upload**
2. Click **➕ Add Files** hoặc **📂 Add Folder**
3. Configure HDFS path
4. Click **▶️ Start Upload**

#### 4️⃣ **Generate PySpark Code**

1. Mở tab **🤖 AI Code Generator**
2. Nhập mô tả yêu cầu hoặc chọn template
3. Click **✨ Generate Code**
4. Click **▶️ Run in Spark Tab** để chạy ngay

#### 5️⃣ **Monitor Performance**

1. Mở tab **📊 Performance Monitor**
2. Click **▶️ Start Monitoring**
3. Xem real-time stats
4. Export data nếu cần: **💾 Export Stats**

---

## 📖 Hướng Dẫn Chi Tiết

### Docker Management

#### Start Containers

```
Bước 1: Click "START CONTAINERS"
Bước 2: Đợi containers pull images (lần đầu tiên)
Bước 3: Verify status trong log
```

**Containers được khởi động:**
- `namenode`: HDFS NameNode (port 9870, 8020)
- `datanode`: HDFS DataNode
- `spark-master`: Spark Master (port 8080, 7077)
- `spark-worker`: Spark Worker (port 8081)

#### Stop Containers

```
Click "STOP CONTAINERS"
Confirm dialog
Đợi containers shutdown gracefully
```

#### Edit Compose File

1. Click **✏️ Edit** trong Docker Management
2. Chỉnh sửa docker-compose.yml
3. Click **✓ Validate** để kiểm tra syntax
4. Click **💾 Save** để lưu
5. **Restart containers** để áp dụng thay đổi

### HDFS Operations

#### Upload Single File

```python
1. Click "➕ Add Files"
2. Chọn file từ file browser
3. Set HDFS destination path
4. Click "▶️ Start Upload"
```

#### Upload Multiple Files

```python
1. Click "📂 Add Folder"
2. Chọn folder chứa files
3. Files tự động được thêm vào list
4. Configure options:
   - Auto-extract archives
   - Delete archive after extract
5. Click "▶️ Start Upload"
```

#### Batch Upload with Progress

```python
# Files được upload song song
# Progress bar hiển thị tổng tiến độ
# Individual status cho từng file
# Auto-retry nếu upload failed
```

### AI Code Generation

#### Using Templates

```python
# Template: Word Count
1. Click "Word Count" template
2. Update HDFS path và App name
3. Click "✨ Generate Code"
4. Code tự động fill vào editor

# Custom Description
1. Nhập mô tả chi tiết trong text area
2. Specify input/output paths
3. Generate và review code
4. Edit nếu cần
5. Save hoặc Run
```

#### Available Templates

1. **Word Count**: Đếm số từ trong file text
2. **CSV Analysis**: Phân tích file CSV
3. **Data Filter**: Lọc dữ liệu theo điều kiện
4. **Top N**: Tìm top N records

### Performance Monitoring

#### Real-time Monitoring

```python
# Start monitoring
1. Set update interval (1-10 seconds)
2. Click "▶️ Start Monitoring"
3. Switch giữa các views:
   - 📊 Table View: Tổng quan
   - 📋 Detail View: Chi tiết
   - 📉 History: Timeline

# Stop monitoring
Click "⏹️ Stop Monitoring"
```

#### Export Statistics

```python
1. Click "💾 Export Stats"
2. Chọn location và filename
3. Data được export dạng JSON
4. Có thể import lại sau
```

---

## ⌨️ Phím Tắt

### Global Shortcuts

| Phím       | Chức Năng                  |
|------------|----------------------------|
| `Ctrl+O`   | Mở file browser            |
| `Ctrl+R`   | Auto run Spark job         |
| `F5`       | Generate commands          |
| `F1`       | Hiển thị help              |
| `Esc`      | Dừng operation hiện tại    |
| `Ctrl+S`   | Export log                 |
| `Ctrl+L`   | Clear log                  |
| `Ctrl+C`   | Copy commands/selection    |
| `Alt+F4`   | Thoát application          |

### Context Menu Shortcuts

**Right-click trên file entry:**
- 📂 Browse...
- 📋 Paste
- ✖ Clear
- 📂 Open in Explorer

**Right-click trên log:**
- 📋 Copy Selection
- 🔍 Select All
- 🗑️ Clear Log
- 💾 Export Log

**Right-click trên command text:**
- 📋 Copy All
- 🔍 Select All
- 💾 Save to file

---

## 🛠️ Cấu Hình

### Configuration File

File config: `spark_runner_config.json`

```json
{
  "container": "spark-worker",
  "master": "spark://spark-master:7077",
  "hdfs_container": "namenode",
  "hdfs_host": "hdfs://namenode:8020",
  "hdfs_default_path": "/user/spark/data",
  "auto_extract_archives": true,
  "delete_archive_after_extract": true,
  "compose_file": "docker-compose.yml",
  "history": []
}
```

### Thay Đổi Configuration

#### Through GUI:

1. **Settings** menu → **Lưu cấu hình hiện tại**
2. Hoặc click **💾 Lưu** trong Configuration section

#### Manual Edit:

```bash
# Open config file
notepad spark_runner_config.json  # Windows
nano spark_runner_config.json     # Linux/Mac

# Edit values
# Save and restart app
```

### Backup Configuration

```
Menu → Settings → Backup Configuration
Chọn location để save backup
File được save với timestamp
```

### Restore Configuration

```
Menu → Settings → Restore Configuration
Chọn backup file
Confirm overwrite
Restart application
```

### Reset to Defaults

```
Menu → Settings → Reset về mặc định
Hoặc click "↺ Reset" trong Configuration section
```

---

## ❓ FAQ

### Q1: Docker Desktop không khởi động?

**A:** 
```
1. Check Windows/macOS services
2. Restart Docker Desktop manually
3. Check system requirements
4. Run as Administrator (Windows)
5. Check logs: Docker Desktop → Settings → Troubleshoot
```

### Q2: Containers không start được?

**A:**
```
1. Check Docker Desktop đang chạy
2. Verify docker-compose.yml syntax
3. Check port conflicts (8080, 8081, 9870...)
4. Pull images manually:
   docker-compose pull
5. Clean và rebuild:
   docker-compose down -v
   docker-compose up -d
```

### Q3: Spark job failed?

**A:**
```
1. Check file path đúng chưa
2. Verify Python syntax
3. Check container logs:
   docker logs spark-worker
4. Verify Spark master URL
5. Check resource availability
```

### Q4: HDFS upload failed?

**A:**
```
1. Test HDFS connection
2. Check HDFS path permissions
3. Verify namenode đang running
4. Check file size limits
5. Review HDFS logs
```

### Q5: Performance Monitor không hiển thị data?

**A:**
```
1. Verify containers đang running
2. Check Docker stats command:
   docker stats --no-stream
3. Restart monitoring
4. Check permissions
```

---

## 🐛 Troubleshooting

### Common Issues

#### Issue 1: Module Import Errors

```bash
# Error: ModuleNotFoundError: No module named 'pyspark'
Solution:
pip install pyspark pyyaml

# Or upgrade
pip install --upgrade pyspark pyyaml
```

#### Issue 2: Permission Denied (Linux/Mac)

```bash
# Error: Permission denied for docker commands
Solution:
sudo usermod -aG docker $USER
newgrp docker

# Or run with sudo
sudo python3 main.py
```

#### Issue 3: Port Already in Use

```bash
# Error: Port 8080 is already allocated
Solution:
1. Find process using port:
   netstat -ano | findstr :8080  # Windows
   lsof -i :8080                 # Mac/Linux

2. Kill process or edit docker-compose.yml:
   ports:
     - "8082:8080"  # Change external port
```

#### Issue 4: Docker Compose Not Found

```bash
# Error: docker-compose: command not found
Solution:
# Install Docker Compose V2 (recommended)
docker compose version

# Or install standalone:
pip install docker-compose
```

#### Issue 5: Encoding Errors

```bash
# Error: UnicodeDecodeError
Solution:
# Edit script encoding line:
# -*- coding: utf-8 -*-

# Or set environment variable:
set PYTHONIOENCODING=utf-8  # Windows
export PYTHONIOENCODING=utf-8  # Linux/Mac
```

### Debug Mode

```python
# Enable verbose logging
# Edit main.py:
import logging
logging.basicConfig(level=logging.DEBUG)

# Run app và check detailed logs
```

### Getting Help

1. **Check Logs**: Menu → Help → View Logs
2. **Export Logs**: Ctrl+S
3. **GitHub Issues**: https://github.com/yourusername/GUI-Docker/issues
4. **Documentation**: https://github.com/yourusername/GUI-Docker/wiki

---

## 📝 Changelog

### Version 3.0.0 (2025-01-12)

#### 🎉 Major Updates

- ✨ **NEW:** Performance Monitor tab
  - Real-time Docker stats
  - CPU, Memory, Network monitoring
  - Multiple view modes
  - Statistics export

- 🎨 **UI/UX Overhaul:**
  - Modern Material Design
  - Enhanced color scheme
  - Better tooltips
  - Responsive layout
  - Auto-save configuration

- 🚀 **Performance Improvements:**
  - Thread pool optimization
  - Better error handling
  - Retry logic with backoff
  - Resource cleanup

- 🔧 **Enhanced Features:**
  - Compose file editor
  - Template management
  - Backup/Restore config
  - Advanced validation

#### 🐛 Bug Fixes

- Fixed Docker Desktop auto-start
- Resolved encoding issues
- Fixed memory leaks
- Improved error messages

#### 📝 Documentation

- Comprehensive README
- User guide
- API documentation
- Troubleshooting guide

### Version 2.4.2 (Previous)

- Basic functionality
- Spark runner
- HDFS upload
- AI code generator

---

## 👨‍💻 Đóng Góp

Contributions are welcome! 🎉

### How to Contribute

1. **Fork repository**
2. **Create feature branch**
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **Commit changes**
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
4. **Push to branch**
   ```bash
   git push origin feature/AmazingFeature
   ```
5. **Open Pull Request**

### Coding Standards

- Follow PEP 8 style guide
- Add docstrings to functions
- Write meaningful commit messages
- Test before submitting PR

### Reporting Bugs

Use GitHub Issues với template:

```markdown
**Bug Description:**
Clear và concise description

**Steps to Reproduce:**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior:**
What should happen

**Screenshots:**
If applicable

**Environment:**
- OS: [e.g., Windows 11]
- Python version: [e.g., 3.9]
- Docker version: [e.g., 24.0.5]
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

```
Copyright (c) 2025 Spark Runner GUI Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 🙏 Acknowledgments

- **Apache Spark** - Distributed computing framework
- **Docker** - Containerization platform
- **Python Tkinter** - GUI framework
- **GitHub Copilot** - AI coding assistant

---

## 📞 Contact & Support

- **GitHub**: https://github.com/yourusername/GUI-Docker
- **Issues**: https://github.com/yourusername/GUI-Docker/issues
- **Email**: support@example.com
- **Documentation**: https://github.com/yourusername/GUI-Docker/wiki

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/GUI-Docker&type=Date)](https://star-history.com/#yourusername/GUI-Docker&Date)

---

<div align="center">

**Made with ❤️ by developers, for developers**

[⬆ Back to Top](#-spark-runner-gui---pro-edition-v300)

</div>
