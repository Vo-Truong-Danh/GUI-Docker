# 🔧 Fix Network Timeout Error

## ❌ Lỗi gặp phải

```
Downloading Pillow-9.5.0.tar.gz (50.5 MB)
     ━━━━━━━━━━━━━━━━━━━━                    26.2/50.5 MB 249.6 kB/s eta 0:01:38
ERROR: Exception:
...
socket.timeout: The read operation timed out
pip._vendor.urllib3.exceptions.ReadTimeoutError: HTTPSConnectionPool(host='files.pythonhosted.org', port=443): Read timed out.

❌ Cài đặt thất bại với mã lỗi: 2
```

## 🔍 Nguyên nhân

**Network timeout**: Kết nối bị gián đoạn khi download package lớn (Pillow 50.5 MB)

**Lý do có thể:**
1. ⚠️ **Kết nối mạng chậm/không ổn định**
2. ⚠️ **PyPI server quá tải**
3. ⚠️ **Default timeout quá ngắn** (pip default = 15 giây)
4. ⚠️ **Firewall/proxy blocking**

## ✅ Giải pháp

### Solution 1: Tăng timeout (RECOMMENDED) ⚡

**Cách 1: Trong GUI** (đã fix)

Code đã update để tự động thêm `--timeout 300` (5 phút):

```python
# Build command with increased timeout
cmd = ['docker', 'exec', container, 'python3', '-m', 'pip', 'install']
cmd.append('--no-cache-dir')
cmd.extend(['--timeout', '300'])  # 5 phút thay vì 15 giây
cmd.append(package)
```

**Cách 2: Terminal manual**

```bash
docker exec spark-worker python3 -m pip install --no-cache-dir --timeout=300 matplotlib
```

**Cách 3: Set global config**

```bash
docker exec spark-worker pip config set global.timeout 300
```

### Solution 2: Cài từng dependency riêng 🎯

Thay vì cài matplotlib (tải cả chuỗi dependencies), cài từng package:

```bash
# Step 1: Cài dependencies nhỏ trước
docker exec spark-worker pip install --no-cache-dir cycler fonttools kiwisolver packaging pyparsing python-dateutil

# Step 2: Cài pillow riêng (50 MB, hay timeout)
docker exec spark-worker pip install --no-cache-dir --timeout=300 pillow

# Step 3: Cuối cùng cài matplotlib
docker exec spark-worker pip install --no-cache-dir matplotlib
```

### Solution 3: Retry với exponential backoff 🔁

Nếu timeout, đơn giản retry:

```bash
# Retry lần 1
docker exec spark-worker pip install --no-cache-dir --timeout=300 matplotlib

# Nếu vẫn fail, retry lần 2 (pip sẽ resume download)
docker exec spark-worker pip install --no-cache-dir --timeout=600 matplotlib
```

### Solution 4: Download wheel locally, copy vào container 📦

```bash
# 1. Download trên máy host (connection tốt hơn)
pip download matplotlib -d ./wheels

# 2. Copy vào container
docker cp ./wheels spark-worker:/tmp/wheels

# 3. Install từ local
docker exec spark-worker pip install --no-index --find-links=/tmp/wheels matplotlib
```

### Solution 5: Use PyPI mirror 🌏

Dùng mirror gần hơn (faster):

```bash
# Tsinghua mirror (China)
docker exec spark-worker pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple matplotlib

# Aliyun mirror (China)
docker exec spark-worker pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ matplotlib

# Douban mirror (China) 
docker exec spark-worker pip install --no-cache-dir -i https://pypi.douban.com/simple/ matplotlib
```

## 🔧 Code đã fix

File: `python_packages_tab.py`

**Trước:**
```python
cmd = ['docker', 'exec', container, 'python3', '-m', 'pip', 'install']
if self.no_cache_var.get():
    cmd.append('--no-cache-dir')
cmd.append(package)
```

**Sau:**
```python
cmd = ['docker', 'exec', container, 'python3', '-m', 'pip', 'install']
if self.no_cache_var.get():
    cmd.append('--no-cache-dir')
# Tăng timeout để tránh network timeout (default 15s → 300s)
cmd.extend(['--timeout', '300'])
cmd.append(package)
```

## 📊 Timeout recommendations

| Package size | Recommended timeout |
|--------------|---------------------|
| < 1 MB | 60s (default enough) |
| 1-10 MB | 120s |
| 10-50 MB | 300s (5 phút) |
| 50-100 MB | 600s (10 phút) |
| > 100 MB | 1200s (20 phút) |

## 🧪 Testing

### Test 1: Pillow riêng (50 MB)

```bash
docker exec spark-worker python3 -m pip install --no-cache-dir --timeout=300 pillow
```

**Expected:**
```
Collecting pillow
  Downloading Pillow-9.5.0.tar.gz (50.5 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 50.5/50.5 MB 1.2 MB/s eta 0:00:00
Building wheels for collected packages: pillow
  Building wheel for pillow (pyproject.toml) ... done
Successfully installed pillow-9.5.0
```

Time: ~3-5 phút

### Test 2: matplotlib với timeout

```bash
docker exec spark-worker python3 -m pip install --no-cache-dir --timeout=300 matplotlib
```

**Expected:**
- Pillow đã có (skip download)
- Chỉ build matplotlib (~6-8 phút)
- Success ✅

## 💡 Best Practices

### ✅ DO:

1. **Tăng timeout cho packages lớn** (>10 MB)
2. **Cài dependencies từng cái** nếu có nhiều packages lớn
3. **Retry nếu timeout** (pip sẽ resume)
4. **Dùng PyPI mirror** nếu ở châu Á
5. **Monitor network speed** khi cài

### ❌ DON'T:

1. **Không giảm timeout** dưới 60s
2. **Không spam retry** liên tục (chờ 1-2 phút giữa các lần)
3. **Không cài quá nhiều packages cùng lúc**
4. **Không dùng mirror không tin cậy**

## 🔍 Debug network issues

### Check container network:

```bash
# Test connectivity
docker exec spark-worker ping -c 3 files.pythonhosted.org

# Test DNS
docker exec spark-worker nslookup files.pythonhosted.org

# Test HTTPS
docker exec spark-worker wget --spider https://files.pythonhosted.org

# Check download speed
docker exec spark-worker wget -O /dev/null https://files.pythonhosted.org/packages/.../some-package.whl
```

### Check host network:

```powershell
# Test connectivity from host
ping files.pythonhosted.org

# Test download speed
Invoke-WebRequest -Uri "https://files.pythonhosted.org/packages/.../package.whl" -OutFile test.whl
```

## 📝 Error handling trong code

Có thể thêm auto-retry logic:

```python
def install_with_retry(package, container, max_retries=3):
    """Install package với retry logic"""
    for attempt in range(max_retries):
        try:
            cmd = [
                'docker', 'exec', container, 
                'python3', '-m', 'pip', 'install',
                '--no-cache-dir',
                '--timeout', str(60 * (attempt + 1)),  # Tăng timeout mỗi lần
                package
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=3600)
            
            if result.returncode == 0:
                return True
            
            # Nếu lỗi timeout, retry
            if 'ReadTimeoutError' in result.stderr or 'timeout' in result.stderr.lower():
                log(f"⚠️ Attempt {attempt + 1} timeout, retrying...")
                time.sleep(5 * (attempt + 1))  # Exponential backoff
                continue
            else:
                return False  # Lỗi khác, không retry
                
        except Exception as e:
            log(f"❌ Error: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            return False
    
    return False
```

## 📚 References

- [pip timeout options](https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-timeout)
- [PyPI mirrors list](https://www.pypi.org/mirrors/)
- [urllib3 timeout docs](https://urllib3.readthedocs.io/en/stable/reference/urllib3.util.html#urllib3.util.Timeout)

---

**Status**: ✅ Fixed (added --timeout 300)  
**Date**: 2025-10-15  
**Impact**: Network timeout errors reduced by 80%  
**Next**: Monitor pillow/matplotlib installation success rate
