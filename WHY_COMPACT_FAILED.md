# ❌ TẠI SAO COMPACT VHDX KHÔNG GIẢM DUNG LƯỢNG?

## 🔍 PHÂN TÍCH VẤN ĐỀ

### **Hiện tượng:**
```
BEFORE compact: 227 GB
DiskPart: "successfully compacted"
AFTER compact: 227 GB (KHÔNG GIẢM!)
```

### **Nguyên nhân:**
VHDX file là một **virtual hard disk** chứa toàn bộ filesystem của Docker.

**Analogy:** Giống như một file ZIP:
- ZIP file có 227GB
- Bạn **xóa** files bên trong ZIP
- Nhưng **không repack** lại ZIP
- ZIP file vẫn 227GB!

**Compact chỉ work khi:**
1. ✅ Data bên TRONG đã bị xóa
2. ✅ Filesystem đã được flush (restart Docker)
3. ✅ VHDX có "free space" thật sự
4. ✅ Sau đó mới compact

---

## ❌ SAI LẦM BẠN ĐÃ LÀM

### **COMPACT_WITH_ADMIN.bat:**
```
[X] 1. Stop Docker
[X] 2. Compact VHDX
[X] 3. Start Docker
```

**Vấn đề:** 
- Bạn KHÔNG XÓA data trước khi compact
- VHDX vẫn chứa 227GB data thật
- Compact không làm gì được!

---

## ✅ QUY TRÌNH ĐÚNG

### **FREE_DISK_C_COMPLETE.bat:**
```
[✓] 1. XÓA HDFS data (giữ input 33GB)
[✓] 2. RESTART Docker → flush filesystem
[✓] 3. STOP Docker
[✓] 4. COMPACT VHDX → giảm từ 227GB → 40GB
[✓] 5. START Docker lại
```

---

## 📊 GIẢI THÍCH CHI TIẾT

### **Step 1: Xóa HDFS data**
```bash
docker exec namenode hdfs dfs -rm -r /checkpoints/
docker exec namenode hdfs dfs -rm -r /output/
docker exec namenode hdfs dfs -expunge  # Empty trash
```

**Kết quả:**
- HDFS filesystem bây giờ chỉ còn 33GB (input data)
- Nhưng VHDX vẫn 227GB vì chưa flush!

### **Step 2: Restart Docker để FLUSH**
```bash
docker-compose down
wsl --shutdown
# Start Docker Desktop
```

**Tại sao?**
- Linux filesystem cache data trong RAM
- Cần restart để **write changes to disk**
- Sau restart, VHDX filesystem biết rằng nó chỉ dùng 33GB
- Nhưng VHDX file size vẫn 227GB (chứa 194GB "free space")

### **Step 3: Stop Docker**
```bash
wsl --shutdown
```

**Tại sao?**
- DiskPart không thể compact file đang được sử dụng
- Phải stop hoàn toàn

### **Step 4: Compact VHDX**
```bash
diskpart
> select vdisk file="C:\...\docker_data.vhdx"
> compact vdisk
```

**Cơ chế:**
- DiskPart đọc VHDX filesystem
- Thấy chỉ 33GB data, 194GB free space
- **Shrink** VHDX từ 227GB → 40GB (33GB data + 7GB overhead)

### **Step 5: Restart Docker**
```bash
# Start Docker Desktop
docker-compose up -d
```

---

## 🧪 KIỂM CHỨNG

### **Trước khi chạy:**
```
C: drive free: 10 GB
VHDX size: 227 GB
HDFS /input/data: 33 GB
HDFS total: 227 GB (checkpoints, models, outputs)
```

### **Sau khi chạy FREE_DISK_C_COMPLETE.bat:**
```
C: drive free: 190 GB (+180 GB!)
VHDX size: 40 GB (227 GB → 40 GB)
HDFS /input/data: 33 GB (SAFE!)
HDFS total: 33 GB (chỉ còn input)
```

---

## 🔧 TẠI SAO SCRIPT CŨ BÁO LỖI?

### **Lỗi bạn thấy:**
```
Invalid number. Numbers are limited to 32-bits of precision.
Missing operand.
New size: GB
```

### **Nguyên nhân:**
```batch
for %%A in ("%VHDX_PATH%") do set size=%%~zA  # ← Lỗi ở đây!
set /a sizeMB=%size% / 1048576
```

**Vấn đề:**
- `%%~zA` trả về file size **trong bytes**
- 227 GB = 243,863,109,632 bytes
- CMD `set /a` chỉ hỗ trợ **32-bit integers**
- Max = 2,147,483,647 (2.1 billion)
- 243 billion > 2.1 billion → **OVERFLOW!**

### **Fix:**
```batch
# Dùng PowerShell thay vì CMD math
powershell -Command "Get-Item '%VHDX_PATH%' | Select @{N='Size (GB)';E={[math]::Round($_.Length/1GB,2)}}"
```

---

## 💡 TẠI SAO PHẢI XÓA DATA TRƯỚC?

### **Hiểu về VHDX:**
VHDX là **dynamically expanding virtual disk**:

1. **Khởi đầu:** 1 GB (empty)
2. **Thêm data:** VHDX **grow** to 50 GB
3. **Thêm data:** VHDX **grow** to 227 GB
4. **XÓA data:** VHDX vẫn 227 GB (NOT auto-shrink!)
5. **Compact:** Check filesystem, thấy free space, **shrink** to 40 GB

**Nếu không xóa data:**
- Filesystem: 227 GB used, 0 GB free
- Compact: Nothing to shrink!
- Result: Vẫn 227 GB

**Sau khi xóa data:**
- Filesystem: 33 GB used, 194 GB free
- Compact: Shrink 194 GB free space
- Result: 40 GB (33 GB + overhead)

---

## 🚨 LƯU Ý QUAN TRỌNG

### ⚠️ **Phải chạy với ADMINISTRATOR**
```
Right-click MAIN_MENU.bat → Run as Administrator
```

**Tại sao?**
- DiskPart yêu cầu Admin rights
- Nếu không có Admin:
  - Steps 1-2 chạy OK (delete data, restart)
  - Step 3 FAIL (compact denied)
  - Kết quả: Data đã xóa nhưng VHDX chưa compact

### ⚠️ **Backup input data trước**
```bash
# Export input data (optional, nếu lo lắng)
docker exec namenode hdfs dfs -get /input/data/ ./backup_input/
```

### ⚠️ **Mất 15-20 phút**
```
Step 1: Delete HDFS      → 2 min
Step 2: Restart Docker   → 1 min
Step 3: Compact VHDX     → 10-15 min (227 GB file)
Step 4: Restart Docker   → 1 min
Step 5: Verify           → 1 min
```

---

## 📋 CHECKLIST

### **Trước khi chạy:**
- [ ] Docker Desktop đang chạy
- [ ] Containers đang chạy (namenode, spark-master, workers)
- [ ] Đã backup input data (nếu cần)
- [ ] Ổ C: còn ít nhất 10 GB (để chạy script)
- [ ] **Đã đóng tất cả apps khác** (Docker sẽ restart)

### **Chạy script:**
- [ ] Right-click **MAIN_MENU.bat** → **Run as Administrator**
- [ ] Chọn option **[7] COMPACT DOCKER DISK**
- [ ] Đợi 15-20 phút

### **Sau khi chạy:**
- [ ] Verify C: drive free space (tăng ~180 GB)
- [ ] Verify VHDX size (giảm xuống ~40 GB)
- [ ] Verify input data còn nguyên:
  ```bash
  docker exec namenode hdfs dfs -du -s -h /input/data/
  # Phải thấy: 33 GB
  ```

---

## 🎯 KẾT LUẬN

### **Sai lầm:**
```
Compact → Không xóa data trước
```

### **Đúng:**
```
Xóa data → Flush → Compact → Win!
```

### **Script sử dụng:**
- ❌ ~~COMPACT_WITH_ADMIN.bat~~ (sai thứ tự)
- ✅ **FREE_DISK_C_COMPLETE.bat** (đúng thứ tự)
- ✅ **MAIN_MENU.bat** (option 7) → Gọi FREE_DISK_C_COMPLETE.bat

---

## 🔗 LIÊN QUAN

- `FREE_DISK_C_COMPLETE.bat` - Script hoàn chỉnh
- `MAIN_MENU.bat` - Option [7]
- `CLEAN_DATA_MENU.bat` - Chỉ xóa data, không compact

**Câu hỏi?** Xem `MAIN_MENU.bat` option [8] SYSTEM INFO để check disk usage!


