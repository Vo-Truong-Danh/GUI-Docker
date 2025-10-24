# 🚀 HƯỚNG DẪN CHẠY DASHBOARD BẰNG LOCAL SERVER

## ⚠️ VẤN ĐỀ CẦN GIẢI QUYẾT

Browser không cho phép truy cập file JSON local trực tiếp do **CORS policy** (Cross-Origin Resource Sharing).

**Lỗi:**
```
Access to fetch at 'file:///D:/tmp/ml_analysis_summary.json' from origin 'null' has been blocked by CORS policy
```

## ✅ GIẢI PHÁP

Cần chạy dashboard thông qua **Local HTTP Server** thay vì mở file trực tiếp.

---

## 📋 CÁC BƯỚC THỰC HIỆN

### Bước 1: Chạy Python Server

```bash
cd D:\BaiTapSinhVien\TH BigData\GUI-Docker
python simple_server.py
```

**Output:**
```
╔════════════════════════════════════════════════════════════╗
║           DASHBOARD LOCAL SERVER STARTED                   ║
╚════════════════════════════════════════════════════════════╝

📍 Server Address: http://localhost:8000
📁 Serving from:   D:\BaiTapSinhVien\TH BigData\GUI-Docker

🌐 Dashboard URL:  http://localhost:8000/index2_1.html

✅ Server is running... (Press Ctrl+C to stop)
```

### Bước 2: Mở Dashboard

Server sẽ tự động mở trình duyệt.  
Nếu không, mở thủ công: **http://localhost:8000/index2_1.html**

### Bước 3: Chạy Spark Job

- Vào **GUI Application** → **Spark Runner Tab**
- Nhấn **"Run Spark Job"**
- Đợi kết thúc (sẽ tạo 6 PNG + 1 JSON file)

### Bước 4: Chạy ML Analytics

- Vào **ML Analytics Tab**
- Nhấn **"Run Analysis"** hoặc **"Extract Results"**
- Chờ copy files từ Docker về máy (vào thư mục `tmp/`)

### Bước 5: Refresh Dashboard

- Quay lại Dashboard trên trình duyệt
- Nhấn **F5** để refresh
- Dữ liệu sẽ tự động load!

---

## 📊 DASHBOARD CÓ CÁC TAB:

1. **Giới thiệu** - Mô tả đề tài
2. **Dashboard Tổng quan** - Stat cards + biểu đồ tổng hợp
3. **📊 Dữ liệu Khoa học** ✨ **MỚI** - Hiển thị tất cả 21+ chỉ số chi tiết:
   - 💰 Tổng Doanh Thu
   - 📊 Tổng Giao Dịch
   - 📈 Giá Trị TB/Đơn
   - 🌍 Số Quốc Gia
   - 👥 Phân Khúc Khách Hàng (VIP/Regular/Occasional)
   - 🔵 Linear Regression (R², RMSE)
   - 🟢 Random Forest (R², RMSE)
   - 🏆 Best Model
   - 🥇 Top Quốc Gia
   - 🏷️  Top Sản Phẩm
   - 📅 Ngày Phân Tích
   - ✅ Trạng Thái
4. **Quy trình Xử lý** - 4 bước ETL
5. **Phân cụm Khách hàng** - Biểu đồ K-Means
6. **Dự đoán Doanh thu** - Biểu đồ Regression
7. **Phân loại Sản phẩm** - Biểu đồ Bisecting K-Means
8. **Phân tích Nâng cao** - Heatmaps & Feature Importance

---

## 🛑 DỪNG SERVER

Bấm **Ctrl + C** trong terminal

```
✋ Server stopped by user
Thank you for using Dashboard Server!
```

---

## 💡 TIPS

- **Browser tự động mở:** Khi chạy `simple_server.py`, dashboard sẽ mở tự động
- **Port 8000 bận?** Sửa `PORT = 8000` thành port khác (e.g., 8001)
- **Refresh lại dữ liệu:** F5 hoặc Ctrl+R
- **Xem console log:** F12 → Console tab (có [SUCCESS]/[ERROR] messages)

---

## 📁 FILE STRUCTURE

```
D:\BaiTapSinhVien\TH BigData\GUI-Docker\
├── simple_server.py          ← Server này
├── index2_1.html             ← Dashboard (được update)
├── tmp/
│   ├── ml_analysis_summary.json      (JSON data)
│   ├── ml_result_1_customer_clustering.png
│   ├── ml_result_2_regression_analysis.png
│   ├── ml_result_3_product_clustering.png
│   ├── ml_result_4_comprehensive_dashboard.png
│   ├── ml_result_5_advanced_analytics.png
│   └── ml_result_6_trends_comparison.png
└── docker_results_extractor.py  ← Copy files từ Docker
```

---

## 🎯 WORKFLOW HOÀN CHỈNH

```
1. Chạy simple_server.py
         ↓
2. Dashboard mở tự động (http://localhost:8000/index2_1.html)
         ↓
3. Chạy Spark Job (tạo PNG + JSON)
         ↓
4. Chạy ML Analytics (copy files)
         ↓
5. Refresh Dashboard → Xem dữ liệu thực tế
```

---

**Vậy là xong! 🎉 Dashboard sẽ hoạt động hoàn hảo.**
