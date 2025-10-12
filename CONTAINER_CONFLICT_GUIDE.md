# 🐳 Container Name Conflict - Hướng Dẫn Giải Quyết

## 📋 Tổng Quan

Khi bạn đổi từ file `docker-compose.yml` này sang file khác, có thể gặp lỗi:
```
Error: The container name "/namenode" is already in use
```

### ❓ Tại Sao Xảy Ra?

Docker không cho phép 2 container cùng tên tồn tại đồng thời. Khi bạn:
1. Start containers từ file `D:/Downloads/docker-compose.yml`
2. Stop containers (chỉ dừng, KHÔNG xóa)
3. Đổi sang file khác và start lại
4. ❌ Conflict xảy ra vì container cũ vẫn còn (trạng thái stopped)

---

## 🚀 Giải Pháp Tự Động (v4.2.0+)

Ứng dụng giờ đây **TỰ ĐỘNG XỬ LÝ 100%** - Không cần xác nhận!

### ⚡ Flow Tự Động:

```
1. Start Docker
   ↓
2. Phát hiện conflict → "already in use" in stderr
   ↓
3. Log warning: "⚠️ Detected container name conflict"
   ↓
4. Auto-run: docker-compose down
   ↓
5. Log success: "✅ Old containers removed"
   ↓
6. Auto-retry: docker-compose up -d
   ↓
7. ✅ Success!
```

**Bạn chỉ cần click "Start Docker" và chờ - App lo tất cả!** 🎉

---

## 🔍 Log Messages Mới

### Khi Phát Hiện Conflict:
```log
[22:13:30] 🐳 Starting Docker containers...
[22:13:30] 📄 Using: docker-compose.yml
[22:13:30] 💻 $ docker-compose -f D:/Downloads/docker-compose.yml up -d
[22:13:30] ⚠️ Detected container name conflict
[22:13:30] 💡 Tip: Containers with same names already exist
```

### Nếu Chọn YES (Auto-clean):
```log
[22:13:35] 🧹 Removing old containers...
[22:13:35] 💻 $ docker-compose -f D:/Downloads/docker-compose.yml down
[22:13:38] ✅ Old containers removed
[22:13:38] 🔄 Starting new containers...
[22:13:38] 💻 $ docker-compose -f D:/Downloads/docker-compose.yml up -d
[22:13:42] ✅ Docker containers started successfully
```

### Nếu Chọn NO:
```log
[22:13:35] ℹ️ Keeping old containers
[22:13:35] 💡 You can manually remove them using "Clean Docker" button
```

---

## 🛠️ Giải Pháp Thủ Công

Nếu bạn muốn xử lý thủ công:

### Option 1: Dùng Button "Clean Docker"
1. Nhấn nút **"🧹 Clean Docker"** trong tab Spark Runner
2. Xác nhận dialog
3. Nhấn **"▶️ Start Docker"** lại

### Option 2: Dùng Docker CLI
```powershell
# Xem tất cả containers (kể cả stopped)
docker ps -a

# Xóa container cụ thể
docker rm namenode spark-master

# Hoặc xóa tất cả stopped containers
docker container prune -f
```

### Option 3: Dùng Docker Desktop
1. Mở **Docker Desktop**
2. Tab **Containers**
3. Tìm container bị conflict
4. Click ⋮ → **Delete**

---

## 💡 Best Practices

### 1️⃣ Luôn Clean Trước Khi Đổi File
Workflow tốt nhất:
```
Stop Docker → Clean Docker → Đổi file → Start Docker
```

### 2️⃣ Đặt Tên Container Unique
Trong `docker-compose.yml`, thêm prefix:
```yaml
services:
  spark-master:
    container_name: project1_spark-master  # ✅ Unique
  
  namenode:
    container_name: project1_namenode      # ✅ Unique
```

### 3️⃣ Sử Dụng Project Name
Chạy với project name khác nhau:
```powershell
# File 1
docker-compose -p project1 up -d

# File 2
docker-compose -p project2 up -d
```

### 4️⃣ Kiểm Tra Trước Khi Start
```powershell
# Xem containers đang chạy
docker ps

# Xem tất cả containers
docker ps -a
```

---

## 🔧 Technical Details

### Phát Hiện Conflict
```python
# Check stderr for conflict pattern
if returncode != 0 and stderr and 'already in use' in stderr:
    # Trigger conflict handler
```

### Auto-cleanup Process
```python
1. Detect: "already in use" in stderr
2. Show: messagebox.askyesnocancel()
3. Clean: docker-compose down
4. Retry: docker-compose up -d
```

### Thread Safety
- Dialog hiển thị trong main thread: `root.after(0, handler)`
- Docker commands chạy trong thread pool
- Status updates thread-safe

---

## 📊 Troubleshooting

### Vấn Đề: Clean thất bại
```log
❌ Failed to remove old containers
Error: Cannot kill container: permission denied
```
**Giải pháp:**
- Chạy Docker Desktop as Administrator
- Hoặc dùng: `docker rm -f container_name`

### Vấn Đề: Conflict vẫn xảy ra sau clean
```log
Error: The container name "/namenode" is already in use
```
**Nguyên nhân:** Container từ compose file khác
**Giải pháp:**
```powershell
# List tất cả containers
docker ps -a | findstr namenode

# Force remove
docker rm -f namenode
```

### Vấn Đề: Network conflict
```log
Error: network with name mynetwork already exists
```
**Giải pháp:**
```powershell
# Remove network
docker network rm mynetwork

# Hoặc clean all
docker network prune -f
```

---

## 📖 Quick Reference

| Tình Huống | Giải Pháp | Command |
|------------|-----------|---------|
| Container name conflict | Auto-clean | Click YES trong dialog |
| Manual cleanup | Clean Docker button | UI: 🧹 Clean Docker |
| Check containers | Docker CLI | `docker ps -a` |
| Remove specific | Docker CLI | `docker rm container_name` |
| Remove all stopped | Docker CLI | `docker container prune -f` |
| Force remove running | Docker CLI | `docker rm -f container_name` |
| Network conflict | Docker CLI | `docker network prune -f` |
| Volume conflict | Docker CLI | `docker volume prune -f` |

---

## 🎯 Kết Luận

**Bây giờ bạn có thể:**
- ✅ Đổi file docker-compose.yml thoải mái
- ✅ Ứng dụng tự động phát hiện conflict
- ✅ Chọn xóa cũ hoặc giữ lại
- ✅ Retry tự động sau khi clean
- ✅ Log rõ ràng từng bước

**Không còn lo lắng về container name conflict!** 🎉

---

*Last Updated: October 12, 2025*  
*Version: 4.2.0*
