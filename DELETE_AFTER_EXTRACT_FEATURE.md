# Tùy chọn xóa file nén sau khi giải nén

## ✅ Đã hoàn tất

Đã thêm tùy chọn **"Delete ZIP file after extraction"** vào HDFS Upload Tab.

## 🎯 Tính năng mới

### Checkbox mới: "Delete ZIP file after extraction"

**Vị trí:** Configuration Card → Options section (dưới "Auto-extract compressed files")

**Chức năng:**
- ✅ Tự động xóa file nén (.zip, .tar.gz, .tar, .gz) từ HDFS sau khi giải nén thành công
- ✅ Chỉ xóa khi extraction thành công
- ✅ Giữ nguyên file nếu extraction thất bại
- ✅ Lưu trạng thái vào config file
- ✅ Khôi phục trạng thái khi khởi động lại

## 📝 File đã sửa

### `hdfs_upload_tab_v4_clean.py` ✅

#### 1. Thêm UI Checkbox (dòng ~388-410)
```python
# Delete after extraction option
self.delete_after_extract_var = tk.BooleanVar(value=self.config.get('delete_after_extract', False))
delete_check = tk.Checkbutton(
    config_content,
    text='Delete ZIP file after extraction',
    variable=self.delete_after_extract_var,
    bg='#FFFFFF',
    fg='#24292F',
    font=('Segoe UI', 9),
    activebackground='#FFFFFF',
    selectcolor='#FFFFFF'
)
delete_check.pack(anchor='w', pady=(0, 8))
```

#### 2. Lưu config (dòng ~779)
```python
def save_config(self):
    """Save HDFS configuration to JSON file"""
    self.config['hdfs_container'] = self.container_var.get()
    self.config['hdfs_path'] = self.path_var.get()
    self.config['hdfs_port'] = self.hdfs_port_var.get()
    self.config['auto_extract'] = self.auto_extract_var.get()
    self.config['delete_after_extract'] = self.delete_after_extract_var.get()  # ← MỚI
```

#### 3. Logic xóa file cho ZIP (Java extraction) (dòng ~996-1010)
```python
if success:
    self.log(f"      ✅ Extracted and uploaded {uploaded} file(s) to HDFS", 'success')
    self.log(f"      📁 Location: {hdfs_target}/", 'success')
    
    # Delete ZIP file from HDFS if option is enabled
    if self.delete_after_extract_var.get():
        self.log(f"      🗑️ Deleting ZIP file from HDFS...", 'info')
        delete_cmd = ['docker', 'exec', container, 'hdfs', 'dfs', '-rm', f'{hdfs_target}/{filename}']
        delete_result = run_hidden(delete_cmd, capture_output=True, text=True, timeout=30)
        
        if delete_result.returncode == 0:
            self.log(f"      ✅ Deleted ZIP file from HDFS: {filename}", 'success')
        else:
            self.log(f"      ⚠️ Failed to delete ZIP file: {delete_result.stderr}", 'warning')
    
    return True
```

#### 4. Logic xóa file cho TAR/GZ (dòng ~1138-1152)
```python
if upload_success > 0:
    self.log(f"      ✓ Uploaded {upload_success}/{len(extracted_files)} files to HDFS", 'success')
    self.log(f"      📂 Extract Location: {extract_hdfs_dir}/", 'success')
    
    # Delete compressed file from HDFS if option is enabled
    if self.delete_after_extract_var.get():
        self.log(f"      🗑️ Deleting compressed file from HDFS...", 'info')
        compressed_hdfs_path = f'{hdfs_path.rstrip("/")}/{filename}'
        delete_cmd = ['docker', 'exec', container, 'hdfs', 'dfs', '-rm', compressed_hdfs_path]
        delete_result = run_hidden(delete_cmd, capture_output=True, text=True, timeout=30)
        
        if delete_result.returncode == 0:
            self.log(f"      ✅ Deleted compressed file from HDFS: {filename}", 'success')
        else:
            self.log(f"      ⚠️ Failed to delete compressed file: {delete_result.stderr}", 'warning')
```

## 🔄 Flow hoạt động

### Trường hợp 1: ZIP file (Java extraction)

1. **Upload** → File được upload lên HDFS: `/input/data.zip`
2. **Extract** → Java unzip extract nội dung
3. **Upload extracted** → Files được upload vào `/input/` 
4. **Check option** → Nếu "Delete ZIP file after extraction" = ✅
5. **Delete ZIP** → Xóa `/input/data.zip` từ HDFS
6. **Result** → Chỉ còn file đã extract trong `/input/`

### Trường hợp 2: TAR/GZ files

1. **Upload** → File được upload lên HDFS: `/input/data.tar.gz`
2. **Extract** → Untar/gunzip extract nội dung vào thư mục tạm
3. **Upload extracted** → Files được upload vào `/input/data/`
4. **Check option** → Nếu "Delete ZIP file after extraction" = ✅
5. **Delete Archive** → Xóa `/input/data.tar.gz` từ HDFS
6. **Result** → Chỉ còn thư mục `/input/data/` chứa file đã extract

### Trường hợp 3: Extraction thất bại

1. **Upload** → File được upload lên HDFS: `/input/corrupt.zip`
2. **Extract** → Extraction thất bại ❌
3. **Skip delete** → KHÔNG xóa file (bất kể checkbox có checked hay không)
4. **Result** → File gốc được giữ nguyên: `/input/corrupt.zip`

## 📊 Log output mẫu

### Khi checkbox CHECKED (xóa file):
```
[17:05:45] Step 2.5/4: Extracting ZIP with Java...
[17:05:45] 📦 Step 1: Extracting ZIP file with Java...
[17:05:45] 📦 Extracting with Java: /tmp/data.zip
[17:05:48] ✅ Extraction successful!
[17:05:48]    Extracted 3 files
[17:05:48] ✅ Extracted and uploaded 3 file(s) to HDFS
[17:05:48] 📁 Location: /input/
[17:05:48] 🗑️ Deleting ZIP file from HDFS...
[17:05:49] ✅ Deleted ZIP file from HDFS: data.zip  ← XÓA THÀNH CÔNG
```

### Khi checkbox UNCHECKED (giữ file):
```
[17:05:45] Step 2.5/4: Extracting ZIP with Java...
[17:05:45] 📦 Step 1: Extracting ZIP file with Java...
[17:05:45] 📦 Extracting with Java: /tmp/data.zip
[17:05:48] ✅ Extraction successful!
[17:05:48]    Extracted 3 files
[17:05:48] ✅ Extracted and uploaded 3 file(s) to HDFS
[17:05:48] 📁 Location: /input/
                                                        ← KHÔNG XÓA
```

### Khi extraction thất bại:
```
[17:05:45] Step 2.5/4: Extracting ZIP with Java...
[17:05:45] 📦 Step 1: Extracting ZIP file with Java...
[17:05:45] 📦 Extracting with Java: /tmp/corrupt.zip
[17:05:46] ❌ Extraction failed: ERROR: Invalid ZIP format
[17:05:46] ⚠️ Extraction failed: Extraction failed
[17:05:46] ℹ️ ZIP file uploaded without extraction   ← GIỮ FILE
```

## 💡 Use cases

### Use Case 1: Tiết kiệm dung lượng HDFS
**Tình huống:** Upload file ZIP 1GB, extract ra 3GB  
**Không xóa:** Tốn 4GB (1GB ZIP + 3GB extracted)  
**Có xóa:** Chỉ tốn 3GB (extracted files)  
**Tiết kiệm:** 25% dung lượng

### Use Case 2: Upload nhiều file ZIP
**Tình huống:** Upload 10 file ZIP, mỗi file 500MB  
**Không xóa:** 5GB (ZIP) + extracted data  
**Có xóa:** Chỉ có extracted data  
**Tiết kiệm:** 5GB

### Use Case 3: Debug/Archive
**Tình huống:** Cần giữ file ZIP gốc để backup hoặc debug  
**Giải pháp:** UNCHECK "Delete ZIP file after extraction"  
**Kết quả:** Có cả ZIP và extracted files

## 🎛️ Config file format

**File:** `spark_runner_config.json`

```json
{
  "hdfs_container": "namenode",
  "hdfs_path": "/input",
  "hdfs_port": "8020",
  "hdfs_host": "hdfs://namenode:8020",
  "auto_extract": true,
  "delete_after_extract": false
}
```

## ✨ Lợi ích

### Quản lý dung lượng
- ✅ **Tiết kiệm HDFS storage** - Tự động xóa file nén sau khi extract
- ✅ **Tùy chọn linh hoạt** - Người dùng quyết định xóa hay giữ
- ✅ **An toàn** - Chỉ xóa khi extract thành công

### Trải nghiệm người dùng
- ✅ **Một checkbox đơn giản** - Dễ sử dụng
- ✅ **Lưu trạng thái** - Không cần cấu hình lại mỗi lần
- ✅ **Log rõ ràng** - Biết chính xác file nào được xóa

### Kỹ thuật
- ✅ **Hỗ trợ đầy đủ** - ZIP, TAR.GZ, TGZ, TAR, GZ
- ✅ **Error handling** - Không xóa nếu extraction lỗi
- ✅ **Logging** - Ghi log đầy đủ mọi action

## 🧪 Test cases

### Test 1: ZIP file với delete enabled ✅
```
1. Upload file.zip (100MB)
2. Checkbox: ✅ Delete ZIP file after extraction
3. Extract thành công → 5 files
4. Expected: file.zip bị xóa từ HDFS
5. Result: Chỉ còn 5 files extracted
```

### Test 2: ZIP file với delete disabled ✅
```
1. Upload file.zip (100MB)
2. Checkbox: ☐ Delete ZIP file after extraction
3. Extract thành công → 5 files
4. Expected: file.zip vẫn còn trong HDFS
5. Result: Có cả file.zip VÀ 5 files extracted
```

### Test 3: Extraction thất bại ✅
```
1. Upload corrupt.zip (50MB)
2. Checkbox: ✅ Delete ZIP file after extraction
3. Extract THẤT BẠI ❌
4. Expected: corrupt.zip KHÔNG bị xóa (dù checkbox checked)
5. Result: corrupt.zip vẫn còn trong HDFS
```

### Test 4: TAR.GZ file ✅
```
1. Upload data.tar.gz (200MB)
2. Checkbox: ✅ Delete ZIP file after extraction
3. Extract thành công → data/ directory
4. Expected: data.tar.gz bị xóa
5. Result: Chỉ còn data/ directory
```

### Test 5: Save/Load config ✅
```
1. Checkbox: ✅ Delete ZIP file after extraction
2. Click "Save Config"
3. Đóng và mở lại GUI
4. Expected: Checkbox vẫn checked
5. Result: State được khôi phục đúng
```

## 📅 Ngày cập nhật
17 Tháng 10, 2025

## 👨‍💻 Tác giả
GitHub Copilot + User
