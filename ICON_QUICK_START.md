# 🎨 Quick Start: Thêm Icon Cho Ứng Dụng

## ⚡ Cách Nhanh Nhất (Tự Động)

```powershell
# Bước 1: Tạo icon tự động
python create_icon.py

# Bước 2: Build với icon
.\build.bat

# Hoặc dùng build_config.spec
pyinstaller build_config.spec --noconfirm
```

**Xong!** Icon sẽ tự động được thêm vào `SparkRunnerGUI.exe`

---

## 📝 Chi Tiết Từng Bước

### **1. Tạo Icon**

#### Option A: Tự động (Khuyến nghị)
```powershell
# Cài Pillow nếu chưa có
pip install Pillow

# Tạo icon
python create_icon.py
```

**Kết quả:**
- ✅ `icon.ico` - Icon chính (256x256 + multiple sizes)
- ✅ `icon_preview.png` - Preview full size
- ✅ `icon_small.png` - Preview nhỏ

#### Option B: Tự tạo
1. Tạo ảnh PNG 256x256 pixels
2. Convert sang ICO:
```python
from PIL import Image
img = Image.open('logo.png')
img.save('icon.ico', format='ICO', sizes=[(16,16), (32,32), (48,48), (256,256)])
```

#### Option C: Download online
- Tải icon .ico từ internet
- Đổi tên thành `icon.ico`
- Copy vào folder `GUI-Docker/`

### **2. Build Với Icon**

#### Cách 1: Dùng build.bat (Tự động)
```powershell
.\build.bat
```
Script tự động:
- ✅ Check icon có tồn tại không
- ✅ Tạo icon tự động nếu chưa có
- ✅ Build với icon

#### Cách 2: Dùng build_config.spec
```powershell
pyinstaller build_config.spec --noconfirm
```

#### Cách 3: Command line trực tiếp
```powershell
pyinstaller ^
    --name=SparkRunnerGUI ^
    --onefile ^
    --windowed ^
    --icon=icon.ico ^
    --add-data=run_spark_gui;run_spark_gui ^
    run_spark_gui\main.py
```

### **3. Verify Icon**

```powershell
# Check file executable
cd dist
dir SparkRunnerGUI.exe

# Right-click → Properties → See icon
explorer .
```

---

## 🎯 Màu Sắc & Theme

### **Icon Mặc Định (create_icon.py)**
```
Background: #0F172A (Dark blue)
Primary: #FF6B00 (Orange - Spark)
Accent: #FFD700 (Gold)
Text: #FFFFFF (White)
Symbol: "S" (Bold, centered)
```

### **Customize Icon**

Edit `create_icon.py`:

```python
# Thay đổi màu nền
img = Image.new('RGBA', (size, size), color=(15, 23, 42, 255))  # Your color

# Thay đổi chữ
text = "SR"  # Spark Runner
# hoặc
text = "⚡"  # Lightning emoji

# Thay đổi màu chữ
draw.text((text_x, text_y), text, font=font, fill=(255, 107, 0, 255))  # Orange
```

---

## 🔍 Troubleshooting

### Problem: Icon không hiển thị

**Solution 1: Check file**
```powershell
Test-Path icon.ico
# Should return: True
```

**Solution 2: Clear cache**
```powershell
# Windows icon cache
ie4uinit.exe -show

# Rebuild
Remove-Item dist, build -Recurse -Force
.\build.bat
```

**Solution 3: Verify build log**
```powershell
# Check PyInstaller output
# Should see: "Using icon from icon.ico"
```

### Problem: Icon bị vỡ/mờ

**Solution:** Tạo lại với multiple sizes
```python
img.save('icon.ico', format='ICO', sizes=[
    (16, 16),   # Small
    (32, 32),   # Medium
    (48, 48),   # Large
    (64, 64),   # Extra Large
    (128, 128), # HD
    (256, 256)  # Full HD
])
```

---

## 💡 Tips

### **1. Professional Icon Design**
```
✅ Simple & clean design
✅ Clear at 16x16 pixels
✅ High contrast colors
✅ Flat design (no gradients if possible)
✅ Matches app theme
```

### **2. Best Icon Formats**
```
Primary: .ICO (Windows native)
Source: .PNG (editing)
Vector: .SVG (scalable)
```

### **3. Icon Testing**
```powershell
# Test at different sizes
# - Taskbar (32x32)
# - Desktop (48x48)
# - Alt+Tab (256x256)
# - File Explorer (various)
```

---

## 📦 Complete Example

```powershell
# 1. Navigate to project
cd "d:\BaiTapSinhVien\TH BigData\GUI-Docker"

# 2. Create icon
python create_icon.py

# 3. Preview icon
start icon_preview.png

# 4. Build with icon
.\build.bat

# 5. Test
cd dist
.\SparkRunnerGUI.exe

# 6. Verify icon
# - Check icon in file explorer
# - Check icon in taskbar when running
# - Right-click EXE → Properties → Icon tab
```

---

## ✨ Result

After completing:
- ✅ SparkRunnerGUI.exe has professional icon
- ✅ Icon visible in:
  - File Explorer
  - Taskbar
  - Alt+Tab switcher
  - Start menu (if pinned)
  - Desktop shortcut
- ✅ Branded, professional look

---

## 🎨 Custom Icon Resources

### Free Icon Tools:
- **Figma** - Design custom icons
- **Inkscape** - Free vector graphics
- **GIMP** - Image editing

### Online Converters:
- https://convertio.co/png-ico/
- https://www.favicon-generator.org/
- https://www.icoconverter.com/

### Icon Libraries:
- https://icons8.com/
- https://www.flaticon.com/
- https://fontawesome.com/

---

**Need help?** Check `ADD_ICON_GUIDE.md` for detailed documentation!
