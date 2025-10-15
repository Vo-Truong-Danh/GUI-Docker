# 🔧 Fix Build Tools Conflict Error

## ❌ Lỗi gặp phải

```
ERROR: openblas-dev-0.3.6-r0: trying to overwrite usr/include/cblas.h owned by lapack-dev-3.8.0-r1.
ERROR: openblas-dev-0.3.6-r0: trying to overwrite usr/include/lapacke.h owned by lapack-dev-3.8.0-r1.
...
❌ Không thể cài đặt build tools!
```

## 🔍 Nguyên nhân

**Package conflict**: `openblas-dev` và `lapack-dev` cùng cung cấp các file header:
- `cblas.h`
- `lapacke.h`
- `lapacke_mangling.h`
- `lapacke_config.h`
- `lapacke_utils.h`

Alpine Linux package manager (apk) không cho phép 2 package cùng own 1 file.

## ✅ Giải pháp

### Cách 1: Chỉ cài minimal packages (RECOMMENDED)

```bash
docker exec spark-worker apk add --no-cache build-base freetype-dev libpng-dev
```

**Lý do:**
- matplotlib **CHỈ CẦN** build-base (make, gcc) và freetype-dev
- **KHÔNG CẦN** openblas hoặc lapack (chỉ numpy/scipy mới cần)

### Cách 2: Force overwrite (NOT RECOMMENDED)

```bash
docker exec spark-worker apk add --force-overwrite build-base freetype-dev libpng-dev openblas-dev lapack-dev
```

**Nhược điểm:** Có thể gây xung đột sau này.

## 📦 Build tools cần thiết cho từng package

| Package | Build tools cần thiết |
|---------|----------------------|
| **matplotlib** | build-base, freetype-dev, libpng-dev |
| **numpy** | build-base, openblas-dev (hoặc lapack-dev) |
| **scipy** | build-base, openblas-dev, gfortran |
| **pillow** | build-base, jpeg-dev, zlib-dev, freetype-dev |
| **pandas** | build-base (chỉ cần nếu build từ source) |
| **lxml** | build-base, libxml2-dev, libxslt-dev |

## 🔧 Code đã fix

File: `python_packages_tab.py`

**Trước:**
```python
install_cmd = [
    'docker', 'exec', container, 'apk', 'add',
    'build-base', 'freetype-dev', 'libpng-dev', 'openblas-dev', 'lapack-dev'
]
```

**Sau:**
```python
# Cài minimal build tools (không cài openblas/lapack vì conflict với nhau)
install_cmd = [
    'docker', 'exec', container, 'apk', 'add', '--no-cache',
    'build-base', 'freetype-dev', 'libpng-dev'
]
```

**Changes:**
1. ❌ Removed: `openblas-dev`, `lapack-dev`
2. ✅ Added: `--no-cache` flag
3. ✅ Added comment giải thích

## ✅ Kết quả

```bash
PS> docker exec spark-worker apk add --no-cache build-base freetype-dev libpng-dev
fetch http://dl-cdn.alpinelinux.org/alpine/v3.10/main/x86_64/APKINDEX.tar.gz
fetch http://dl-cdn.alpinelinux.org/alpine/v3.10/community/x86_64/APKINDEX.tar.gz
(1/10) Installing libmagic (5.37-r1)
(2/10) Installing file (5.37-r1)
(3/10) Installing make (4.2.1-r2)
(4/10) Installing fortify-headers (1.1-r0)
(5/10) Installing build-base (0.5-r1)
...
✅ OK: 625 MiB in 116 packages
```

Build tools đã được cài đặt thành công! 🎉

## 🚀 Test matplotlib

```bash
docker exec spark-worker python3 -m pip install --no-cache-dir matplotlib
```

Output:
```
Collecting matplotlib
  Downloading matplotlib-3.5.3.tar.gz (35.2 MB)
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Building wheel for matplotlib (pyproject.toml) ... [đang chạy]
```

Sẽ mất **6-10 phút** để build thành công.

## 💡 Lưu ý

### Nếu cần numpy/scipy sau này:

```bash
# Option 1: Chỉ cài openblas-dev (recommended)
docker exec spark-worker apk add --no-cache openblas-dev

# Option 2: Chỉ cài lapack-dev
docker exec spark-worker apk add --no-cache lapack-dev

# KHÔNG cài cả 2 cùng lúc!
```

### Nếu đã cài conflict packages:

```bash
# Xóa 1 trong 2
docker exec spark-worker apk del openblas-dev
# Hoặc
docker exec spark-worker apk del lapack-dev

# Sau đó cài lại package còn lại
docker exec spark-worker apk add --no-cache openblas-dev
```

## 📚 References

- [Alpine Linux APK](https://wiki.alpinelinux.org/wiki/Alpine_Linux_package_management)
- [matplotlib build deps](https://matplotlib.org/stable/devel/dependencies.html)
- [openblas vs lapack conflict](https://github.com/alpinelinux/docker-alpine/issues/98)

---

**Status**: ✅ Fixed  
**Date**: 2025-10-15  
**Impact**: matplotlib build tools conflict resolved
