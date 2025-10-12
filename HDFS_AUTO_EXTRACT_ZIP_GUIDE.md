# 📦 HDFS Upload - Auto-Extract ZIP Files

## 🎯 Tổng Quan

Tính năng **tự động giải nén file ZIP** khi upload lên HDFS. Khi bạn upload file `.zip`, hệ thống sẽ:
1. Upload file ZIP gốc lên HDFS
2. Tự động giải nén file ZIP
3. Upload tất cả files đã giải nén vào thư mục riêng trên HDFS
4. Cleanup các file tạm

---

## ✨ Tính Năng Mới

### **Auto-Extract ZIP**
- ✅ Tự động detect file `.zip`
- ✅ Giải nén trên Docker container (không tốn tài nguyên máy local)
- ✅ Upload cả file ZIP gốc + files đã giải nén
- ✅ Tạo thư mục riêng cho extracted files
- ✅ Real-time logging cho từng bước
- ✅ Error handling robust

### **Checkbox Control**
- ✅ Checkbox "Auto-extract compressed files" để bật/tắt
- ✅ Mặc định: **BẬT** (value=True)
- ✅ Có thể tắt nếu chỉ muốn upload file ZIP không giải nén

---

## 🎬 Workflow

### **Khi Upload File ZIP**

```
1. Select file.zip
   ├─> file.zip (10 MB)
   └─> Checkbox: ☑ Auto-extract compressed files

2. Click "Upload"
   └─> Start upload process

3. Step 1/4: Copy to container
   └─> docker cp file.zip namenode:/tmp/

4. Step 2/4: Upload to HDFS
   └─> hdfs dfs -put /tmp/file.zip /data/file.zip

5. Step 2.5/4: Extract ZIP (NEW!)
   ├─> unzip -o file.zip -d /tmp/extracted_1/
   ├─> hdfs dfs -mkdir -p /data/file/
   ├─> hdfs dfs -put /tmp/extracted_1/* /data/file/
   └─> rm -rf /tmp/extracted_1/

6. Step 3/4: Verify
   └─> hdfs dfs -test -e /data/file.zip

7. Step 4/4: Cleanup
   └─> rm /tmp/file.zip
```

---

## 📁 Cấu Trúc HDFS

### **Trước Khi Extract (Chỉ upload ZIP)**
```
/data/
  └── file.zip          (10 MB - File nén gốc)
```

### **Sau Khi Extract (Auto-extract enabled)**
```
/data/
  ├── file.zip          (10 MB - File nén gốc)
  └── file/             (Thư mục extracted)
      ├── data1.csv     (3 MB)
      ├── data2.txt     (2 MB)
      ├── config.json   (500 KB)
      └── subfolder/
          └── more.csv  (4 MB)
```

**Lợi ích:**
- ✅ Có cả file ZIP gốc (để backup/download)
- ✅ Có files đã giải nén (sẵn sàng xử lý với Spark)
- ✅ Tổ chức rõ ràng, dễ quản lý

---

## 🎯 Các Trường Hợp Sử Dụng

### **Case 1: Upload + Extract (Khuyến nghị)**
```
☑ Auto-extract compressed files (Enabled)

Upload: dataset.zip (100 MB)
Result:
  /data/dataset.zip           (File gốc)
  /data/dataset/              (Extracted folder)
    ├── train.csv
    ├── test.csv
    └── validate.csv

→ Spark có thể đọc trực tiếp từ /data/dataset/*.csv
```

### **Case 2: Chỉ Upload ZIP (Không Extract)**
```
☐ Auto-extract compressed files (Disabled)

Upload: archive.zip (50 MB)
Result:
  /data/archive.zip           (Chỉ file gốc)

→ Cần extract thủ công sau nếu muốn
```

### **Case 3: Upload nhiều ZIP files**
```
☑ Auto-extract compressed files (Enabled)

Upload:
  - data1.zip
  - data2.zip
  - data3.zip

Result:
  /data/data1.zip
  /data/data1/
    └── (extracted files)
  /data/data2.zip
  /data/data2/
    └── (extracted files)
  /data/data3.zip
  /data/data3/
    └── (extracted files)
```

---

## 💻 Chi Tiết Kỹ Thuật

### **Extract Logic**

```python
# Check if auto-extract enabled and file is ZIP
if self.auto_extract_var.get() and filename.lower().endswith('.zip'):
    # 1. Unzip on container
    unzip_cmd = ['docker', 'exec', container, 'unzip', '-o', 
                 f'/tmp/{filename}', '-d', f'/tmp/extracted_{i}']
    
    # 2. Create extract directory in HDFS
    extract_dir = target_path.rsplit('.zip', 1)[0]
    mkdir_extract_cmd = ['docker', 'exec', container, 'hdfs', 'dfs', 
                         '-mkdir', '-p', extract_dir]
    
    # 3. Upload extracted files to HDFS
    put_extracted_cmd = ['docker', 'exec', container, 'hdfs', 'dfs', 
                         '-put', '-f', f'/tmp/extracted_{i}/*', extract_dir]
    
    # 4. Cleanup temp extracted files
    subprocess.run(['docker', 'exec', container, 'rm', '-rf', 
                   f'/tmp/extracted_{i}'], capture_output=True)
```

### **Error Handling**

```python
try:
    # Extract process
    ...
except Exception as e:
    self.log(f"⚠️ Extraction error: {str(e)}", 'warning')
    self.log(f"ℹ️  ZIP file uploaded but not extracted", 'info')
    # Upload vẫn thành công, chỉ extract thất bại
```

**Ưu điểm:**
- Extract thất bại → ZIP file vẫn được upload
- Không block toàn bộ upload process
- User nhận được thông báo chi tiết

---

## 📊 Log Output Example

### **Successful Extract**
```
[1/1] 📤 Uploading: dataset.zip
      Size: 10240.5 KB
      Step 1/4: Copy to container
      💻 $ docker cp "dataset.zip" namenode:/tmp/
      ✓ Copied to container /tmp/
      Step 2/4: Upload to HDFS
      💻 $ hdfs dfs -put -f /tmp/dataset.zip /data/dataset.zip
      ✓ Uploaded to HDFS
      📍 Location: /data/dataset.zip
      Step 2.5/4: Extracting ZIP file...
      💻 $ unzip -o dataset.zip -d /tmp/extracted_1
      ✓ Extracted successfully
      💻 $ hdfs dfs -put /tmp/extracted_1/* /data/dataset/
      ✓ Extracted files uploaded to HDFS
      📂 Extract Location: /data/dataset/
      Step 3/4: File verified in HDFS ✓
      Step 4/4: Cleanup temp file
      ✓ Cleaned up /tmp/dataset.zip

📊 Upload Summary
   ✅ Success: 1
   ❌ Failed: 0
   📁 Total: 1
```

### **Extract Failed (ZIP still uploaded)**
```
[1/1] 📤 Uploading: corrupted.zip
      ...
      ✓ Uploaded to HDFS
      📍 Location: /data/corrupted.zip
      Step 2.5/4: Extracting ZIP file...
      ⚠️ Extraction failed: End-of-central-directory signature not found
      ℹ️  ZIP file uploaded but not extracted
      Step 3/4: File verified in HDFS ✓
      ...

📊 Upload Summary
   ✅ Success: 1    (ZIP uploaded successfully)
   ❌ Failed: 0
```

---

## 🔧 Configuration

### **Enable/Disable Auto-Extract**

**UI:**
```
HDFS Upload Tab
  └─> Options Section
      └─> ☑ Auto-extract compressed files
```

**Config File (`spark_runner_config.json`):**
```json
{
  "auto_extract": true
}
```

**Programmatically:**
```python
self.auto_extract_var.set(True)   # Enable
self.auto_extract_var.set(False)  # Disable
```

---

## 🛠️ Requirements

### **Docker Image Requirements**
Container phải có `unzip` utility:

```dockerfile
# Trong Dockerfile của namenode
RUN apt-get update && apt-get install -y unzip
```

**Check nếu có unzip:**
```bash
docker exec namenode which unzip
# Output: /usr/bin/unzip
```

**Cài đặt nếu chưa có:**
```bash
docker exec namenode apt-get update
docker exec namenode apt-get install -y unzip
```

---

## ⚡ Performance

### **Small ZIP (< 50 MB)**
```
Upload time:     2-5 seconds
Extract time:    1-3 seconds
Total:           3-8 seconds
```

### **Medium ZIP (50-200 MB)**
```
Upload time:     5-15 seconds
Extract time:    3-10 seconds
Total:           8-25 seconds
```

### **Large ZIP (> 200 MB)**
```
Upload time:     15-60 seconds
Extract time:    10-30 seconds
Total:           25-90 seconds
```

**Tips:**
- Extract trên container (không ảnh hưởng máy local)
- Timeout: 120 seconds cho extract command
- Cleanup tự động các file tạm

---

## 🐛 Troubleshooting

### **Problem 1: Extraction Failed - "unzip: command not found"**
**Nguyên nhân:** Container không có unzip utility

**Giải pháp:**
```bash
docker exec namenode apt-get update
docker exec namenode apt-get install -y unzip
```

### **Problem 2: Extraction Failed - "End-of-central-directory signature not found"**
**Nguyên nhân:** File ZIP bị corrupt

**Giải pháp:**
- Kiểm tra file ZIP trên local
- Re-download hoặc re-create file ZIP
- ZIP file vẫn được upload, chỉ extract thất bại

### **Problem 3: Extraction Timeout**
**Nguyên nhân:** ZIP file quá lớn (> 500 MB)

**Giải pháp:**
- Tăng timeout trong code (hiện tại: 120s)
- Hoặc split ZIP thành nhiều files nhỏ hơn
- Hoặc tắt auto-extract, extract thủ công sau

### **Problem 4: Out of Space on Container**
**Nguyên nhân:** `/tmp` trên container không đủ dung lượng

**Giải pháp:**
```bash
# Check space
docker exec namenode df -h /tmp

# Cleanup old files
docker exec namenode rm -rf /tmp/extracted_*
```

---

## 📈 Roadmap

### **Future Enhancements**
- [ ] Hỗ trợ `.tar.gz`, `.tar` files
- [ ] Progress bar cho extract process
- [ ] Parallel extraction cho multiple files
- [ ] Custom extract location
- [ ] Selective extraction (chọn files cần extract)

---

## 📝 Changelog

### **Version 4.3.1** (Current - 2025-10-13)
- ✅ Added auto-extract for ZIP files
- ✅ Extract on Docker container (không ảnh hưởng local)
- ✅ Upload cả ZIP gốc + extracted files
- ✅ Real-time logging cho extract process
- ✅ Robust error handling
- ✅ Auto cleanup temp files

---

## 🎯 Quick Start

### **Test Auto-Extract**

1. **Prepare test ZIP:**
   ```bash
   # Create test files
   echo "data1" > file1.txt
   echo "data2" > file2.txt
   
   # Create ZIP
   zip test.zip file1.txt file2.txt
   ```

2. **Upload with GUI:**
   - Mở tab **HDFS Upload**
   - Chọn `test.zip`
   - Ensure ☑ **Auto-extract compressed files** is checked
   - Click **Upload**

3. **Verify on HDFS:**
   ```bash
   # Check ZIP file
   docker exec namenode hdfs dfs -ls /data/test.zip
   
   # Check extracted folder
   docker exec namenode hdfs dfs -ls /data/test/
   # Should show: file1.txt, file2.txt
   
   # Read extracted file
   docker exec namenode hdfs dfs -cat /data/test/file1.txt
   # Output: data1
   ```

4. **Expected Result:**
   ```
   ✅ test.zip uploaded
   ✅ Files extracted to /data/test/
   ✅ Both ZIP and extracted files available
   ```

---

## 📞 Support

**Nếu gặp vấn đề:**
1. Check Docker container có `unzip` command
2. Check log output trong HDFS Upload tab
3. Verify disk space: `docker exec namenode df -h`
4. Test với ZIP file nhỏ trước (< 10 MB)

**Version:** 4.3.1  
**Feature:** Auto-Extract ZIP Files  
**Date:** 2025-10-13
