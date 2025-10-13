# 🔧 Hướng Dẫn Cấu Hình Cổng (Port Configuration Guide)

## 📋 Tổng Quan

Spark Runner GUI v4.4.3 cho phép bạn tùy chỉnh cổng (port) cho tất cả các services. Có **2 cách** để cấu hình cổng:

1. **Trong Giao Diện (UI)** - Dễ dàng, trực quan ✅ Khuyến nghị
2. **Chỉnh Sửa File JSON** - Cho người dùng advanced

---

## 🎯 Cách 1: Cấu Hình Trong Giao Diện (KHUYẾN NGHỊ)

### A. Cấu Hình Cổng HDFS (Tab HDFS Upload)

**Bước 1:** Mở ứng dụng
```bash
python main.py
# Hoặc double-click: START.bat
```

**Bước 2:** Chuyển đến tab **"HDFS Upload"**

**Bước 3:** Trong phần **"⚙️ Configuration"**, bạn sẽ thấy:

```
Container:       [namenode ▼]
Upload Path:     [/input          ]
HDFS Port:       [8020  ] (Default: 8020)
```

**Bước 4:** Thay đổi cổng HDFS:
- Ví dụ: Đổi từ `8020` → `9000`
- Hoặc cổng khác tùy ý

**Bước 5:** Click **"💾 Save Config"**

**Kết quả:**
```
✅ Configuration saved successfully!

Container: namenode
HDFS Host: hdfs://namenode:9000
Upload Path: /input
```

**Bước 6:** Restart ứng dụng để áp dụng thay đổi
```bash
# Đóng app → Mở lại
python main.py
```

---

### B. Cấu Hình Cổng Services Khác (Tab Settings)

**Cổng có thể điều chỉnh:**

| Service | Default Port | Mô tả |
|---------|--------------|-------|
| Spark Master UI | 9090 | Web UI của Spark Master |
| Spark Worker UI | 8081 | Web UI của Spark Worker |
| HDFS NameNode UI | 9870 | Web UI của HDFS NameNode |
| HDFS DataNode UI | 9864 | Web UI của HDFS DataNode |
| History Server | 18080 | Spark History Server |
| Jupyter | 8888 | Jupyter Notebook |

**Hướng dẫn:**

1. Chuyển đến tab **"Settings"** (nếu có)
2. Tìm phần **"Ports Configuration"**
3. Nhập cổng mới
4. Click **"Save"**

---

## 🎯 Cách 2: Chỉnh Sửa File JSON (Advanced)

### File: `spark_runner_config.json`

**Vị trí:** `run_spark_gui/spark_runner_config.json`

**Cấu trúc:**
```json
{
  "hdfs_container": "namenode",
  "hdfs_host": "hdfs://namenode:8020",
  "hdfs_port": "8020",
  "hdfs_path": "/input",
  
  "ports": {
    "spark_master_ui": "9090",
    "spark_worker_ui": "8081",
    "hdfs_namenode_ui": "9870",
    "hdfs_datanode_ui": "9864",
    "history_server": "18080",
    "jupyter": "8888"
  }
}
```

---

## 📝 Ví Dụ Thay Đổi Cổng

### Ví dụ 1: Đổi cổng HDFS từ 8020 → 9000

**Trước:**
```json
{
  "hdfs_host": "hdfs://namenode:8020",
  "hdfs_port": "8020"
}
```

**Sau:**
```json
{
  "hdfs_host": "hdfs://namenode:9000",
  "hdfs_port": "9000"
}
```

**Kiểm tra:**
```bash
# Kiểm tra HDFS có hoạt động không
docker exec namenode hdfs dfs -ls /
```

---

### Ví dụ 2: Đổi cổng Spark Master UI từ 9090 → 8080

**Trước:**
```json
{
  "ports": {
    "spark_master_ui": "9090"
  }
}
```

**Sau:**
```json
{
  "ports": {
    "spark_master_ui": "8080"
  }
}
```

**Truy cập:**
- Cũ: `http://localhost:9090`
- Mới: `http://localhost:8080`

---

### Ví dụ 3: Thay đổi nhiều cổng cùng lúc

```json
{
  "hdfs_port": "9000",
  "hdfs_host": "hdfs://namenode:9000",
  
  "ports": {
    "spark_master_ui": "8080",
    "spark_worker_ui": "8082",
    "hdfs_namenode_ui": "9871",
    "jupyter": "9999"
  }
}
```

---

## ⚠️ Lưu Ý Quan Trọng

### 1. **Cổng Phải Khớp Với Docker Compose**

Nếu bạn thay đổi cổng trong `spark_runner_config.json`, **PHẢI** thay đổi tương ứng trong `docker-compose.yml`:

**Ví dụ:** Đổi cổng Spark Master UI từ 9090 → 8080

**File: docker-compose.yml**
```yaml
services:
  spark-master:
    ports:
      - "8080:8080"  # Thay đổi từ 9090:8080
```

**File: spark_runner_config.json**
```json
{
  "ports": {
    "spark_master_ui": "8080"
  }
}
```

### 2. **Tránh Xung Đột Cổng**

Đảm bảo cổng mới **KHÔNG bị chiếm** bởi service khác:

**Kiểm tra cổng đang sử dụng (Windows):**
```powershell
netstat -ano | findstr :8020
```

**Kiểm tra cổng đang sử dụng (Linux/Mac):**
```bash
lsof -i :8020
```

### 3. **Restart Services**

Sau khi thay đổi cổng, **PHẢI restart** containers:

```bash
# Stop containers
docker-compose down

# Start với config mới
docker-compose up -d
```

### 4. **Backup Config**

Trước khi thay đổi, **backup** file config:

```bash
# Windows
copy spark_runner_config.json spark_runner_config.json.backup

# Linux/Mac
cp spark_runner_config.json spark_runner_config.json.backup
```

---

## 🔍 Troubleshooting

### Lỗi: "Connection refused" sau khi đổi cổng

**Nguyên nhân:** Cổng trong config không khớp với Docker Compose

**Giải pháp:**
1. Kiểm tra `docker-compose.yml`:
   ```bash
   docker-compose config
   ```

2. So sánh với `spark_runner_config.json`

3. Đảm bảo cổng **GIỐNG NHAU**

4. Restart containers:
   ```bash
   docker-compose restart
   ```

---

### Lỗi: "Port already in use"

**Nguyên nhân:** Cổng đã bị chiếm bởi service khác

**Giải pháp 1:** Đổi sang cổng khác
```json
{
  "hdfs_port": "9001"  // Thay vì 9000
}
```

**Giải pháp 2:** Stop service đang chiếm cổng
```bash
# Tìm process ID
netstat -ano | findstr :8020

# Kill process (Windows - cần admin)
taskkill /PID <PID> /F
```

---

### Lỗi: "Cannot connect to HDFS"

**Nguyên nhân:** HDFS không lắng nghe trên cổng đã cấu hình

**Giải pháp:**

1. Kiểm tra HDFS config trong container:
   ```bash
   docker exec namenode cat /etc/hadoop/core-site.xml | grep fs.defaultFS
   ```

2. Output mong đợi:
   ```xml
   <value>hdfs://namenode:8020</value>
   ```

3. Nếu khác → Cần thay đổi HDFS config:
   ```bash
   # Vào container
   docker exec -it namenode bash
   
   # Edit core-site.xml
   vi /etc/hadoop/core-site.xml
   
   # Tìm fs.defaultFS và đổi port
   <property>
     <name>fs.defaultFS</name>
     <value>hdfs://namenode:9000</value>
   </property>
   
   # Restart HDFS
   hdfs --daemon stop namenode
   hdfs --daemon start namenode
   ```

---

## ✅ Checklist Sau Khi Đổi Cổng

- [ ] ✅ Đã thay đổi trong `spark_runner_config.json`
- [ ] ✅ Đã thay đổi trong `docker-compose.yml` (nếu cần)
- [ ] ✅ Đã backup config cũ
- [ ] ✅ Đã restart containers (`docker-compose restart`)
- [ ] ✅ Đã restart app (close → reopen)
- [ ] ✅ Đã test connection:
  - Click **"🔍 Test"** trong HDFS Upload tab
  - Hoặc: `docker exec namenode hdfs dfs -ls /`

---

## 📚 Tham Khảo Thêm

| Tài Liệu | Mô Tả |
|----------|-------|
| `QUICKSTART.md` | Hướng dẫn nhanh cho người mới |
| `USER_GUIDE.md` | Hướng dẫn chi tiết từng tab |
| `TROUBLESHOOTING.md` | Khắc phục lỗi thường gặp |
| `docker-compose.yml` | Cấu hình Docker services |

---

## 🎓 Mẹo Hay

### 1. Sử dụng Cổng Chuẩn
Nếu không cần thiết, **nên giữ cổng mặc định**:
- HDFS: `8020`
- Spark Master UI: `9090`
- HDFS NameNode UI: `9870`

### 2. Ghi Chú Thay Đổi
Tạo file `PORT_CHANGES.md` để ghi lại:
```markdown
# Port Changes Log

## 2025-10-13
- Changed HDFS port: 8020 → 9000
- Reason: Port conflict with other service
- Modified files:
  - spark_runner_config.json
  - docker-compose.yml
```

### 3. Test Sau Mỗi Thay Đổi
```bash
# 1. Test HDFS
docker exec namenode hdfs dfs -ls /

# 2. Test Spark Master
curl http://localhost:9090

# 3. Test containers
docker ps
```

---

## 💡 Kết Luận

**Đơn giản nhất:**
1. Mở app → Tab "HDFS Upload"
2. Đổi cổng trong **"HDFS Port"**
3. Click **"💾 Save Config"**
4. Restart app → Done! ✅

**Chúc bạn cấu hình thành công!** 🎉

---

**Version:** v4.4.3  
**Last Updated:** October 13, 2025  
**Author:** Spark Runner GUI Team
