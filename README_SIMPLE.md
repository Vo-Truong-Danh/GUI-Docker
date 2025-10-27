# 🚀 HƯỚNG DẪN NHANH - Spark Runner GUI

## ✨ CÁCH DÙNG ĐƠN GIẢN NHẤT

### 🎬 Lần đầu tiên (Setup):

```bash
# 1. Build Docker image (20 phút - CHỈ LÀM 1 LẦN)
docker-compose build spark-worker
```

### 🎮 Hàng ngày (Sử dụng):

**Cách 1: Dùng file .bat (Đơn giản nhất)**

```
1. Double-click: START_ALL.bat
   → Tự động start Docker + mở GUI

2. Khi xong việc, double-click: STOP_ALL.bat
   → Dừng tất cả containers
```

**Cách 2: Thủ công (Hiểu rõ hơn)**

```bash
# Terminal 1: Start Docker
docker-compose up -d

# Terminal 2: Mở GUI
cd run_spark_gui
python main.py
```

---

## ❓ CÂU HỎI THƯỜNG GẶP

### ❌ Chạy main.py có tự build Docker không?
**KHÔNG!** main.py chỉ là GUI, cần Docker chạy sẵn.

### 🔄 Luồng hoạt động:
```
1. Build Docker (1 lần) → docker-compose build
2. Start Docker        → docker-compose up -d
3. Mở GUI              → python main.py
```

### 📦 Packages ở đâu?
Trong **Docker image** (`my-spark-worker:latest`), không phải máy bạn.

### 💾 Có cần cài lại packages không?
**KHÔNG!** Đã có sẵn trong image, dùng mãi mãi.

---

## 🎯 TÓM TẮT

| Thao tác | Tần suất | Lệnh |
|----------|----------|------|
| **Build image** | 1 lần duy nhất | `docker-compose build` |
| **Start cluster** | Mỗi lần dùng | `START_ALL.bat` hoặc `docker-compose up -d` |
| **Mở GUI** | Mỗi lần dùng | `python run_spark_gui/main.py` |
| **Stop cluster** | Khi xong việc | `STOP_ALL.bat` hoặc `docker-compose down` |

---

## 🌐 Links quan trọng

- Spark Master: http://localhost:8080
- HDFS NameNode: http://localhost:9870

---

**Chúc học tốt! 🎓**

