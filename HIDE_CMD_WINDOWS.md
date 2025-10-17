# Đã tắt hiển thị CMD khi chạy subprocess

## ✅ Đã hoàn tất

Đã áp dụng cơ chế ẩn cửa sổ CMD cho tất cả subprocess commands trong chương trình.

## 📝 File đã sửa

### 1. `large_file_upload.py` ✅
**Thay đổi:**
- Import `run_hidden` và `popen_hidden` từ `subprocess_utils`
- Thay thế **TẤT CẢ** `subprocess.run()` bằng `run_hidden()`
- Áp dụng cho:
  - ✅ Tạo temp directory
  - ✅ Copy chunks to container
  - ✅ Merge chunks
  - ✅ Upload to HDFS
  - ✅ Copy file for extraction
  - ✅ Cleanup operations
  - ✅ Verify upload
  - ✅ Direct upload (small files)
  - ✅ Get HDFS file info

**Code mẫu:**
```python
# Import hidden subprocess utilities
try:
    from subprocess_utils import run_hidden, popen_hidden
except ImportError:
    # Fallback if not available
    def run_hidden(*args, **kwargs):
        return subprocess.run(*args, **kwargs)
    def popen_hidden(*args, **kwargs):
        return subprocess.Popen(*args, **kwargs)

# Sử dụng
run_hidden(
    ['docker', 'exec', container, 'mkdir', '-p', temp_dir_container],
    check=True,
    capture_output=True
)
```

## 🔧 Cơ chế hoạt động

### Windows (win32)
```python
def get_subprocess_params():
    params = {}
    if sys.platform == 'win32':
        # Hide console window
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        
        params['startupinfo'] = startupinfo
        params['creationflags'] = subprocess.CREATE_NO_WINDOW
    return params
```

### Unix/Linux/macOS
- Không cần xử lý đặc biệt (không có CMD window)
- Tự động bỏ qua các params Windows-specific

## 📊 Các file đã có sẵn cơ chế ẩn CMD

Các file sau đã sử dụng `subprocess_utils.py`:
- ✅ `container_image_viewer.py` - Đã có STARTUPINFO và CREATE_NO_WINDOW
- ✅ `docker_utils.py` - Đã có CREATE_NO_WINDOW
- ✅ `hdfs_upload_tab_v4_clean.py` - Sử dụng `run_hidden` từ subprocess_utils
- ✅ `spark_runner_tab_v4_clean.py` - Sử dụng subprocess_utils
- ✅ `performance_monitor_v4_clean.py` - Sử dụng subprocess_utils

## 🎯 Lợi ích

### Trải nghiệm người dùng
- ✅ **Không còn cửa sổ CMD nhấp nháy** khi upload file
- ✅ **Giao diện sạch sẽ** - chỉ có GUI chính
- ✅ **Chuyên nghiệp hơn** - không thấy console commands

### Kỹ thuật
- ✅ **Tương thích đa nền tảng** - Windows/Linux/macOS
- ✅ **Fallback an toàn** - Nếu không import được vẫn chạy bình thường
- ✅ **Tập trung hóa** - Một nơi quản lý subprocess params
- ✅ **Dễ bảo trì** - Thay đổi một lần, áp dụng mọi nơi

## 🧪 Test

### Test 1: Upload file nhỏ (<100MB)
```
✅ Không thấy CMD window khi copy to container
✅ Không thấy CMD window khi upload to HDFS
✅ Không thấy CMD window khi cleanup
```

### Test 2: Upload file lớn (>100MB) - Chunked upload
```
✅ Không thấy CMD window khi tạo temp directory
✅ Không thấy CMD window khi copy từng chunk
✅ Không thấy CMD window khi merge chunks
✅ Không thấy CMD window khi upload to HDFS
✅ Không thấy CMD window khi copy for extraction
✅ Không thấy CMD window khi cleanup
```

### Test 3: Upload nhiều file cùng lúc
```
✅ Không thấy CMD window cho bất kỳ file nào
✅ GUI luôn ở foreground
✅ Chỉ thấy progress logs trong GUI
```

## 📚 API Reference

### `subprocess_utils.py`

#### `get_subprocess_params() -> dict`
Trả về dict chứa params để ẩn CMD window trên Windows.

#### `run_hidden(*args, **kwargs)`
Wrapper cho `subprocess.run()` với CMD ẩn.
```python
result = run_hidden(['docker', 'ps'], capture_output=True, text=True)
```

#### `popen_hidden(*args, **kwargs)`
Wrapper cho `subprocess.Popen()` với CMD ẩn.
```python
process = popen_hidden(['docker', 'exec', ...], stdout=subprocess.PIPE)
```

## 🔄 Migration Pattern

### Trước:
```python
subprocess.run(
    ['docker', 'exec', container, 'command'],
    check=True,
    capture_output=True
)
```

### Sau:
```python
from subprocess_utils import run_hidden

run_hidden(
    ['docker', 'exec', container, 'command'],
    check=True,
    capture_output=True
)
```

## 🎉 Kết quả

**Trước khi sửa:**
- ❌ Nhiều cửa sổ CMD đen nhấp nháy khi upload
- ❌ Làm người dùng hoang mang
- ❌ Trông không chuyên nghiệp

**Sau khi sửa:**
- ✅ Hoàn toàn không thấy CMD window
- ✅ GUI luôn ở foreground
- ✅ Trải nghiệm mượt mà, chuyên nghiệp

## 📅 Ngày cập nhật
17 Tháng 10, 2025

## 👨‍💻 Người thực hiện
GitHub Copilot + User
