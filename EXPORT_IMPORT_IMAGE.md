# 📦 HƯỚNG DẪN EXPORT/IMPORT DOCKER IMAGE

## Dành cho người muốn share image đã build sẵn (không cần build lại)

---

## 🎁 NGƯỜI GỬI (Export Image)

### Cách 1: Export ra file .tar (Offline)

```bash
# Export image ra file (mất vài phút)
docker save my-spark-worker:latest -o my-spark-worker.tar

# Kích thước file: ~1.9GB
# Upload lên Google Drive/OneDrive để share
```

### Cách 2: Push lên Docker Hub (Online)

```bash
# 1. Login Docker Hub
docker login

# 2. Tag image
docker tag my-spark-worker:latest YOUR_USERNAME/spark-worker:latest

# 3. Push lên Docker Hub
docker push YOUR_USERNAME/spark-worker:latest
```

---

## 📥 NGƯỜI NHẬN (Import Image)

### Nếu nhận file .tar:

```bash
# 1. Download file my-spark-worker.tar

# 2. Load image vào Docker (mất vài phút)
docker load -i my-spark-worker.tar

# 3. Kiểm tra
docker images my-spark-worker

# 4. Chạy ngay (KHÔNG CẦN BUILD!)
docker-compose up -d
```

### Nếu dùng Docker Hub:

```bash
# 1. Pull image từ Docker Hub
docker pull YOUR_USERNAME/spark-worker:latest

# 2. Tag lại cho đúng tên
docker tag YOUR_USERNAME/spark-worker:latest my-spark-worker:latest

# 3. Chạy ngay
docker-compose up -d
```

---

## 📊 SO SÁNH 2 CÁCH

| Tiêu chí | Share Code | Share Image |
|----------|-----------|-------------|
| **Kích thước** | ~50MB | ~1.9GB |
| **Tốc độ người nhận** | ❌ Chậm (phải build 20 phút) | ✅ Nhanh (chỉ load image) |
| **Yêu cầu internet** | ✅ Cần (download packages khi build) | ❌ Không cần (nếu dùng .tar) |
| **Dễ share** | ✅ Dễ (GitHub/Email) | ⚠️ Khó (file lớn) |
| **Phù hợp cho** | Developers, học sinh | End users, demo |

---

## 💡 KHUYẾN NGHỊ

### ✅ **Share Code** nếu:
- Nộp bài tập cho thầy/cô
- Share lên GitHub
- Người nhận có kiến thức Docker
- Muốn người khác hiểu cách build

### ✅ **Share Image** nếu:
- Demo cho khách hàng
- Người nhận không rành Docker
- Cần chạy nhanh, không có thời gian build
- Có cách share file lớn (Google Drive, USB)

---

## 🎯 KHUYẾN NGHỊ TỐT NHẤT

**Share CẢ 2:**
1. Code → GitHub repository
2. Image → Docker Hub hoặc Google Drive

Người dùng có thể chọn:
- Có thời gian → Build từ code (hiểu rõ hơn)
- Không có thời gian → Download image (dùng luôn)

