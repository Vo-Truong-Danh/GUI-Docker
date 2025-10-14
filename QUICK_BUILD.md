# 🚀 QUICK BUILD GUIDE - Spark Runner GUI

## ⚡ Cách Nhanh Nhất (Recommended)

### Bước 1: Enable PowerShell Scripts (chỉ 1 lần)
```powershell
# Mở PowerShell AS ADMINISTRATOR
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Chọn [Y] Yes
```

### Bước 2: Build
```powershell
cd "d:\BaiTapSinhVien\TH BigData\GUI-Docker"
.\build.ps1
```

Đợi 2-5 phút → Done! ✅

---

## 🔧 Cách Manual (nếu PowerShell bị disable)

### Bước 1: Cài PyInstaller
```powershell
pip install pyinstaller
```

### Bước 2: Build
```powershell
cd "d:\BaiTapSinhVien\TH BigData\GUI-Docker"

pyinstaller `
    --name="SparkRunnerGUI" `
    --onefile `
    --windowed `
    --add-data="run_spark_gui;run_spark_gui" `
    --add-data="docker-compose.yml;." `
    --add-data="spark_runner_config.json;." `
    --hidden-import=yaml `
    --hidden-import=tkinter `
    --exclude-module=matplotlib `
    --exclude-module=numpy `
    --noconfirm `
    "run_spark_gui\main.py"
```

### Bước 3: Lấy file .exe
```
dist\SparkRunnerGUI.exe  ← Đây là file cần distribute!
```

---

## 📦 Output

Sau khi build xong:

```
GUI-Docker/
├── dist/
│   └── SparkRunnerGUI.exe  ← Main executable (30-50 MB)
├── build/                   ← Temp files (có thể xóa)
└── SparkRunnerGUI.spec      ← Build config (có thể xóa)
```

---

## 🎯 Test Executable

```powershell
# Chạy thử
cd dist
.\SparkRunnerGUI.exe

# Hoặc double-click vào file
```

---

## 📤 Distribution

### Cách 1: Single File (Đơn giản)
```
Gửi file: SparkRunnerGUI.exe (30-50 MB)
User chỉ cần: Docker Desktop + Run file .exe
```

### Cách 2: Package (Professional)
```powershell
# Tạo folder release
New-Item -ItemType Directory -Path "SparkRunnerGUI_v6.0.1_Windows"

# Copy files
Copy-Item "dist\SparkRunnerGUI.exe" "SparkRunnerGUI_v6.0.1_Windows\"
Copy-Item "README.md" "SparkRunnerGUI_v6.0.1_Windows\"
Copy-Item "docker-compose.yml" "SparkRunnerGUI_v6.0.1_Windows\"

# Tạo ZIP
Compress-Archive -Path "SparkRunnerGUI_v6.0.1_Windows" -DestinationPath "SparkRunnerGUI_v6.0.1_Windows.zip"

# Share ZIP file
```

---

## ❓ Troubleshooting

### Problem: "PowerShell script disabled"
```powershell
# Solution: Run as Administrator
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problem: "Module not found" error
```powershell
# Solution: Add missing module
pyinstaller ... --hidden-import=missing_module_name
```

### Problem: Build quá lâu
```
Normal! Build lần đầu mất 2-5 phút
Build sau sẽ nhanh hơn
```

### Problem: File .exe quá lớn
```powershell
# Normal: 30-50 MB là OK
# Giảm size: Thêm --exclude-module
```

---

## ✅ Checklist

- [ ] Python 3.8+ installed
- [ ] PyInstaller installed (`pip install pyinstaller`)
- [ ] Build completed (check `dist/SparkRunnerGUI.exe`)
- [ ] Test executable works
- [ ] Create release package (optional)
- [ ] Share with users!

---

## 🎉 Done!

User chỉ cần:
1. ✅ Install Docker Desktop
2. ✅ Run SparkRunnerGUI.exe
3. ✅ Start containers từ Settings
4. ✅ Enjoy!

**No Python installation required for end users!** 🚀

---

## 📚 Full Documentation

Xem chi tiết: `BUILD_INSTRUCTIONS.md`
