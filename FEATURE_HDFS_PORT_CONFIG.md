# ✨ TÍNH NĂNG MỚI v4.4.4 - Cấu Hình Cổng HDFS

## 🎯 Tính Năng

Bây giờ bạn có thể **chỉnh cổng HDFS** trực tiếp trong giao diện tab **HDFS Upload**, không cần chỉnh file JSON thủ công nữa! 🎉

---

## 🚀 Cách Sử Dụng (3 Bước)

### Bước 1: Mở Tab HDFS Upload
```
Khởi động app → Click tab "HDFS Upload"
```

### Bước 2: Tìm Phần Configuration
Trong card **"⚙️ Configuration"**, bạn sẽ thấy:

```
Container:       [namenode ▼]
Upload Path:     [/input          ]
HDFS Port:       [8020  ] (Default: 8020)  ← MỚI!
```

### Bước 3: Thay Đổi và Lưu
```
1. Nhập cổng mới (ví dụ: 9000)
2. Click "💾 Save Config"
3. Restart app
4. Done! ✅
```

---

## 📸 Screenshot Mô Phỏng

```
┌─────────────────────────────────────────┐
│ ⚙️ Configuration                        │
├─────────────────────────────────────────┤
│                                          │
│ Container:                               │
│ ┌────────────────────────────┐          │
│ │ namenode                 ▼ │          │
│ └────────────────────────────┘          │
│                                          │
│ Upload Path:                             │
│ ┌────────────────────────────┐          │
│ │ /input                     │          │
│ └────────────────────────────┘          │
│                                          │
│ HDFS Port:                    ← MỚI!    │
│ ┌──────┐                                │
│ │ 8020 │ (Default: 8020)                │
│ └──────┘                                │
│                                          │
│ ☑ Auto-extract compressed files         │
│                                          │
│ ┌─────────────┐ ┌──────────┐           │
│ │ 💾 Save Config│ │ 🔍 Test  │           │
│ └─────────────┘ └──────────┘           │
└─────────────────────────────────────────┘
```

---

## 💡 Ví Dụ Thực Tế

### Ví dụ 1: Đổi cổng từ 8020 → 9000

**Thao tác:**
1. Nhập `9000` vào field "HDFS Port"
2. Click "💾 Save Config"

**Kết quả:**
```
✅ Configuration saved successfully!

Container: namenode
HDFS Host: hdfs://namenode:9000
Upload Path: /input

File: D:\...\spark_runner_config.json
```

**Log hiển thị:**
```
✓ Configuration saved to D:\...\spark_runner_config.json
   • Container: namenode
   • HDFS Host: hdfs://namenode:9000
   • Upload Path: /input
```

---

### Ví dụ 2: Kiểm tra cổng mới

**Sau khi đổi cổng, test connection:**

1. Click **"🔍 Test"**
2. Log sẽ hiển thị:
   ```
   🔍 Testing HDFS connection...
   📦 Container: namenode
   💻 Executing: docker exec namenode hdfs dfs -ls /
   ✅ Connection successful!
   ```

---

## ⚙️ File Config Tự Động Cập Nhật

Khi bạn save, file **`spark_runner_config.json`** sẽ tự động update:

**Trước:**
```json
{
  "hdfs_container": "namenode",
  "hdfs_host": "hdfs://namenode:8020",
  "hdfs_port": "8020"
}
```

**Sau khi đổi → 9000:**
```json
{
  "hdfs_container": "namenode",
  "hdfs_host": "hdfs://namenode:9000",
  "hdfs_port": "9000"
}
```

---

## ⚠️ Lưu Ý Quan Trọng

### 1. Phải Restart App
Sau khi save config, **bắt buộc restart** app để áp dụng thay đổi:
```
Close app → Reopen app
```

### 2. Phải Khớp Với Docker Compose
Nếu đổi cổng, **nhớ check** file `docker-compose.yml`:

**Ví dụ:** Nếu đổi sang cổng 9000, đảm bảo:
```yaml
services:
  namenode:
    ports:
      - "9000:9000"  # Phải khớp!
```

### 3. Test Sau Khi Đổi
Luôn **test connection** sau khi đổi cổng:
```
Click "🔍 Test" → Xem log → Đảm bảo "✅ Connection successful!"
```

---

## 📚 Tài Liệu Chi Tiết

Xem thêm trong **`PORT_CONFIGURATION_GUIDE.md`**:
- Hướng dẫn chi tiết từng bước
- Troubleshooting cho lỗi cổng
- Ví dụ với nhiều cổng khác nhau
- Checklist hoàn chỉnh

---

## 🎉 Lợi Ích

| Trước | Sau |
|-------|-----|
| Phải mở file JSON | Chỉnh trong UI |
| Phải biết cú pháp JSON | Click và nhập số |
| Dễ sai format | Validation tự động |
| Không có feedback | Có thông báo rõ ràng |

---

## 🚀 Kết Luận

**Chỉnh cổng HDFS giờ đây đơn giản như:**
```
Tab HDFS Upload → Nhập cổng → Save → Restart → Done! ✅
```

**Không cần lo về:**
- ❌ Chỉnh file JSON thủ công
- ❌ Sai cú pháp
- ❌ Không biết file ở đâu

**Chỉ cần:**
- ✅ Nhập số cổng
- ✅ Click Save
- ✅ Restart app

**Thật sự đơn giản!** 😊

---

**Version:** v4.4.4  
**Date:** October 13, 2025  
**Feature:** Configurable HDFS Port in UI
