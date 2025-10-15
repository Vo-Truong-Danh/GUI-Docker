# 🔧 Fix Log - Large File Upload

## ❌ Lỗi gặp phải:

```
[Errno 2] No such file or directory: '/tmp/upload_20251015_231149_chunk_0000'
```

## 🔍 Nguyên nhân:

Script đang tạo temp path sai:
```python
# SAI ❌
chunk_path_local = f"{temp_dir}_{chunk_filename}"
# Kết quả: "/tmp/upload_20251015_231149_chunk_0000"
# → Path này KHÔNG tồn tại trên Windows!
```

**Vấn đề:**
- `temp_dir` là path trong **container** (`/tmp/upload_xxx`)
- Script cố tạo file tại path này trên **máy host Windows**
- Windows không có `/tmp/` directory!

## ✅ Giải pháp:

### 1. Tạo temp directory riêng cho local và container

```python
# Create temp directory in container
temp_dir_container = f"/tmp/upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Create temp directory on local machine (Windows/Linux compatible)
import tempfile
temp_dir_local = tempfile.mkdtemp(prefix='hdfs_upload_')
```

### 2. Sử dụng đúng temp path

```python
# Local chunk path (Windows: C:\Users\xxx\AppData\Local\Temp\hdfs_upload_xxx\chunk_0000)
chunk_path_local = os.path.join(temp_dir_local, chunk_filename)

# Container chunk path (Linux: /tmp/upload_20251015_231149/chunk_0000)
chunk_path_container = f"{temp_dir_container}/{chunk_filename}"
```

### 3. Cleanup cả 2 temp directories

```python
try:
    # ... upload logic ...
finally:
    # Clean up local temp directory
    import shutil
    if os.path.exists(temp_dir_local):
        shutil.rmtree(temp_dir_local)
```

## 📝 Code Changes:

**File**: `large_file_upload.py`

### Change 1: Create proper temp directories (line ~80)

```python
# OLD ❌
temp_dir = f"/tmp/upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
subprocess.run(['docker', 'exec', container, 'mkdir', '-p', temp_dir], ...)

# NEW ✅
temp_dir_container = f"/tmp/upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
subprocess.run(['docker', 'exec', container, 'mkdir', '-p', temp_dir_container], ...)

import tempfile
temp_dir_local = tempfile.mkdtemp(prefix='hdfs_upload_')
```

### Change 2: Use correct paths (line ~105)

```python
# OLD ❌
chunk_path_local = f"{temp_dir}_{chunk_filename}"  # Wrong!

# NEW ✅
chunk_path_local = os.path.join(temp_dir_local, chunk_filename)
chunk_path_container = f"{temp_dir_container}/{chunk_filename}"
```

### Change 3: Update all references (line ~140+)

```python
# OLD ❌
merged_file = f"{temp_dir}/{filename}"
merge_cmd = f"cat {temp_dir}/chunk_* > {merged_file}"

# NEW ✅
merged_file = f"{temp_dir_container}/{filename}"
merge_cmd = f"cat {temp_dir_container}/chunk_* > {merged_file}"
```

### Change 4: Cleanup both temp directories (line ~173+)

```python
# Container cleanup
subprocess.run(['docker', 'exec', container, 'rm', '-rf', temp_dir_container], ...)

# NEW: Local cleanup
finally:
    import shutil
    if os.path.exists(temp_dir_local):
        shutil.rmtree(temp_dir_local)
```

## 🧪 Test lại:

```powershell
# Test với file lớn
cd run_spark_gui
python main.py

# Tab "HDFS Upload"
# Browse → chọn file 2.7 GB
# Container: namenode
# HDFS Path: /input
# Click "Upload"
```

**Kết quả mong đợi:**

```
📊 File size: 2708.54 MB
📦 Using chunked upload
🔪 Chunk size: 50.00 MB
🧩 Total chunks: 55

📁 Created local temp directory: C:\Users\xxx\AppData\Local\Temp\hdfs_upload_abc123
📁 Creating temp directory in container: /tmp/upload_20251015_231500

📦 Chunk 1/55: 50.00 MB
   ✓ Progress: 1.8%
📦 Chunk 2/55: 50.00 MB
   ✓ Progress: 3.7%
...
📦 Chunk 55/55: 8.54 MB
   ✓ Progress: 100.0%

🔗 Merging chunks...
  ✓ Merged into: /tmp/upload_20251015_231500/file.csv

📤 Uploading to HDFS...
  ✓ Uploaded to HDFS: /input/file.csv

🧹 Cleaning up temporary files...
  ✓ Cleanup complete
  🧹 Cleaned up local temp: C:\Users\xxx\AppData\Local\Temp\hdfs_upload_abc123

🔍 Verifying upload...
  ✅ Verification successful!

✅ Successfully uploaded file.csv to /input/
⏱️ Total time: 4m 32s
```

## 🎯 Summary:

| Item | Before | After |
|------|--------|-------|
| **Local temp** | ❌ `/tmp/upload_xxx_chunk_0000` (không tồn tại trên Windows) | ✅ `C:\Users\xxx\AppData\Local\Temp\hdfs_upload_xxx\chunk_0000` |
| **Container temp** | ✅ `/tmp/upload_xxx/` | ✅ `/tmp/upload_xxx/` |
| **Cleanup** | ❌ Chỉ cleanup container | ✅ Cleanup cả local và container |
| **Cross-platform** | ❌ Chỉ chạy trên Linux | ✅ Chạy cả Windows/Linux/Mac |

## ✅ Status:

**Fixed** - Ready for testing với file 2.7 GB!

---

**Date**: 2025-10-15 23:15  
**Issue**: Path error on Windows  
**Fix**: Separate local and container temp directories
