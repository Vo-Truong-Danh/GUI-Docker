# 🎯 UNIFIED DASHBOARD - HƯỚNG DẪN ĐẦY ĐỦ

## 📌 TÓM TẮT

Đã **gộp 2 dashboard** thành **1 file duy nhất** với bố trí hợp lý:
- ✅ **Dashboard Tổng quan** - Metrics chính
- ✅ **Phân tích Khách hàng** - Segmentation
- ✅ **Phân loại Sản phẩm** - Categories
- ✅ **Kết quả ML** - Model performance
- ✅ **Xu hướng & Phân tích** - Top performers
- ✅ **Dữ liệu Khoa học** - All metrics table

---

## 🚀 CÁCH CHẠY NGAY LẬP TỨC

### **Option 1: Chạy GUI (RECOMMEND)**

```bash
cd "d:\BaiTapSinhVien\TH BigData\GUI-Docker\run_spark_gui"
python main.py
```

Trong GUI:
1. Đi tới tab **📊 Dashboard**
2. Click **🚀 Khởi Động Server**
3. Click **🌐 Mở Dashboard**
4. **Unified Dashboard** mở tự động ✅

### **Option 2: Chạy HTTP Server trực tiếp**

```bash
cd "d:\BaiTapSinhVien\TH BigData\GUI-Docker"
python -m http.server 8000
```

Rồi mở trình duyệt:
```
http://localhost:8000/unified_dashboard.html
```

---

## 📁 CẤU TRÚC FILE

```
GUI-Docker/
├── unified_dashboard.html ✅ NEW - File dashboard hợp nhất
├── tmp/
│   ├── ml_analysis_summary.json ✅
│   ├── ml_result_1_customer_clustering.png ✅
│   ├── ml_result_2_regression_analysis.png ✅
│   ├── ml_result_3_product_clustering.png ✅
│   ├── ml_result_4_comprehensive_dashboard.png ✅
│   ├── ml_result_5_advanced_analytics.png ✅
│   └── ml_result_6_trends_comparison.png ✅
├── run_spark_gui/
│   ├── dashboard_tab.py ✅ (UPDATED - mở unified_dashboard.html)
│   └── main.py
├── index2_1.html (cũ - giữ lại cho reference)
├── dashboard_analytics.html (cũ - giữ lại cho reference)
└── ...
```

---

## ✨ FEATURES CỦA UNIFIED DASHBOARD

### **1️⃣ Sidebar Navigation (Trái)**
```
📊 Dashboard Tổng quan
👥 Phân tích Khách hàng
📦 Phân loại Sản phẩm
🤖 Kết quả ML
📈 Xu hướng & Phân tích
🔬 Dữ liệu Khoa học
```

### **2️⃣ Dashboard Tổng quan**
- 💰 Tổng doanh thu
- 📊 Tổng giao dịch
- 📈 Giá trị trung bình
- 🤖 Best Model R² Score
- 📋 Bảng thông tin chung

### **3️⃣ Phân tích Khách hàng**
- 🎯 Phân loại: VIP, Regular, Occasional
- 📊 Ảnh phân cụm K-Means

### **4️⃣ Phân loại Sản phẩm**
- 🏷️ Danh mục sản phẩm
- 📦 Ảnh Bisecting K-Means clustering

### **5️⃣ Kết quả ML**
- 🤖 So sánh: Linear Regression vs Random Forest
- 📊 Ảnh regression analysis
- 📈 Dashboard tổng hợp

### **6️⃣ Xu hướng & Phân tích**
- 🔝 Top revenue country
- ⭐ Top product
- 📊 Ảnh advanced analytics
- 📈 Ảnh trends comparison

### **7️⃣ Dữ liệu Khoa học**
- 📋 Bảng 14 chỉ số chi tiết
- Toàn bộ metrics trong 1 bảng

---

## 🖼️ HÌNH ÁNH (Placeholder vs Real)

### **Placeholder Images** (Test ngay)
```
✅ Tất cả 6 ảnh đã tạo
✅ Màu sắc: Blue, Teal, Green, Gold, Red, Purple
✅ Hiển thị "Placeholder - Run code7.py for real data"
```

### **Real Images** (Chạy code7.py)
```bash
cd run_spark_gui
python code7.py
```

Khi chạy code7.py:
- ✅ Tạo 6 ảnh ML thực tế
- ✅ Tạo file JSON với dữ liệu thực
- ✅ Dashboard tự load dữ liệu mới

---

## 📊 JSON DATA STRUCTURE

```json
{
  "total_revenue": 9468513.50,
  "total_transactions": 500570,
  "avg_order_value": 18.91,
  "num_customers": 4373,
  "num_products": 4070,
  "best_model_r2": 0.8956,
  "best_model": "Random Forest",
  "prediction_rmse": 12.45,
  "customer_segments": {
    "VIP": { "count": 315, "percentage": 7.2 },
    "Regular": { "count": 2148, "percentage": 49.1 },
    "Occasional": { "count": 1910, "percentage": 43.7 }
  },
  "product_categories": { ... },
  "top_revenue_country": "Netherlands",
  "top_product": "PAPER CRAFT",
  ...
}
```

---

## 🎨 RESPONSIVE DESIGN

- ✅ **Desktop**: Full sidebar + main content
- ✅ **Tablet**: Sidebar ẩn, menu toggle button
- ✅ **Mobile**: Full responsive, hamburger menu

**Test trên mobile:**
```
http://localhost:8000/unified_dashboard.html
```
Click icon ☰ để toggle sidebar.

---

## 🔄 AUTO-LOAD DATA

Dashboard tự động:
1. Tải JSON từ `tmp/ml_analysis_summary.json`
2. Nếu lỗi → Retry 5 lần, delay 2 giây
3. Nếu vẫn lỗi → Hiển thị error message

**Logs console:**
```javascript
[INFO] Đang tải dữ liệu từ: tmp/ml_analysis_summary.json
[SUCCESS] Dữ liệu tải thành công
[RETRY] Lần 1/5...
[ERROR] Không thể tải dữ liệu
```

---

## ✅ CHECKLIST

- [x] Gộp `index2_1.html` + `dashboard_analytics.html`
- [x] Tạo `unified_dashboard.html` (950+ lines)
- [x] Sidebar navigation 6 pages
- [x] Stat cards + tables
- [x] 6 images grid
- [x] JSON auto-load + retry
- [x] Placeholder images (ready to use)
- [x] Update `dashboard_tab.py` (mở unified file)
- [x] Responsive design
- [x] Error handling

---

## 📈 IMPROVEMENTS

**Trước (2 file):**
```
❌ Phải mở 2 tab riêng
❌ Khó quản lý code
❌ Trùng lặp HTML/CSS
❌ Navigation phức tạp
```

**Sau (1 file):**
```
✅ 1 file duy nhất
✅ Sidebar navigation đẹp
✅ Code modular (6 hàm render)
✅ DRY principle - không trùng lặp
✅ 950 lines - well-organized
```

---

## 🚨 TROUBLESHOOTING

| Vấn đề | Nguyên nhân | Giải pháp |
|--------|-----------|----------|
| ❌ Ảnh hiển thị placeholder | Chưa chạy code7.py | `python code7.py` tạo ảnh thực |
| ❌ JSON không load | Server chưa chạy | Click "Khởi Động Server" |
| ❌ Port 8000 bận | Process khác dùng port | Thay port: `python -m http.server 8001` |
| ❌ Dashboard không mở | Browser blocked | Check firewall, try `webbrowser.open()` |
| ❌ Sidebar lẫn | Mobile view | Click ☰ để toggle, click link để đóng |

---

## 🎯 NEXT STEPS

1. **Chạy GUI:**
   ```bash
   cd run_spark_gui && python main.py
   ```

2. **Start Server:**
   - Click "🚀 Khởi Động Server"
   - Click "🌐 Mở Dashboard"

3. **Explore Dashboard:**
   - Xem 6 trang khác nhau
   - Click các links trong sidebar
   - Scroll xem ảnh

4. **Generate Real Data (Optional):**
   ```bash
   python code7.py
   ```
   - Ảnh sẽ update
   - Data sẽ refresh

---

## 📋 FILES MODIFIED

- ✅ `unified_dashboard.html` - NEW (950 lines)
- ✅ `dashboard_tab.py` - UPDATED (3 changes: URL, info text, log)
- ✅ `tmp/ml_analysis_summary.json` - EXISTS
- ✅ `tmp/*.png` - 6 placeholder images

---

## 💡 TIPS

**Mở DevTools:**
- F12 hoặc Right-click → Inspect
- Console tab: xem logs
- Network tab: xem requests

**JSON test:**
```bash
curl http://localhost:8000/tmp/ml_analysis_summary.json
```

**Image test:**
```bash
curl http://localhost:8000/tmp/ml_result_1_customer_clustering.png
```

---

**Status:** ✅ READY FOR PRODUCTION  
**Last Updated:** 25/10/2025  
**Version:** 1.0 - Unified
