# 📦 Hướng Dẫn Build Spark Runner GUI

## 🎯 Tổng Quan

Build ứng dụng Spark Runner GUI thành file `.exe` standalone để dễ dàng phân phối và cài đặt.

---

## ✅ Yêu Cầu

### 1. **Python**
```powershell
# Check version
python --version  # Cần Python 3.8+

# Install Python nếu chưa có
# Download: https://www.python.org/downloads/
```

### 2. **PyInstaller**
```powershell
pip install pyinstaller
```

### 3. **Dependencies**
```powershell
pip install -r requirements.txt
```

---

## 🚀 Cách Build

### **Phương pháp 1: Sử dụng Script Tự Động (Khuyến Nghị)**

```powershell
# Mở PowerShell tại thư mục GUI-Docker
cd "d:\BaiTapSinhVien\TH BigData\GUI-Docker"

# Chạy script build
.\build.ps1
```

**Script sẽ tự động:**
1. ✅ Kiểm tra Python version
2. ✅ Cài đặt PyInstaller (nếu chưa có)
3. ✅ Cài đặt dependencies
4. ✅ Xóa build cũ
5. ✅ Build executable
6. ✅ Verify file .exe
7. ✅ Tạo release package

**Output:**
```
dist/
└── SparkRunnerGUI_v6.0.1_Windows/
    ├── SparkRunnerGUI.exe       ← Main executable
    ├── QUICKSTART.txt           ← Quick start guide
    ├── README.md
    ├── docker-compose.yml
    └── spark_runner_config.json
```

---

### **Phương pháp 2: Build Thủ Công**

#### A. **Clean previous build**
```powershell
Remove-Item -Path dist -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path build -Recurse -Force -ErrorAction SilentlyContinue
```

#### B. **Build với spec file (Khuyến nghị)**
```powershell
pyinstaller build_config.spec --noconfirm
```

#### C. **Build với command line**
```powershell
pyinstaller `
    --name="SparkRunnerGUI" `
    --onefile `
    --windowed `
    --add-data="run_spark_gui;run_spark_gui" `
    --add-data="docker-compose.yml;." `
    --hidden-import=yaml `
    --hidden-import=tkinter `
    --exclude-module=matplotlib `
    --noconfirm `
    "run_spark_gui\main.py"
```

---

## 📊 Build Options

### **PyInstaller Options Explained**

| Option | Mô tả |
|--------|-------|
| `--name="SparkRunnerGUI"` | Tên file .exe |
| `--onefile` | Đóng gói thành 1 file .exe duy nhất |
| `--windowed` | Ẩn console window (GUI app) |
| `--add-data` | Include thêm files/folders |
| `--hidden-import` | Import modules không tự detect |
| `--exclude-module` | Loại bỏ modules không cần |
| `--noconfirm` | Overwrite không hỏi |
| `--icon=icon.ico` | Thêm icon (optional) |

### **Console vs Windowed**

```powershell
# GUI app (no console) - User-friendly
--windowed

# Console app - For debugging
--console
```

---

## 🔧 Customize Build

### **1. Thêm Icon**
```powershell
# Tạo file icon.ico (256x256 recommended)
# Thêm vào build command:
--icon="icon.ico"
```

### **2. Thêm Version Info**
```python
# Tạo file version.txt
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(6, 0, 1, 0),
    prodvers=(6, 0, 1, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable('040904B0', [
        StringStruct('CompanyName', 'Your Company'),
        StringStruct('FileDescription', 'Spark Runner GUI'),
        StringStruct('FileVersion', '6.0.1'),
        StringStruct('ProductName', 'Spark Runner GUI'),
        StringStruct('ProductVersion', '6.0.1')])
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)

# Add to command:
--version-file=version.txt
```

### **3. Thêm Splash Screen**
```powershell
--splash="splash.png"
```

---

## 🐛 Troubleshooting

### **❌ Problem: "Python not found"**
```powershell
# Solution: Add Python to PATH
# Windows: System Properties → Environment Variables → PATH
# Add: C:\Python39\
```

### **❌ Problem: "Module not found" khi run .exe**
```powershell
# Solution: Add hidden import
pyinstaller ... --hidden-import=missing_module
```

### **❌ Problem: .exe quá lớn (>100MB)**
```powershell
# Solution 1: Exclude unused modules
--exclude-module=matplotlib
--exclude-module=numpy
--exclude-module=scipy

# Solution 2: Use UPX compression
--upx-dir="C:\upx"

# Solution 3: Use onedir instead of onefile (faster startup)
# Remove: --onefile
```

### **❌ Problem: "Failed to execute script"**
```powershell
# Solution: Build with console for debugging
pyinstaller ... --console  # See error messages

# Common causes:
# 1. Missing data files → Use --add-data
# 2. Hidden imports → Use --hidden-import
# 3. Runtime errors → Check code logic
```

### **❌ Problem: Slow startup**
```powershell
# Solution: Use --onedir instead of --onefile
# This creates a folder with multiple files but starts faster
```

---

## 📦 Distribution

### **1. Single .exe (Simple)**
```
dist/SparkRunnerGUI.exe  ← Just send this file!
```

**Pros:**
- ✅ Siêu đơn giản
- ✅ 1 file duy nhất

**Cons:**
- ❌ Startup chậm (extract temp files mỗi lần run)
- ❌ File size lớn hơn

---

### **2. Folder Package (Recommended)**
```
dist/SparkRunnerGUI_v6.0.1_Windows/
├── SparkRunnerGUI.exe
├── QUICKSTART.txt
├── README.md
├── docker-compose.yml
└── spark_runner_config.json
```

**Distribution:**
```powershell
# Nén thành ZIP
Compress-Archive -Path "dist/SparkRunnerGUI_v6.0.1_Windows" -DestinationPath "SparkRunnerGUI_v6.0.1_Windows.zip"

# Share ZIP file
# Users extract và run SparkRunnerGUI.exe
```

**Pros:**
- ✅ Startup nhanh
- ✅ Dễ troubleshoot
- ✅ Include docs và configs

---

### **3. Installer (Professional)**

**Sử dụng Inno Setup:**
```inno
; Install script
#define MyAppName "Spark Runner GUI"
#define MyAppVersion "6.0.1"
#define MyAppExeName "SparkRunnerGUI.exe"

[Setup]
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=installers
OutputBaseFilename=SparkRunnerGUI_Setup_v{#MyAppVersion}

[Files]
Source: "dist\SparkRunnerGUI.exe"; DestDir: "{app}"
Source: "README.md"; DestDir: "{app}"
Source: "docker-compose.yml"; DestDir: "{app}"

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
```

**Build installer:**
```powershell
# Download Inno Setup: https://jrsoftware.org/isdl.php
# Compile script → Get .exe installer
```

---

## ✅ Post-Build Checklist

- [ ] Test .exe on clean Windows machine
- [ ] Verify Docker Desktop requirement
- [ ] Check file size (should be < 100MB)
- [ ] Test all features work
- [ ] Verify config files load correctly
- [ ] Check error handling
- [ ] Test with/without Docker running
- [ ] Verify icon displays correctly (if added)

---

## 📝 Release Notes Template

```markdown
## Spark Runner GUI v6.0.1 - Release

### 📥 Download
- Windows: SparkRunnerGUI_v6.0.1_Windows.zip (XX MB)

### ✨ Features
- Spark Job Runner
- HDFS File Upload
- AI Code Generator
- Performance Monitor
- Docker Compose Editor

### 📋 Requirements
- Windows 10/11 (64-bit)
- Docker Desktop
- 4GB RAM minimum

### 🚀 Installation
1. Extract ZIP file
2. Run SparkRunnerGUI.exe
3. Start Docker Desktop
4. Start containers from Settings

### 🐛 Known Issues
- None

### 📞 Support
- GitHub: https://github.com/yourusername/GUI-Docker
- Issues: https://github.com/yourusername/GUI-Docker/issues
```

---

## 🎯 Quick Commands

```powershell
# Full build
.\build.ps1

# Clean build
Remove-Item dist, build -Recurse -Force; pyinstaller build_config.spec --noconfirm

# Debug build (with console)
pyinstaller build_config.spec --noconfirm --console

# Test executable
.\dist\SparkRunnerGUI.exe

# Create ZIP
Compress-Archive -Path "dist\SparkRunnerGUI_v6.0.1_Windows" -DestinationPath "Release.zip"
```

---

## 📚 Resources

- **PyInstaller Docs**: https://pyinstaller.org/en/stable/
- **Inno Setup**: https://jrsoftware.org/isinfo.php
- **Icon Creator**: https://www.favicon-generator.org/
- **UPX Compressor**: https://upx.github.io/

---

## ✨ Done!

Sau khi build xong, bạn có:
- ✅ File `.exe` standalone
- ✅ Release package với docs
- ✅ Ready to distribute!

User chỉ cần:
1. Install Docker Desktop
2. Run `.exe`
3. Enjoy! 🚀
