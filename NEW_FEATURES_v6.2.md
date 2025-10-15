# 🆕 Tính Năng Mới - GUI v6.2

## 📊 1. Container Image Viewer

### Mô tả
Xem và tải ảnh/biểu đồ kết quả từ Docker container ngay trong GUI!

### Cách sử dụng

#### 🚀 Mở Image Viewer:
```
Menu → Tools → 📊 Container Image Viewer
```

#### 👁️ Xem ảnh trong container:

**Cách 1: Browse tự động**
```
1. Chọn container: spark-worker
2. Nhập path: /tmp/
3. Click "📂 Browse" 
   → Sẽ liệt kê tất cả file ảnh (.png, .jpg, .jpeg, .gif)
4. Chọn ảnh muốn xem
5. Click "View Selected"
```

**Cách 2: Nhập path trực tiếp**
```
1. Container: spark-worker
2. Image Path: /tmp/sentiment_vs_growth_chart.png
3. Click "👁️ View"
```

#### 💾 Download ảnh về máy:
```
1. Sau khi xem ảnh
2. Click "💾 Download"
3. Chọn nơi lưu
4. Done!
```

### 🎯 Use Cases

#### Case 1: Xem biểu đồ Spark output
```python
# Trong Spark job (ví dụ: 4.4.py)
import matplotlib.pyplot as plt

# Vẽ biểu đồ
plt.figure(figsize=(10, 6))
plt.plot(data)
plt.title('Sentiment Analysis')

# LƯU vào container
plt.savefig('/tmp/my_chart.png')
print("Biểu đồ đã được lưu tại container 'spark-worker' trong đường dẫn: /tmp/my_chart.png")
```

```
Sau khi chạy job:
1. Menu → Tools → Container Image Viewer
2. Container: spark-worker
3. Path: /tmp/my_chart.png
4. Click "View" → Xem ngay!
```

#### Case 2: Browse tất cả ảnh output
```
1. Spark job tạo nhiều biểu đồ trong /tmp/
2. Image Viewer → Browse → /tmp/
3. Sẽ show list tất cả .png
4. Click chọn → View
```

#### Case 3: Download ảnh để đưa vào báo cáo
```
1. View ảnh trong container
2. Click "Download"
3. Lưu vào: D:\Reports\images\chart1.png
4. Dùng cho PowerPoint/Word
```

### 📂 Các path thường dùng

| Container | Path | Mô tả |
|-----------|------|-------|
| `spark-worker` | `/tmp/` | Output mặc định của Spark jobs |
| `spark-worker` | `/opt/workspace/` | Workspace folder |
| `namenode` | `/tmp/` | HDFS temp files |
| `datanode` | `/hadoop/dfs/data/` | Data storage |

### ⚠️ Lưu ý

- **Ảnh phải có trong container**: Nếu job chưa chạy hoặc path sai → không thấy ảnh
- **Format hỗ trợ**: PNG, JPG, JPEG, GIF, BMP
- **Size giới hạn**: Ảnh quá lớn (>50MB) có thể load chậm
- **Path phân biệt hoa/thường**: Linux path case-sensitive!

---

## ⏰ 2. Phản Hồi Realtime (5-10s)

### Mô tả
Khi cài thư viện Python (pip install), GUI sẽ cập nhật progress **mỗi 5-10 giây** để bạn biết đang chạy gì!

### Cải tiến

#### Trước (v6.1):
```
🚀 Đang cài đặt: pandas
... (im lặng 2-3 phút) ...
Building wheel for pandas: still running...
... (im lặng tiếp 2-3 phút) ...
✅ Cài đặt thành công
```

#### Sau (v6.2):
```
🚀 Đang cài đặt: pandas
📥 Đang tải thông tin...
⬇️ Downloading pandas... 50%
🔧 Cài dependencies...
📝 Chuẩn bị metadata...
⚙️ ĐANG BUILD: Quá trình này có thể mất 5-15 phút, vui lòng đợi...
⏰ Vẫn đang chạy... (10s đã trôi qua)      ← MỚI!
⏰ Vẫn đang chạy... (20s đã trôi qua)      ← MỚI!
⏰ Vẫn đang chạy... (30s đã trôi qua)      ← MỚI!
⏰ Vẫn đang build... (1 phút đã trôi qua)  ← MỚI!
⏰ Vẫn đang build... (2 phút đã trôi qua)  ← MỚI!
⚠️ Đã chạy 5 phút - Đây là bình thường...  ← MỚI!
⏰ Đã chạy 10 phút - Gần xong rồi...       ← MỚI!
✅ Hoàn thành trong 12 phút 34 giây
```

### Cập nhật theo thời gian

| Thời gian | Thông báo |
|-----------|-----------|
| **Mỗi 5s** | Cập nhật status bar với thời gian realtime |
| **Mỗi 10s** | Log message: "⏰ Vẫn đang chạy... (Xs)" |
| **5 phút** | Cảnh báo: Bình thường, cần 10-15 phút |
| **10 phút** | Cảnh báo: Gần xong, còn 2-5 phút |

### Status Bar Realtime

```
Trước:  ⏳ Đang cài đặt pandas...
Sau:    ⏳ ⚙️ Build pandas... (2m 34s - 127 dòng)
                              ↑ Thời gian realtime!
```

### Code trong python_packages_tab.py

```python
# Update mỗi 5 giây
if current_time - last_update >= 5:
    elapsed = int(current_time - start_time)
    mins, secs = divmod(elapsed, 60)
    time_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"
    
    # Hiển thị realtime
    self.update_status(f"⏳ {current_stage} {package}... ({time_str} - {line_count} dòng)")
    
    # Log mỗi 10 giây
    if elapsed % 10 == 0:
        self.log_output(f"⏰ Vẫn đang chạy... ({time_str} đã trôi qua)\n")
```

---

## 🎯 Demo Scenarios

### Scenario 1: Cài pandas và xem biểu đồ

```
1. Tab "Python Packages"
   → Package: pandas
   → Click "Cài đặt"
   
2. Theo dõi log:
   ⏰ Vẫn đang chạy... (10s)
   ⏰ Vẫn đang chạy... (20s)
   ⏰ Vẫn đang chạy... (30s)
   ...
   ✅ Hoàn thành trong 4m 23s
   
3. Tab "Spark Runner"
   → Chạy job vẽ biểu đồ (4.4.py)
   → Output: "Biểu đồ lưu tại /tmp/chart.png"
   
4. Menu → Tools → Container Image Viewer
   → Container: spark-worker
   → Path: /tmp/chart.png
   → Click "View"
   → Xem biểu đồ ngay!
   
5. Click "Download"
   → Lưu vào: D:\Reports\chart.png
```

### Scenario 2: Browse tất cả biểu đồ output

```
1. Spark job tạo nhiều biểu đồ:
   /tmp/chart1.png
   /tmp/chart2.png
   /tmp/chart3.png
   
2. Image Viewer → Browse → /tmp/
   → List hiện:
     chart1.png
     chart2.png
     chart3.png
     
3. Click chọn chart1.png → View
4. Click "Download" → Lưu
5. Repeat cho chart2, chart3
```

### Scenario 3: Cài thư viện lớn với progress tracking

```
1. Cài matplotlib (lâu nhất):
   → Status: ⏳ ⚙️ Build matplotlib... (0m 5s - 23 dòng)
   → Log: ⏰ Vẫn đang chạy... (10s)
   → Status: ⏳ ⚙️ Build matplotlib... (0m 15s - 67 dòng)
   → Log: ⏰ Vẫn đang chạy... (20s)
   ...
   → Status: ⏳ ⚙️ Build matplotlib... (4m 52s - 892 dòng)
   → Log: ⚠️ Đã chạy 5 phút - Bình thường...
   → ✅ Hoàn thành trong 5m 43s
```

---

## 🛠️ Technical Details

### Container Image Viewer

**Files:**
- `container_image_viewer.py` - Main viewer class
- Dependencies: `PIL` (Pillow), `tkinter`

**Architecture:**
```
ContainerImageViewer
├── UI Components
│   ├── Control Frame (container, path, buttons)
│   ├── Canvas (image display with scrollbars)
│   └── Status Bar
├── Methods
│   ├── browse_container() - List images
│   ├── view_image() - Display image
│   └── download_image() - Save to local
└── Docker Integration
    └── docker cp container:/path/to/image.png local_temp
        → Load with PIL
        → Display in Canvas
```

**Key Features:**
- Auto-resize lớn images to fit canvas
- Scrollable for huge images
- Cross-platform (Windows/Linux/Mac)
- Hidden console windows on Windows

### Progress Monitor

**Files:**
- `python_packages_tab.py` - Line 557-591 (enhanced)

**Key Improvements:**
```python
# Mỗi 5 giây
if current_time - last_update >= 5:
    # Update status bar realtime
    self.update_status(f"⏳ {stage} {pkg}... ({time_str})")
    
    # Log mỗi 10 giây
    if elapsed % 10 == 0:
        self.log_output(f"⏰ Vẫn đang chạy... ({time_str})\n")
    
    # Cảnh báo milestone
    if elapsed == 300:  # 5 phút
        self.log_output("⚠️ Đã 5 phút - Bình thường...\n")
    if elapsed == 600:  # 10 phút
        self.log_output("⏰ Đã 10 phút - Gần xong...\n")
```

---

## ✅ Testing

### Test Image Viewer

```powershell
# 1. Tạo ảnh test trong container
docker exec spark-worker bash -c "echo 'iVBORw0KGg...' | base64 -d > /tmp/test.png"

# 2. Mở GUI → Tools → Image Viewer
# 3. Container: spark-worker
# 4. Path: /tmp/test.png
# 5. Click View → Should show image!
```

### Test Progress Monitor

```powershell
# 1. Mở GUI → Tab "Python Packages"
# 2. Package: pandas
# 3. Click "Cài đặt"
# 4. Quan sát log:
#    - Mỗi 10s có "⏰ Vẫn đang chạy..."
#    - Status bar cập nhật realtime
#    - Progress bar tăng dần
```

---

## 📝 Version History

### v6.2 (2025-10-16)
- ✅ Added Container Image Viewer
- ✅ Enhanced pip install progress (5-10s updates)
- ✅ Realtime status bar with elapsed time
- ✅ Milestone warnings (5min, 10min)

### v6.1 (2025-10-15)
- Large file upload optimization
- Chunked upload for >100MB files
- Progress tracking for uploads

### v6.0 (2025-10-14)
- Hidden console windows (Windows)
- Enhanced error handling
- Auto-recovery system

---

## 🎉 Summary

**2 Tính năng mới:**

1. **📊 Container Image Viewer**: Xem ảnh/biểu đồ trong container ngay trong GUI
   - Browse, View, Download
   - Support: PNG, JPG, JPEG, GIF, BMP
   - Access: Menu → Tools → Container Image Viewer

2. **⏰ Progress Monitor**: Cập nhật realtime mỗi 5-10s khi cài thư viện
   - Status bar: Thời gian realtime + số dòng log
   - Log: Message mỗi 10s "⏰ Vẫn đang chạy..."
   - Cảnh báo milestone: 5 phút, 10 phút

**Use case chính:**
```
Spark job → Tạo biểu đồ → Lưu /tmp/chart.png
→ Image Viewer → Xem ngay → Download về
```

**Kết quả:** Không cần dùng `docker cp` thủ công nữa! 🎉
