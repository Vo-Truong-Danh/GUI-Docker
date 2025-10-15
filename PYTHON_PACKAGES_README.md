# 📦 Tính năng mới: Python Packages Manager

## Tổng quan

Tab **Python Packages** giúp cài đặt thư viện Python vào Spark Docker containers một cách dễ dàng, không cần dùng terminal.

## Cách sử dụng nhanh

### 1. Mở tab "📦 Python Packages"

### 2. Chọn container
```
Container: spark-worker (mặc định)
```

### 3. Cài thư viện

**Cách 1: Nhập tên**
```
Tên thư viện: matplotlib==3.5.3
```

**Cách 2: Chọn từ danh sách phổ biến**
```
Hoặc chọn: [matplotlib] ▼
```

### 4. Nhấn "✅ Cài đặt"

## Ví dụ

### Cài matplotlib (như lệnh CLI của bạn)
```
Container: spark-worker
Tên thư viện: matplotlib==3.5.3
Tùy chọn: ✓ Không dùng cache
→ Nhấn "✅ Cài đặt"
```

**Lệnh tương đương**:
```bash
docker exec spark-worker python3 -m pip install --no-cache-dir "matplotlib==3.5.3"
```

### Cài nhiều thư viện cùng lúc
```
Tên thư viện: pandas numpy scikit-learn
```

### Xem thư viện đã cài
```
→ Nhấn "📋 Xem đã cài"
```

### Gỡ thư viện
```
1. Nhấn "📋 Xem đã cài"
2. Click chọn thư viện trong bảng
3. Nhấn "🗑️ Gỡ thư viện"
```

## Thư viện phổ biến có sẵn

- **Visualization**: matplotlib, seaborn, plotly
- **Data**: pandas, numpy, scipy
- **ML**: scikit-learn, xgboost, lightgbm
- **DL**: torch, tensorflow, keras
- **Image**: opencv-python, pillow
- **Web**: requests, beautifulsoup4, fastapi

## Tính năng

- ✅ Cài đặt thư viện với chỉ định phiên bản
- ✅ Xem danh sách đã cài (tên, phiên bản, đường dẫn)
- ✅ Gỡ thư viện không cần thiết
- ✅ Real-time output trong console
- ✅ Hỗ trợ nhiều containers
- ✅ Danh sách 20+ thư viện phổ biến

## Lưu ý

⚠️ **Thư viện sẽ mất khi xóa container**

**Giải pháp**:
- Thêm vào `requirements.txt` trong Dockerfile
- Hoặc mount volume chứa thư viện
- Hoặc cài lại sau khi khởi động container

## Xem thêm

Chi tiết đầy đủ: [PYTHON_PACKAGES_GUIDE.md](PYTHON_PACKAGES_GUIDE.md)

---

**Phiên bản**: 1.0.0  
**Ngày**: 2025-10-15
