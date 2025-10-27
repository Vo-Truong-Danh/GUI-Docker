# 📚 HƯỚNG DẪN SỬ DỤNG - Spark Runner GUI

## 🎯 YÊU CẦU HỆ THỐNG

- **Docker Desktop** đã cài đặt và đang chạy
- **Windows 10/11** hoặc Linux/MacOS
- **RAM:** Tối thiểu 8GB (khuyến nghị 16GB)
- **Disk:** Ít nhất 10GB trống

---

## 🚀 CÁCH CÀI ĐẶT

### Bước 1: Clone hoặc copy project này

```bash
cd D:\BaiTapSinhVien\TH BigData\
# (Folder GUI-Docker đã có sẵn)
```

### Bước 2: Build Docker image (LẦN ĐẦU - mất 15-20 phút)

```bash
cd GUI-Docker

# Build Spark Worker image với Python packages
docker-compose build spark-worker
```

**⏳ Lưu ý:** Build lần đầu sẽ mất thời gian vì phải:
- Download base image Alpine Linux
- Cài đặt build tools
- Compile và cài các Python packages (pandas, numpy, etc.)

### Bước 3: Khởi động cluster

```bash
docker-compose up -d
```

Chờ 10-20 giây để các services khởi động.

### Bước 4: Kiểm tra trạng thái

```bash
docker-compose ps
```

Tất cả containers phải ở trạng thái **Up**.

---

## 🌐 TRUY CẬP CÁC SERVICES

| Service | URL | Mô tả |
|---------|-----|-------|
| Spark Master UI | http://localhost:8080 | Quản lý Spark cluster |
| HDFS NameNode | http://localhost:9870 | Quản lý HDFS |
| HDFS DataNode | http://localhost:9864 | Xem DataNode status |
| Spark App UI | http://localhost:4040 | UI khi có job đang chạy |

---

## 🖥️ CHẠY GUI APPLICATION

### Windows:
```bash
cd run_spark_gui
python main.py
```

### Hoặc chạy file .exe (nếu đã build):
```bash
cd dist
.\SparkRunnerGUI.exe
```

---

## 📦 PACKAGES ĐÃ CÀI SẴN TRONG WORKER

Các packages sau đã được cài sẵn trong Spark Worker containers:

- ✅ **pandas 1.3.5** - DataFrame processing
- ✅ **numpy 1.21.6** - Numerical computing
- ✅ **PyYAML 5.3.1** - YAML config files
- ✅ **requests 2.28.2** - HTTP requests
- ✅ **python-dotenv 0.21.1** - Environment variables

Bạn có thể dùng các packages này trong PySpark jobs mà không cần cài thêm!

---

## 🛠️ CÁC LỆNH HỮU ÍCH

### Xem logs
```bash
# Logs của tất cả services
docker-compose logs -f

# Logs của Spark Worker
docker logs gui-docker-spark-worker-1 -f
```

### Restart services
```bash
docker-compose restart
```

### Stop tất cả
```bash
docker-compose down
```

### Scale workers (thêm workers)
```bash
docker-compose up -d --scale spark-worker=3
```

### Vào container để debug
```bash
docker exec -it gui-docker-spark-worker-1 sh
```

---

## ✅ TEST NHANH

Chạy lệnh sau để kiểm tra packages:

```bash
docker exec gui-docker-spark-worker-1 python3 -c "
import pandas as pd
import numpy as np
print('✅ pandas:', pd.__version__)
print('✅ numpy:', np.__version__)
"
```

---

## 🆘 TROUBLESHOOTING

### Lỗi: "Cannot connect to Docker daemon"
→ Mở Docker Desktop và đợi nó khởi động xong

### Lỗi: "Port already in use"
→ Đổi port trong `docker-compose.yml` hoặc kill process đang dùng port

### Lỗi build: "no such host"
→ Kiểm tra kết nối internet, Docker cần download packages

### Container không start
→ Chạy `docker-compose down` rồi `docker-compose up -d` lại

---

## 📝 LƯU Ý

1. **Build CHỈ CẦN LÀM 1 LẦN** - Các lần sau chỉ cần `docker-compose up -d`
2. **Packages nằm trong image** - Không mất khi restart container
3. **Muốn thêm packages** - Sửa `requirements-docker.txt` rồi build lại

---

## 👨‍💻 LIÊN HỆ & HỖ TRỢ

Nếu gặp vấn đề, tạo issue trên GitHub hoặc liên hệ qua email.

**Chúc bạn học tập tốt với Big Data! 🎓**

