# 🎯 HƯỚNG DẪN NHANH: Cài đặt matplotlib

## ⚡ Các bước thực hiện

### 1️⃣ Chọn container
```
Container: spark-worker
```

### 2️⃣ Nhập tên thư viện
```
Tên thư viện: matplotlib
```

### 3️⃣ Nhấn nút "✅ Cài đặt"

### 4️⃣ Xử lý dialog "Build Tools Required"

Sẽ hiện popup:

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

**Nhấn "Yes"** để tiếp tục

### 5️⃣ Đợi cài đặt build tools

Console sẽ hiện:

```
================================================================================
🔧 Đang cài đặt build tools (build-base, freetype-dev, libpng-dev)...
⏰ Quá trình này mất 1-2 phút, vui lòng đợi...
================================================================================

(1/XX) Installing binutils (X.XX-rX)
(2/XX) Installing gcc (X.XX.X-rX)
(3/XX) Installing make (X.XX-rX)
...
✅ Build tools đã được cài đặt thành công!
📦 Bây giờ bạn có thể cài matplotlib, numpy, scipy, v.v.
```

### 6️⃣ Cài đặt matplotlib tiếp tục

```
================================================================================
🚀 Đang cài đặt: matplotlib
📦 Container: spark-worker
💻 Lệnh: docker exec spark-worker python3 -m pip install --no-cache-dir matplotlib
⏰ Bắt đầu lúc: 22:45:30
================================================================================

Collecting matplotlib
  Downloading matplotlib-3.5.3.tar.gz (35.2 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 35.2/35.2 MB

📥 COLLECTING 5%
⬇️ DOWNLOADING 25%
⚙️ ĐANG BUILD 60%
📦 INSTALLING 95%
✅ COMPLETE 100%

✅ Cài đặt thành công matplotlib!
⏱️ Tổng thời gian: 8m 45s
```

## 🎯 Thời gian dự kiến

| Bước | Thời gian |
|------|-----------|
| Kiểm tra build tools | 5s |
| Cài build tools (lần đầu) | 1-2 phút |
| Download matplotlib | 1 phút |
| Build matplotlib | 5-10 phút |
| Install | 30s |
| **Tổng cộng** | **~8-14 phút** |

## ✅ Dấu hiệu thành công

1. **Không có lỗi màu đỏ** trong console
2. **Progress bar đạt 100%**
3. **Thấy dòng**: `✅ Cài đặt thành công matplotlib!`
4. **Có thể list packages** và thấy matplotlib trong danh sách

## 🧪 Kiểm tra kết quả

### Cách 1: List Installed Packages

1. Nhấn nút "📋 Danh sách"
2. Tìm `matplotlib` trong bảng
3. Xem version (vd: 3.5.3)

### Cách 2: Test trong container

```bash
docker exec spark-worker python3 -c "import matplotlib; print(matplotlib.__version__)"
```

Kết quả: `3.5.3` (hoặc version khác)

### Cách 3: Test plot đơn giản

```bash
docker exec spark-worker python3 -c "
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.plot([1,2,3], [4,5,6])
plt.savefig('/tmp/test.png')
print('✅ matplotlib hoạt động!')
"
```

## 🚨 Xử lý lỗi

### Lỗi 1: Build tools cài thất bại

**Hiện tượng:**
```
❌ Không thể cài đặt build tools!
```

**Giải pháp:**
```bash
# Cài thủ công bằng terminal
docker exec -u root spark-worker apk add build-base freetype-dev libpng-dev
```

### Lỗi 2: Vẫn build fail sau khi có build tools

**Hiện tượng:**
```
ERROR: Failed building wheel for matplotlib
```

**Giải pháp:**
```bash
# Cài thêm dependencies
docker exec spark-worker apk add openblas-dev lapack-dev
```

### Lỗi 3: Timeout (quá lâu không phản hồi)

**Hiện tượng:**
- Progress bar dừng ở 60%
- Không có output mới > 5 phút

**Giải pháp:**
- **ĐỪNG TẮT APP**
- Build vẫn đang chạy
- Xem log trong terminal:
```bash
docker logs spark-worker -f
```

### Lỗi 4: Out of memory

**Hiện tượng:**
```
Killed
gcc: fatal error: Killed signal terminated program
```

**Giải pháp:**
```bash
# Tăng memory cho Docker
# Docker Desktop → Settings → Resources → Memory: 4GB+
```

## 💡 Tips & Tricks

### Tip 1: Cài build tools trước (recommended)

```bash
# Chạy lệnh này TRƯỚC khi cài matplotlib trong GUI
docker exec spark-worker apk add build-base freetype-dev libpng-dev openblas-dev lapack-dev
```

Lợi ích:
- Không cần xử lý dialog
- Nhanh hơn (không cần confirm)
- Có thể cài nhiều packages liên tiếp

### Tip 2: Test với pure Python packages trước

```
✅ requests (nhanh, 10s)
✅ beautifulsoup4 (nhanh, 15s)
✅ pyyaml (nhanh, 20s)
```

Đảm bảo GUI hoạt động đúng trước khi test matplotlib

### Tip 3: Cài numpy trước matplotlib

```
numpy → matplotlib
```

Vì matplotlib depends on numpy. Cài numpy trước giúp:
- Build tools đã có sẵn
- Faster build (đã có numpy wheel)

### Tip 4: Sử dụng pre-built wheel (nếu có)

```bash
# Thử tìm wheel trên PyPI
pip download matplotlib --only-binary :all: --platform manylinux2014_x86_64 --python-version 37

# Nếu có wheel, copy vào container và cài
docker cp matplotlib-*.whl spark-worker:/tmp/
docker exec spark-worker python3 -m pip install /tmp/matplotlib-*.whl
```

## 📊 Các packages khác cần build tools

Sau khi cài build tools 1 lần, bạn có thể cài:

### Data Science:
- ✅ **numpy** - Numerical computing
- ✅ **scipy** - Scientific computing  
- ✅ **pandas** - Data analysis
- ✅ **scikit-learn** - Machine learning

### Image Processing:
- ✅ **pillow** - Image library
- ✅ **opencv-python** - Computer vision

### Other:
- ✅ **lxml** - XML/HTML parser
- ✅ **cryptography** - Crypto library
- ✅ **psycopg2** - PostgreSQL driver

## 🎓 Hiểu về build process

### Tại sao cần build tools?

matplotlib là **Python package có C extensions**:

```
matplotlib
├── Pure Python code (*.py)
└── C/C++ extensions (*.c, *.cpp)
    ├── FreeType2 (fonts rendering)
    ├── libpng (PNG images)
    └── NumPy (array operations)
```

Để compile C/C++ code cần:
- **make**: Build automation
- **gcc**: GNU C compiler
- **g++**: GNU C++ compiler
- **freetype-dev**: FreeType headers
- **libpng-dev**: PNG library headers

### Build from source vs Pre-built wheel

**Build from source** (chậm):
```
Download .tar.gz → Extract → Configure → Compile → Link → Install
                                 ↑
                          Cần build tools
```

**Pre-built wheel** (nhanh):
```
Download .whl → Extract → Install
```

Alpine Linux thường không có pre-built wheels vì kiến trúc khác (musl libc vs glibc)

---

## ✨ Tóm tắt 1 dòng

```
Chọn spark-worker → Nhập matplotlib → Cài đặt → Yes (build tools) → Đợi 8-14 phút → Done ✅
```

**Good luck!** 🚀
