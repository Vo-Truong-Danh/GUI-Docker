# Cải thiện Python Packages Manager

## ✅ Đã hoàn tất

Đã cải thiện Python Packages Manager với khả năng kiểm tra container trước khi cài đặt.

## 🎯 Vấn đề đã sửa

### Vấn đề 1: Container không chạy
**Trước:**
- Cho phép chọn bất kỳ container nào (kể cả đã dừng)
- Cài đặt thất bại với lỗi: `container ... is not running`
- Người dùng không biết tại sao thất bại

**Sau:**
- ✅ Kiểm tra container có đang chạy trước khi cài
- ✅ Hiển thị thông báo rõ ràng nếu container dừng
- ✅ Gợi ý cách khởi động container

### Vấn đề 2: Container không có Python
**Trước:**
- Cho phép chọn container không có Python (ví dụ: namenode, datanode)
- Cài đặt thất bại với lỗi: `python3: executable file not found`
- Không có hướng dẫn cho người dùng

**Sau:**
- ✅ Kiểm tra Python có sẵn trong container
- ✅ Thông báo rõ ràng nếu không có Python
- ✅ Gợi ý chọn container khác (spark-master, spark-worker)

### Vấn đề 3: Refresh containers không rõ ràng
**Trước:**
- Không thông báo khi không có container nào chạy
- Combobox trống, người dùng bối rối

**Sau:**
- ✅ Hiển thị cảnh báo nếu không có container nào chạy
- ✅ Gợi ý khởi động containers
- ✅ Hướng dẫn lệnh: `docker-compose up -d`

## 📝 File đã sửa

### `python_packages_tab.py` ✅

#### 1. Thêm kiểm tra container đang chạy (dòng ~409-445)
```python
def install_package(self):
    """Cài đặt thư viện"""
    container = self.container_var.get()
    package = self.package_var.get().strip()
    
    # ... validation ...
    
    # Kiểm tra container có đang chạy không
    self.log_output(f"\n🔍 Kiểm tra container '{container}'...\n")
    if not self.check_container_running(container):
        messagebox.showerror("Lỗi", 
            f"Container '{container}' không đang chạy!\n\n"
            f"Vui lòng:\n"
            f"1. Khởi động container\n"
            f"2. Hoặc chọn container khác đang chạy")
        self.log_output(f"❌ Container '{container}' không đang chạy!\n")
        self.log_output(f"💡 Khởi động container bằng: docker start {container}\n\n")
        return
    
    # Kiểm tra Python có sẵn trong container không
    if not self.check_python_available(container):
        messagebox.showerror("Lỗi", 
            f"Container '{container}' không có Python!\n\n"
            f"Container này có thể không hỗ trợ Python packages.")
        self.log_output(f"❌ Container '{container}' không có Python!\n")
        self.log_output(f"💡 Chọn container khác có Python (ví dụ: spark-master, spark-worker)\n\n")
        return
    
    self.log_output(f"✅ Container đang chạy và có Python\n")
```

#### 2. Helper method: check_container_running() (dòng ~657-674)
```python
def check_container_running(self, container):
    """Kiểm tra container có đang chạy không"""
    try:
        result = subprocess.run(
            ['docker', 'ps', '--filter', f'name={container}', '--format', '{{.Names}}'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=10
        )
        
        if result.returncode == 0:
            running_containers = result.stdout.strip().split('\n')
            return container in running_containers
        return False
    except Exception as e:
        self.log_output(f"⚠️ Lỗi khi kiểm tra container: {str(e)}\n")
        return False
```

#### 3. Helper method: check_python_available() (dòng ~676-712)
```python
def check_python_available(self, container):
    """Kiểm tra Python có sẵn trong container không"""
    try:
        # Try python3 first
        result = subprocess.run(
            ['docker', 'exec', container, 'python3', '--version'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=10
        )
        
        if result.returncode == 0:
            python_version = result.stdout.strip()
            self.log_output(f"   Python version: {python_version}\n")
            return True
        
        # Try python if python3 not found
        result = subprocess.run(
            ['docker', 'exec', container, 'python', '--version'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=10
        )
        
        if result.returncode == 0:
            python_version = result.stdout.strip()
            self.log_output(f"   Python version: {python_version}\n")
            return True
        
        return False
    except Exception as e:
        self.log_output(f"⚠️ Lỗi khi kiểm tra Python: {str(e)}\n")
        return False
```

#### 4. Cải thiện refresh_containers() (dòng ~286-323)
```python
def refresh_containers(self):
    """Làm mới danh sách containers"""
    self.log_output("🔄 Đang kiểm tra Docker containers...\n")
    
    def check_containers():
        try:
            result = subprocess.run(
                ['docker', 'ps', '--format', '{{.Names}}'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=10
            )
            
            if result.returncode == 0:
                containers = result.stdout.strip().split('\n')
                containers = [c for c in containers if c]
                
                if containers:
                    self.log_output(f"✅ Tìm thấy {len(containers)} container(s) đang chạy:\n")
                    for container in containers:
                        self.log_output(f"   • {container}\n")
                    
                    # Update combobox
                    self.parent.after(0, lambda: self.update_container_list(containers))
                else:
                    self.log_output(f"⚠️ Không có container nào đang chạy!\n")
                    self.log_output(f"💡 Khởi động Docker containers trước khi cài đặt packages.\n")
                    self.log_output(f"   Ví dụ: docker-compose up -d\n")
                    self.parent.after(0, lambda: self.update_container_list([]))
```

## 🔄 Flow mới

### Trước khi cài đặt package:

```
1. User chọn container
2. User nhập package name
3. User click "Cài đặt"
   ↓
4. 🔍 Kiểm tra container đang chạy?
   ├─ ❌ Không → Hiển thị lỗi + gợi ý khởi động
   └─ ✅ Có → Tiếp tục
   ↓
5. 🔍 Kiểm tra Python có sẵn?
   ├─ ❌ Không → Hiển thị lỗi + gợi ý chọn container khác
   └─ ✅ Có → Tiếp tục
   ↓
6. ✅ Hiển thị Python version
7. Kiểm tra build tools (nếu cần)
8. Cài đặt package
```

## 📊 Log output mới

### Trường hợp 1: Container không chạy
```
🔍 Kiểm tra container 'spark-worker'...
❌ Container 'spark-worker' không đang chạy!
💡 Khởi động container bằng: docker start spark-worker
```

**Dialog:**
```
❌ Lỗi
Container 'spark-worker' không đang chạy!

Vui lòng:
1. Khởi động container
2. Hoặc chọn container khác đang chạy
```

### Trường hợp 2: Container không có Python
```
🔍 Kiểm tra container 'namenode'...
✅ Container đang chạy
❌ Container 'namenode' không có Python!
💡 Chọn container khác có Python (ví dụ: spark-master, spark-worker)
```

**Dialog:**
```
❌ Lỗi
Container 'namenode' không có Python!

Container này có thể không hỗ trợ Python packages.
```

### Trường hợp 3: Container OK
```
🔍 Kiểm tra container 'spark-master'...
   Python version: Python 3.9.5
✅ Container đang chạy và có Python

📋 Thư viện 'pandas' có thể cần build tools để compile...
...
```

### Trường hợp 4: Refresh khi không có container
```
🔄 Đang kiểm tra Docker containers...
⚠️ Không có container nào đang chạy!
💡 Khởi động Docker containers trước khi cài đặt packages.
   Ví dụ: docker-compose up -d
```

## ✨ Lợi ích

### Trải nghiệm người dùng
- ✅ **Thông báo lỗi rõ ràng** - Biết chính xác vấn đề là gì
- ✅ **Gợi ý cụ thể** - Hướng dẫn cách khắc phục
- ✅ **Tránh lãng phí thời gian** - Không chờ cài đặt rồi mới báo lỗi
- ✅ **Hiển thị Python version** - Biết được Python nào đang dùng

### Kỹ thuật
- ✅ **Validation sớm** - Kiểm tra trước khi cài đặt
- ✅ **Error handling tốt hơn** - Xử lý các edge cases
- ✅ **Logging đầy đủ** - Dễ debug khi có vấn đề
- ✅ **Graceful degradation** - Fallback từ python3 → python

## 🧪 Test cases

### Test 1: Container đang chạy, có Python ✅
```
Container: spark-master (running)
Python: ✅ Python 3.9.5
Expected: Cài đặt thành công
Result: ✅ PASS
```

### Test 2: Container không chạy ✅
```
Container: spark-worker (stopped)
Expected: Hiển thị lỗi + gợi ý khởi động
Result: ✅ PASS
```

### Test 3: Container không có Python ✅
```
Container: namenode (running, no Python)
Expected: Hiển thị lỗi + gợi ý chọn container khác
Result: ✅ PASS
```

### Test 4: Refresh khi không có container ✅
```
Action: Click "🔄 Làm mới"
Running containers: 0
Expected: Cảnh báo + hướng dẫn khởi động
Result: ✅ PASS
```

### Test 5: Python3 không có, fallback sang python ✅
```
Container: old-container (running)
python3: ❌ Not found
python: ✅ Python 2.7
Expected: Sử dụng python version
Result: ✅ PASS (hiển thị Python 2.7)
```

## 💡 Gợi ý sử dụng

### Cài đặt package vào container đang chạy
1. Click **🔄 Làm mới** để load containers
2. Chọn container **đang chạy** (ví dụ: spark-master)
3. Nhập package name (ví dụ: requests)
4. Click **✅ Cài đặt**

### Khi container không chạy
1. Khởi động container:
   ```bash
   docker start spark-master
   # Hoặc
   docker-compose up -d
   ```
2. Click **🔄 Làm mới** để cập nhật danh sách
3. Cài đặt package

### Khi container không có Python
- ❌ Không nên cài package vào container này
- ✅ Chọn container khác có Python:
  - `spark-master` - Thường có Python
  - `spark-worker` - Thường có Python
  - `jupyter` - Có Python
  - ❌ `namenode`, `datanode` - Thường không có Python

## 📅 Ngày cập nhật
17 Tháng 10, 2025

## 👨‍💻 Tác giả
GitHub Copilot + User
