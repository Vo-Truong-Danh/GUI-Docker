# 🔧 Fix matplotlib Build Error - Build Tools Auto-Install

## 📋 Vấn đề

Khi cài matplotlib trong Docker container Alpine Linux, bị lỗi:

```
GNU make (>= 3.80) or makepp (>= 1.19) is required to build FreeType2.
subprocess.CalledProcessError: Command '['./configure', ...] returned non-zero exit status 1.
ERROR: Failed building wheel for matplotlib
```

### Nguyên nhân:
- Alpine Linux container thiếu **C build tools** (make, gcc, freetype-dev)
- matplotlib cần compile FreeType2 từ source
- pip cố gắng build wheel từ source nhưng thất bại

## ✅ Giải pháp đã triển khai

### 1. **Tự động phát hiện và đề nghị cài build tools**

File: `python_packages_tab.py`

Thêm method mới: `check_and_install_build_tools()`

**Chức năng:**
- Phát hiện Alpine Linux container
- Kiểm tra xem `make` đã cài chưa
- Nếu chưa: hiện dialog hỏi user có muốn cài không
- Tự động cài: `build-base`, `freetype-dev`, `libpng-dev`, `openblas-dev`, `lapack-dev`

**Cách hoạt động:**

```python
def check_and_install_build_tools(self, container):
    """Kiểm tra và cài đặt build tools nếu cần (cho Alpine Linux)"""
    
    # 1. Kiểm tra OS
    cat /etc/os-release → xem có "alpine" không
    
    # 2. Kiểm tra make
    which make → nếu không tìm thấy → returncode != 0
    
    # 3. Hỏi user
    messagebox.askyesno(
        "Build Tools Required",
        "⚠️ Container thiếu build tools..."
    )
    
    # 4. Cài đặt
    docker exec <container> apk add build-base freetype-dev libpng-dev openblas-dev lapack-dev
    
    # 5. Báo kết quả
    return True/False
```

### 2. **Tích hợp vào install flow**

Trong method `install_package()`:

```python
# Danh sách thư viện cần compile
compile_packages = [
    'matplotlib', 'numpy', 'scipy', 'pandas', 
    'pillow', 'lxml', 'cryptography', 'psycopg2'
]

# Kiểm tra trước khi cài
if any(pkg in package.lower() for pkg in compile_packages):
    if not self.check_and_install_build_tools(container):
        return  # Hủy cài đặt
```

## 🚀 Cách sử dụng

### Scenario 1: Cài matplotlib (lần đầu)

1. **Chọn container**: `spark-worker`
2. **Nhập package**: `matplotlib`
3. **Nhấn "Cài đặt"**

→ App sẽ hiện dialog:

```
⚠️ Container thiếu build tools (make, gcc, freetype, etc.)

Một số thư viện như matplotlib, numpy, scipy cần build tools
để compile từ source code.

Bạn có muốn cài đặt build tools không?
(Sẽ mất khoảng 1-2 phút)

💡 Tip: Nếu không muốn cài, bạn có thể thử thư viện khác
hoặc dùng pre-built wheel nếu có sẵn.

[Yes] [No]
```

4. **Nhấn "Yes"**:
   - App cài: `build-base`, `freetype-dev`, `libpng-dev`, `openblas-dev`, `lapack-dev`
   - Mất 1-2 phút
   - Sau đó tiếp tục cài matplotlib

5. **Nhấn "No"**:
   - Cài đặt bị hủy
   - App gợi ý cài thư viện pure Python

### Scenario 2: Build tools đã có

1. Nếu đã cài build tools rồi (hoặc không phải Alpine)
2. App tự động skip dialog
3. Cài đặt package bình thường

## 📦 Build tools được cài đặt

```bash
apk add build-base freetype-dev libpng-dev openblas-dev lapack-dev
```

**build-base**: make, gcc, g++, libc-dev (GNU build tools)  
**freetype-dev**: FreeType2 headers (cho matplotlib fonts)  
**libpng-dev**: PNG image library (cho matplotlib, pillow)  
**openblas-dev**: Optimized BLAS (cho numpy, scipy)  
**lapack-dev**: Linear algebra (cho scipy)

## 🎯 Các thư viện được hỗ trợ

### Cần build tools (auto-check):
- ✅ **matplotlib** - Plotting library
- ✅ **numpy** - Numerical computing
- ✅ **scipy** - Scientific computing
- ✅ **pandas** - Data analysis
- ✅ **pillow** - Image processing
- ✅ **lxml** - XML/HTML parser
- ✅ **cryptography** - Cryptographic recipes
- ✅ **psycopg2** - PostgreSQL adapter

### Không cần build tools (pure Python):
- ✅ **requests** - HTTP library
- ✅ **beautifulsoup4** - HTML/XML parser
- ✅ **pyyaml** - YAML parser
- ✅ **click** - CLI framework
- ✅ **flask** - Web framework
- ✅ **pytest** - Testing framework

## 🔍 Troubleshooting

### Vấn đề 1: Dialog không hiện

**Nguyên nhân**: Container không phải Alpine Linux  
**Giải pháp**: Không cần build tools (OS khác đã có sẵn)

### Vấn đề 2: Cài build tools thất bại

**Nguyên nhân**: Không có quyền root trong container  
**Giải pháp**: 
```bash
docker exec -u root <container> apk add build-base
```

### Vấn đề 3: Vẫn build fail sau khi cài build tools

**Nguyên nhân**: Thiếu thư viện khác (tùy package)  
**Giải pháp**: Xem log lỗi, cài thêm:
```bash
# matplotlib
apk add freetype-dev libpng-dev

# numpy/scipy
apk add openblas-dev lapack-dev gfortran

# pillow
apk add jpeg-dev zlib-dev

# lxml
apk add libxml2-dev libxslt-dev
```

### Vấn đề 4: Muốn skip build, dùng pre-built wheel

**Giải pháp**: Thêm flag vào lệnh pip:
```bash
docker exec spark-worker python3 -m pip install matplotlib --only-binary :all:
```

(GUI chưa có option này - có thể thêm sau)

## 📊 Timeline cài đặt

| Step | Mô tả | Thời gian |
|------|-------|-----------|
| 1 | Kiểm tra build tools | ~5s |
| 2 | Cài build tools (nếu cần) | ~1-2 phút |
| 3 | Download matplotlib | ~1 phút |
| 4 | Build matplotlib từ source | ~5-10 phút |
| 5 | Install matplotlib | ~30s |
| **Tổng** | **Lần đầu với build tools** | **~8-14 phút** |
| **Tổng** | **Lần sau (đã có build tools)** | **~7-12 phút** |

## 🎓 Lưu ý cho người dùng

### ✅ Best Practices:

1. **Cài build tools 1 lần**: Sau đó có thể cài nhiều thư viện
2. **Chờ đợi kiên nhẫn**: Compile từ source mất thời gian
3. **Theo dõi log**: Progress bar + console output
4. **Thử pure Python packages trước**: requests, beautifulsoup4

### ⚠️ Cảnh báo:

1. **Không tắt app** trong khi đang build (5-15 phút)
2. **Không spam click** nút "Cài đặt" nhiều lần
3. **Kiểm tra disk space**: Build cần ~200-500MB temp space
4. **Build tools tốn RAM**: Container cần ít nhất 2GB RAM

## 📝 Code Changes Summary

### Files Modified:

**python_packages_tab.py** (2 changes):

1. **New method** (lines ~337-415):
   - `check_and_install_build_tools(container)`
   - 80 dòng code mới

2. **Modified method** (lines ~430-445):
   - `install_package()` 
   - Thêm 15 dòng check build tools

**Total**: +95 dòng code

### Dependencies:

Không cần thư viện Python mới. Chỉ dùng:
- `subprocess` (có sẵn)
- `tkinter.messagebox` (có sẵn)

## 🧪 Testing

### Test Case 1: Cài matplotlib (không có build tools)

**Steps:**
1. Container Alpine mới (chưa có build tools)
2. Chọn container, nhập "matplotlib"
3. Nhấn "Cài đặt"
4. Nhấn "Yes" ở dialog

**Expected:**
- Dialog hiện "Build Tools Required"
- Cài build tools (1-2 phút)
- Hiện "✅ Build tools đã được cài đặt!"
- Tiếp tục cài matplotlib
- matplotlib cài thành công

### Test Case 2: Cài requests (pure Python)

**Steps:**
1. Container bất kỳ
2. Nhập "requests"
3. Nhấn "Cài đặt"

**Expected:**
- Không hiện dialog build tools
- Cài đặt trực tiếp (nhanh, ~10-30s)
- Thành công

### Test Case 3: User từ chối cài build tools

**Steps:**
1. Container không có build tools
2. Nhập "matplotlib"
3. Nhấn "Cài đặt"
4. Nhấn "No" ở dialog

**Expected:**
- Cài đặt bị hủy
- Log hiện tips:
  ```
  ⚠️ Cài đặt bị hủy do thiếu build tools.
  💡 Tip: Bạn có thể thử:
     1. Cài các thư viện pure Python: requests, beautifulsoup4, pyyaml
     2. Hoặc cài lại build tools bằng lệnh:
        docker exec spark-worker apk add build-base freetype-dev libpng-dev
  ```

### Test Case 4: Container đã có build tools

**Steps:**
1. Đã cài build tools trước đó
2. Nhập "matplotlib"
3. Nhấn "Cài đặt"

**Expected:**
- Không hiện dialog (skip check)
- Cài đặt trực tiếp
- Build thành công

## 🌟 Future Enhancements

### Idea 1: Add checkbox "Prefer Binary"
```python
self.prefer_binary_var = tk.BooleanVar(value=False)
ttk.Checkbutton(frame, text="Prefer pre-built wheels", 
                variable=self.prefer_binary_var)
```

Khi enable: Thêm `--only-binary :all:` vào pip command

### Idea 2: Cache build tools status
```python
self.build_tools_cache = {}  # {container_name: True/False}
```

Tránh check nhiều lần cho cùng container

### Idea 3: Show build tools version
```python
docker exec <container> make --version
docker exec <container> gcc --version
```

Hiện trong log để debug

### Idea 4: Custom build tools packages
```python
# Cho từng thư viện khác nhau
build_deps = {
    'matplotlib': ['build-base', 'freetype-dev', 'libpng-dev'],
    'pillow': ['build-base', 'jpeg-dev', 'zlib-dev'],
    'lxml': ['build-base', 'libxml2-dev', 'libxslt-dev'],
}
```

Chỉ cài packages cần thiết

## 📚 References

- [Alpine Linux packages](https://pkgs.alpinelinux.org/)
- [matplotlib build docs](https://matplotlib.org/stable/devel/dependencies.html)
- [pip build options](https://pip.pypa.io/en/stable/cli/pip_install/)
- [Docker exec docs](https://docs.docker.com/engine/reference/commandline/exec/)

## ✨ Tóm tắt

**Trước đây:**
- Cài matplotlib → Build fail → User không biết lỗi gì
- Phải tự vào container chạy `apk add...`

**Bây giờ:**
- Cài matplotlib → App tự phát hiện thiếu build tools
- Hỏi user có muốn cài không → Tự động cài
- Tiếp tục cài matplotlib → Thành công ✅

**Impact:**
- User experience tốt hơn (không bị stuck)
- Tự động hóa common task
- Giảm confusion cho người mới
- Progress bar vẫn hoạt động đúng

---

**Version**: 1.0  
**Date**: 2025-10-15  
**Author**: GitHub Copilot  
**Status**: ✅ Implemented & Ready for Testing
