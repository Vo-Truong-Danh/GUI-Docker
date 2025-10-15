# 📊 Container Image Viewer - Hướng dẫn sử dụng

## 🎯 Tổng quan

Container Image Viewer là công cụ hiện đại để xem và quản lý hình ảnh/biểu đồ từ Docker containers. Phiên bản v2 với giao diện được tối ưu hóa và nhiều tính năng mới.

---

## ✨ Tính năng mới (v2 - Modern UI)

### 🎨 Giao diện hiện đại
- **Layout 2 hàng**: Controls được tổ chức rõ ràng hơn
- **Emoji icons**: Dễ nhận biết các chức năng
- **Dark canvas**: Nền tối (#2b2b2b) giúp xem ảnh rõ hơn
- **Status bar chi tiết**: Hiển thị size, zoom, format ảnh

### 🔍 Zoom & Navigation
- **Zoom In/Out**: Buttons ➕/➖ hoặc `Ctrl + MouseWheel`
- **Zoom Reset**: Button 🔄 để về 100%
- **Zoom label**: Hiển thị % zoom realtime
- **Mouse wheel scrolling**: Cuộn ảnh mượt mà
- **Zoom range**: 10% → 500%

### 📂 File Browser nâng cao
- **Treeview**: Hiển thị filename + file size
- **Double-click**: Xem ảnh nhanh
- **File info**: Hiển thị kích thước file (KB, MB)
- **Multiple formats**: PNG, JPG, JPEG, GIF, BMP

### 🚀 Quick Path Buttons
- **💡 /tmp/**: Nhảy nhanh đến thư mục /tmp/
- **⚡ /output/**: Nhảy đến thư mục /output/
- **Recent paths dropdown**: Lưu 10 paths gần nhất

### 📊 Image Info Display
- **Original size**: Kích thước gốc (width × height)
- **File size**: Dung lượng file (KB)
- **Color mode**: RGB, RGBA, L, etc.
- **Current zoom**: Zoom level hiện tại

### 🗑️ Clear View
- **Clear button**: Xóa ảnh hiện tại
- **Placeholder**: Hiển thị hướng dẫn khi chưa có ảnh

---

## 🎮 Cách sử dụng

### 1️⃣ Mở Container Image Viewer

**Từ Main GUI:**
```
Menu → Tools → 📊 Container Image Viewer
```

**Hoặc chạy trực tiếp:**
```powershell
cd "d:\BaiTapSinhVien\TH BigData\GUI-Docker\run_spark_gui"
python test_image_viewer.py
```

### 2️⃣ Browse và xem ảnh

**Cách 1: Browse Files**
1. Chọn container (VD: `spark-worker`)
2. Nhập đường dẫn thư mục (VD: `/tmp/`)
3. Click **📂 Browse Files**
4. Double-click ảnh trong danh sách
5. ✅ Ảnh hiển thị tự động!

**Cách 2: Xem trực tiếp**
1. Chọn container
2. Nhập đường dẫn đầy đủ (VD: `/tmp/demo_chart.png`)
3. Click **👁️ View Image**

### 3️⃣ Zoom & Navigate

**Zoom In/Out:**
- Click buttons **➕** / **➖**
- Hoặc `Ctrl + Mouse Wheel`

**Reset Zoom:**
- Click button **🔄**

**Scroll ảnh:**
- Mouse wheel để scroll dọc
- Shift + Mouse wheel để scroll ngang
- Hoặc kéo scrollbar

### 4️⃣ Download ảnh

1. Xem ảnh trước (View)
2. Click **💾 Download**
3. Chọn vị trí lưu
4. ✅ Done!

### 5️⃣ Refresh

- Click **🔄 Refresh** để tải lại ảnh hiện tại
- Hữu ích khi file trong container thay đổi

### 6️⃣ Clear

- Click **🗑️ Clear** để xóa ảnh và reset view

---

## 🎯 Quick Paths

### Container mặc định: `spark-worker`

### Các đường dẫn thường dùng:

| Path | Mô tả | Quick Button |
|------|-------|--------------|
| `/tmp/` | Temporary files | 💡 /tmp/ |
| `/output/` | Output results | ⚡ /output/ |
| `/opt/spark/work/` | Spark work dir | - |
| `/app/` | Application dir | - |

### Recent Paths
- Tự động lưu 10 paths gần nhất
- Chọn từ dropdown "Path"
- Lưu trong file `recent_paths.json`

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + Mouse Wheel Up` | Zoom In |
| `Ctrl + Mouse Wheel Down` | Zoom Out |
| `Mouse Wheel` | Scroll Vertical |
| `Shift + Mouse Wheel` | Scroll Horizontal |
| `Double-click` (in file browser) | View image |

---

## 🎨 UI Elements

### Top Toolbar (Row 1)
```
🐳 Container: [dropdown] | 📁 Path: [combobox] | 💡 /tmp/ | ⚡ /output/
```

### Action Buttons (Row 2)
```
📂 Browse Files | 👁️ View Image | 💾 Download | 🔄 Refresh | 🗑️ Clear
```

### Zoom Controls (Right side)
```
🔍 Zoom: [➕] [100%] [➖] [🔄]
```

### Canvas Area
```
┌─────────────────────────────────────┐
│   Dark canvas (#2b2b2b)             │
│   with image display                │
│   + scrollbars                      │
└─────────────────────────────────────┘
```

### Status Bar (Bottom)
```
✅ Status message | Size: 800×600 | Zoom: 100% | 45.2 KB | RGB
```

---

## 📋 File Browser Window

```
┌──────────────────────────────────────────┐
│  📁 Images in spark-worker:/tmp/ (5 files)│
├──────────────────────────────────────────┤
│ 📄 Filename          │ 📏 Size           │
├──────────────────────┼───────────────────┤
│ demo_chart.png       │ 45.2K             │
│ result.png           │ 120K              │
│ output_graph.jpg     │ 89K               │
│ ...                  │ ...               │
├──────────────────────────────────────────┤
│  [👁️ View Selected]  [❌ Cancel]          │
└──────────────────────────────────────────┘
```

**Features:**
- Treeview với 2 cột: Filename + Size
- Scrollable list
- Double-click để xem nhanh
- Size tự động format (KB, MB)

---

## 🔧 Technical Details

### Supported Formats
- PNG (`.png`)
- JPEG (`.jpg`, `.jpeg`)
- GIF (`.gif`)
- BMP (`.bmp`)

### Image Processing
- **Library**: Pillow (PIL)
- **Resizing**: LANCZOS resampling (high quality)
- **Color modes**: RGB, RGBA, L, LA, CMYK, etc.

### Zoom Implementation
- Zoom level: 10% to 500%
- Multiplier: 1.2x per step
- Preserves aspect ratio
- Real-time update

### Docker Integration
```bash
# List files
docker exec <container> ls -lh <path>

# Copy image
docker cp <container>:<path> <local_temp>

# Display with PIL
Image.open(temp_file)
```

---

## 💡 Tips & Tricks

### 1. Xem ảnh nhanh nhất
```
1. Click "💡 /tmp/"
2. Click "📂 Browse Files"
3. Double-click ảnh
```

### 2. So sánh nhiều ảnh
- Mở nhiều cửa sổ viewer cùng lúc
- Xem ảnh ở container khác nhau

### 3. Zoom chi tiết
```
1. View ảnh
2. Ctrl + Scroll để zoom
3. Kéo ảnh để xem phần cần thiết
```

### 4. Download hàng loạt
```
1. Browse files
2. View từng ảnh
3. Download mỗi ảnh
```

### 5. Recent Paths
- Paths tự động lưu sau mỗi browse
- Chọn nhanh từ dropdown
- Xóa file `recent_paths.json` để reset

---

## 🐛 Troubleshooting

### ❌ "Failed to open image viewer: 'App' object has no attribute 'log'"
**Giải pháp:** Đã fix trong phiên bản mới - sử dụng `print()` thay vì `self.log()`

### ❌ "No image files found"
**Nguyên nhân:** Thư mục không có file ảnh
**Giải pháp:** 
- Kiểm tra path đúng chưa
- Thử path khác (VD: `/tmp/`, `/output/`)

### ❌ "Failed to copy image"
**Nguyên nhân:** Container không chạy hoặc file không tồn tại
**Giải pháp:**
```powershell
# Kiểm tra container đang chạy
docker ps

# Kiểm tra file tồn tại
docker exec spark-worker ls -lh /tmp/
```

### ❌ Module PIL not found
**Giải pháp:**
```powershell
pip install Pillow
```

### ⚠️ Zoom quá chậm
**Nguyên nhân:** Ảnh quá lớn (>10MB)
**Giải pháp:** 
- Zoom từ từ (1-2 lần)
- Reset zoom về 100% trước khi zoom tiếp

---

## 📝 Changelog

### v2.0 - Modern UI (Oct 2025)
- ✅ Giao diện 2 hàng hiện đại
- ✅ Zoom controls (In/Out/Reset)
- ✅ Ctrl+MouseWheel zoom
- ✅ File browser với size info
- ✅ Quick path buttons
- ✅ Recent paths history (10 items)
- ✅ Clear view button
- ✅ Dark canvas background
- ✅ Enhanced status bar
- ✅ Double-click to view
- ✅ Emoji icons everywhere
- ✅ Better error messages

### v1.0 - Initial Release
- ✅ Basic browse/view/download
- ✅ Container selection
- ✅ Path input
- ✅ Canvas display

---

## 🎓 Examples

### Example 1: Xem demo chart
```python
# Container đã có sẵn: /tmp/demo_chart.png
1. Container: spark-worker
2. Path: /tmp/demo_chart.png
3. Click "👁️ View Image"
```

### Example 2: Browse tất cả ảnh trong /tmp/
```python
1. Container: spark-worker
2. Path: /tmp/
3. Click "📂 Browse Files"
4. Double-click ảnh bất kỳ
```

### Example 3: Download ảnh về máy
```python
1. View ảnh (Example 1 hoặc 2)
2. Click "💾 Download"
3. Chọn folder và tên file
4. Save
```

### Example 4: Zoom chi tiết biểu đồ
```python
1. View ảnh
2. Ctrl + Scroll up (zoom to 200%)
3. Kéo để xem chi tiết
4. Ctrl + Scroll down (zoom to 100%)
5. Click 🔄 để reset về 100%
```

---

## 🚀 Advanced Usage

### Custom Recent Paths
Edit `recent_paths.json`:
```json
[
  "/tmp/",
  "/output/charts/",
  "/opt/spark/work/",
  "/app/results/"
]
```

### Multiple Viewers
```python
# Open multiple viewers
python test_image_viewer.py  # Window 1
python test_image_viewer.py  # Window 2
```

### Programmatic Usage
```python
from container_image_viewer import ContainerImageViewer

# Create viewer
viewer = ContainerImageViewer(parent=None)

# Set container and path
viewer.container_var.set("spark-worker")
viewer.path_var.set("/tmp/chart.png")

# Auto-view on startup
viewer.view_image()

# Show window
viewer.show()
```

---

## 📞 Support

**Issues:** Check `main.py` logs for errors

**Documentation:**
- `NEW_FEATURES_v6.2.md` - Chi tiết tính năng
- `FEATURE_SUMMARY_v6.2.md` - Tóm tắt

**Repository:** GUI-Docker by Vo-Truong-Danh

---

## 🎉 Enjoy!

Container Image Viewer v2 - Modern, Fast, Easy to Use! 🚀
