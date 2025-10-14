# 🎨 Hướng Dẫn Thêm Icon Cho Ứng Dụng

## 📋 Yêu Cầu

- File icon định dạng `.ico`
- Kích thước khuyến nghị: 256x256 pixels
- Có thể có nhiều sizes trong 1 file: 16x16, 32x32, 48x48, 256x256

---

## 🔧 Cách 1: Tạo Icon Online (Nhanh)

### **Sử dụng Online Converter**

1. **Tải ảnh logo/icon** (PNG, JPG, SVG)
2. **Convert sang .ico** tại:
   - https://www.favicon-generator.org/
   - https://convertio.co/png-ico/
   - https://www.icoconverter.com/

3. **Download file** → Đặt tên: `icon.ico`
4. **Copy vào folder** `GUI-Docker/`

---

## 🎨 Cách 2: Tạo Icon Bằng Python (Tự Động)

### **Script Tự Động Tạo Icon**

Tạo file `create_icon.py`:

```python
"""
Auto-generate icon for Spark Runner GUI
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    """Create a simple icon"""
    # Create base image (256x256)
    size = 256
    img = Image.new('RGBA', (size, size), color=(15, 23, 42, 255))  # Dark background
    draw = ImageDraw.Draw(img)
    
    # Draw gradient circle
    center = size // 2
    radius = size // 3
    
    # Outer circle (orange/yellow gradient)
    for i in range(radius, 0, -2):
        color_val = int(255 * (i / radius))
        color = (255, color_val, 0, 255)  # Orange to yellow
        draw.ellipse(
            [center - i, center - i, center + i, center + i],
            fill=color
        )
    
    # Draw "S" for Spark
    try:
        # Try to use a nice font
        font = ImageFont.truetype("arial.ttf", 120)
    except:
        # Fallback to default
        font = ImageFont.load_default()
    
    # Draw text
    text = "S"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2 - 10
    
    # Shadow
    draw.text((text_x + 3, text_y + 3), text, font=font, fill=(0, 0, 0, 128))
    # Main text
    draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255, 255))
    
    # Save as ICO with multiple sizes
    img.save('icon.ico', format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (256, 256)])
    print("✅ Icon created: icon.ico")
    
    # Also save as PNG for preview
    img.save('icon_preview.png')
    print("✅ Preview saved: icon_preview.png")

if __name__ == '__main__':
    create_icon()
```

**Chạy script:**
```powershell
pip install Pillow
python create_icon.py
```

---

## 📝 Cách 3: Sử dụng Logo Có Sẵn

### **Convert PNG/JPG sang ICO**

Nếu bạn có logo PNG:

```python
from PIL import Image

# Open PNG
img = Image.open('logo.png')

# Resize nếu cần
img = img.resize((256, 256), Image.Resampling.LANCZOS)

# Save as ICO
img.save('icon.ico', format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (256, 256)])
print("✅ Converted to icon.ico")
```

---

## 🔨 Cách Build Với Icon

### **Option 1: Sử dụng build.bat (Cập nhật)**

Cập nhật file `build.bat` thêm dòng:

```batch
--icon=icon.ico ^
```

### **Option 2: Sử dụng build_config.spec (Cập nhật)**

Cập nhật file `build_config.spec`:

```python
# Tìm dòng:
ICON_FILE = None

# Thay bằng:
ICON_FILE = 'icon.ico'  # Path to your icon file
```

### **Option 3: Command Line Trực Tiếp**

```powershell
pyinstaller ^
    --name=SparkRunnerGUI ^
    --onefile ^
    --windowed ^
    --icon=icon.ico ^
    --add-data=run_spark_gui;run_spark_gui ^
    --add-data=docker-compose.yml;. ^
    --noconfirm ^
    run_spark_gui\main.py
```

---

## ✅ Checklist

- [ ] Có file `icon.ico` trong folder `GUI-Docker/`
- [ ] Kích thước icon: 256x256 hoặc nhiều sizes
- [ ] Cập nhật build script với `--icon=icon.ico`
- [ ] Build lại: `.\build.bat`
- [ ] Verify: Check icon trong `dist\SparkRunnerGUI.exe`

---

## 🎯 Test Icon

Sau khi build:

1. **Check file .exe**:
   - Right-click `SparkRunnerGUI.exe`
   - Properties → See icon
   
2. **Check trong Explorer**:
   - Icon hiển thị trong file explorer
   
3. **Check trong taskbar**:
   - Run app → Icon hiển thị trong taskbar

---

## 🔍 Troubleshooting

### **Problem: Icon không hiển thị**

**Solution 1: Clear icon cache**
```powershell
# Windows
ie4uinit.exe -show
```

**Solution 2: Rebuild**
```powershell
Remove-Item dist, build -Recurse -Force
.\build.bat
```

**Solution 3: Check icon file**
```powershell
# Verify icon.ico exists
Test-Path icon.ico
# Should return True
```

### **Problem: Icon bị vỡ/lỗi**

**Solution:** Use proper ICO format với multiple sizes
```python
# Correct way
img.save('icon.ico', format='ICO', sizes=[(16,16), (32,32), (48,48), (256,256)])
```

---

## 📦 Icon Resources

### **Free Icon Sources:**
- https://icons8.com/ (Free icons)
- https://www.flaticon.com/ (Free with attribution)
- https://iconmonstr.com/ (Free, no attribution)
- https://fontawesome.com/ (Free icons)

### **Icon Themes for Spark:**
- ⚡ Lightning bolt (Spark symbol)
- 🔥 Flame (Spark fire)
- 📊 Data/Analytics
- 🐋 Docker whale
- ☁️ Cloud computing

---

## 💡 Quick Icon Ideas

### **Simple Text Icon:**
```
- Background: Dark blue/black
- Text: "SR" or "S" (Spark Runner)
- Font: Bold, modern
- Color: Orange/Yellow (Spark colors)
```

### **Symbol Icon:**
```
- Lightning bolt ⚡
- + Docker whale 🐋
- Orange/Yellow gradient
```

### **Professional Icon:**
```
- Minimalist design
- Flat colors
- Clear at small sizes
- Matches app theme
```

---

## 🎨 Recommended Icon Colors

```
Primary: #FF6B00 (Orange - Spark)
Secondary: #0969DA (Blue - Docker)
Background: #0F172A (Dark)
Accent: #FFD700 (Gold)
```

---

## 📄 Example: Create Simple Icon

```python
from PIL import Image, ImageDraw

# Create 256x256 icon
img = Image.new('RGB', (256, 256), '#0F172A')
draw = ImageDraw.Draw(img)

# Draw lightning bolt (simplified)
points = [
    (128, 40),   # Top
    (100, 120),  # Mid-left
    (128, 120),  # Mid-center
    (90, 200),   # Bottom-left
    (120, 140),  # Back up
    (128, 140),  # Center
    (160, 70)    # Top-right
]
draw.polygon(points, fill='#FFD700')

# Save
img.save('icon.ico', format='ICO', sizes=[(256,256)])
```

---

## ✨ Done!

After adding icon:
1. ✅ Create `icon.ico`
2. ✅ Update build script
3. ✅ Run `.\build.bat`
4. ✅ Check `dist\SparkRunnerGUI.exe` has icon
5. ✅ Ship it! 🚀
