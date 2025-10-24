# 📊 Dashboard Auto-Load Guide - index2_1.html

## 🎯 Mục đích
Dashboard `index2_1.html` được cập nhật để **tự động tải dữ liệu thực từ Spark Analysis** và hiển thị biểu đồ phân tích.

---

## 🔄 Luồng Dữ Liệu (Data Flow)

```
┌─────────────────────────────────────────────────────────────────┐
│                    SPARK ANALYSIS EXECUTION                     │
│  (Chạy trong Docker Container - /tmp/)                         │
└────────────────────┬────────────────────────────────────────────┘
                     │ Outputs:
                     ├─ /tmp/ml_analysis_summary.json (JSON data)
                     └─ /tmp/ml_analysis_results.png (Chart image)
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│            DOCKER RESULTS EXTRACTOR                             │
│  (copy_docker_results_to_tmp)                                   │
│  docker cp container:/tmp/ → host /tmp/                         │
└────────────────────┬────────────────────────────────────────────┘
                     │ Result: Files available on host
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│            BROWSER LOADS DASHBOARD                              │
│  (index2_1.html)                                                │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ├─ fetch('/tmp/ml_analysis_summary.json')
                     └─ display /tmp/ml_analysis_results.png
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│            STAT CARDS & CHARTS POPULATED                        │
│  ✓ Total Revenue  ✓ Avg Order Value  ✓ Best Model R²           │
│  ✓ Charts in all 7 pages                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📝 Cập Nhật Chi Tiết

### 1️⃣ Auto-Load JavaScript (Dòng ~400)
```javascript
// Configuration - Load từ /tmp/
const CONFIG = {
    dataFile: '/tmp/ml_analysis_summary.json',
    imageFile: '/tmp/ml_analysis_results.png',
    maxRetries: 5,           // Thử 5 lần nếu chưa có dữ liệu
    retryDelay: 2000         // Delay 2 giây giữa các lần thử
};

// Auto-load khi trang mở
loadDataWithRetry()  // Tự động tải dữ liệu với retry
```

### 2️⃣ Nhúng Hình Ảnh (Images)
**Trước:**
```html
<img src="images/ml_result_1_customer_clustering.png" alt="...">
```

**Sau:**
```html
<img src="/tmp/ml_analysis_results.png" alt="..." 
     onerror="this.src='data:image/svg+xml...'">
     <!-- Nếu file chưa có, hiển thị placeholder -->
```

**Tất cả 6 hình ảnh** đã được cập nhật (các trang):
- ✅ Dashboard Tổng quan (page-dashboard)
- ✅ Phân cụm Khách hàng (page-customers)
- ✅ Dự đoán Doanh thu (page-forecast)
- ✅ Phân loại Sản phẩm (page-products)
- ✅ Phân tích Nâng cao (page-advanced) - 2 hình

### 3️⃣ Populate Stat Cards
**JavaScript tự động cập nhật:**
```javascript
// Lấy từ JSON data
const totalRevenue = data.total_revenue      // $...
const avgOrderValue = data.avg_order_value   // $...
const bestModelR2 = data.best_model_r2       // 0.824

// Update HTML elements
document.getElementById('total-revenue').innerText = '$' + totalRevenue
document.getElementById('avg-order-value').innerText = '$' + avgOrderValue
document.getElementById('best-model-r2').innerText = bestModelR2
```

---

## 📊 JSON Data Structure

File `/tmp/ml_analysis_summary.json` cần chứa:
```json
{
    "total_records": 797885,
    "total_revenue": 21416076.5,
    "avg_order_value": 26.84,
    "num_countries": 38,
    "num_products": 4000,
    "best_model_r2": 0.824,
    "top_countries": [...],
    "top_products": [...]
}
```

---

## 🔧 Cách Sử Dụng

### Bước 1: Chạy Spark Analysis
```
GUI → Spark Runner Tab → Chạy Spark Job
```

### Bước 2: Chuyển sang ML Analytics Tab
```
GUI → ML Analytics Tab → Click "Run Analysis"
```
✅ Tự động kéo dữ liệu từ Docker và mở dashboard

### Bước 3: Dashboard Mở Với Dữ Liệu
```
Browser → index2_1.html
├─ Tự động tải /tmp/ml_analysis_summary.json
├─ Populate stat cards
├─ Hiển thị /tmp/ml_analysis_results.png
└─ Nếu chưa có → Thử lại sau 2 giây (×5 lần)
```

---

## ⚙️ Configuration Tuning

Nếu muốn điều chỉnh retry logic, sửa `CONFIG` trong `<script>`:

```javascript
const CONFIG = {
    dataFile: '/tmp/ml_analysis_summary.json',    // ← Thay đổi đường dẫn JSON
    imageFile: '/tmp/ml_analysis_results.png',    // ← Thay đổi đường dẫn image
    maxRetries: 5,                                 // ← Tăng số lần retry
    retryDelay: 2000                              // ← Tăng delay (ms)
};
```

---

## 🐛 Troubleshooting

### ❌ Vấn đề: "⏳ Chưa có dữ liệu" (Placeholder hiển thị)
**Nguyên nhân:** Spark analysis chưa chạy hoặc file chưa được kéo về host

**Giải pháp:**
1. Kiểm tra Spark Job đã hoàn tất chưa (Spark Runner Tab)
2. Click "Run Analysis" để kéo dữ liệu từ Docker
3. Refresh dashboard (Ctrl+R)

### ❌ Vấn đề: Stat cards hiển thị "..."
**Nguyên nhân:** JSON file chưa được tạo

**Giải pháp:**
1. Chạy Spark analysis từ Spark Runner Tab
2. Hãy đợi 2-3 giây để dữ liệu được kéo về
3. Refresh browser

### ❌ Vấn đề: Hình ảnh không hiển thị
**Nguyên nhân:** File `/tmp/ml_analysis_results.png` chưa tồn tại

**Giải pháp:**
1. Chạy ML analysis (sẽ tạo file `ml_analysis_results.png`)
2. Refresh browser (Ctrl+R)
3. Nếu vẫn không được, kiểm tra Docker container đang chạy

---

## 📋 Cách Kiểm Tra Dữ Liệu

### Kiểm tra file JSON có tồn tại:
```powershell
# Windows PowerShell
Get-Item "C:\tmp\ml_analysis_summary.json" -ErrorAction Stop
Get-Item "C:\tmp\ml_analysis_results.png" -ErrorAction Stop
```

### Kiểm tra nội dung JSON:
```powershell
Get-Content "C:\tmp\ml_analysis_summary.json" | ConvertFrom-Json
```

---

## 📂 File Liên Quan

| File | Mục đích |
|------|---------|
| `index2_1.html` | Dashboard chính (đã cập nhật) |
| `/tmp/ml_analysis_summary.json` | Dữ liệu thống kê từ Spark |
| `/tmp/ml_analysis_results.png` | Biểu đồ từ Matplotlib |
| `docker_results_extractor.py` | Kéo dữ liệu từ Docker |
| `ml_analytics_tab.py` | Gọi extractor & mở dashboard |

---

## ✨ Features Bổ Sung

### Sidebar Navigation
- 7 trang phân tích khác nhau
- Click để chuyển trang (không cần reload)

### Responsive Design
- Bootstrap 5 grid system
- Mobile-friendly layout
- Gradient backgrounds & smooth animations

### Smart Fallback
- Nếu PNG không tìm thấy → Hiển thị placeholder gray
- Nếu JSON không tìm thấy → Retry tự động 5 lần
- Không bao giờ crash, luôn có fallback

---

## 🎓 Ví Dụ Dữ Liệu Mẫu

Dữ liệu sẽ nhìn như thế này khi Spark chạy xong:

```json
{
    "total_records": 797885,
    "total_revenue": 21416076.50,
    "avg_order_value": 26.84,
    "num_countries": 38,
    "num_products": 4000,
    "best_model_r2": 0.824,
    "top_countries": [
        {"country": "United Kingdom", "revenue": 500000},
        {"country": "Netherlands", "revenue": 300000},
        {"country": "Germany", "revenue": 250000}
    ],
    "top_products": [
        {"product": "Product A", "revenue": 50000},
        {"product": "Product B", "revenue": 45000}
    ]
}
```

Dashboard sẽ tự động populate tất cả giá trị này! 🎉

---

## 📞 Summary

✅ **Auto-load từ /tmp/** - Không cần thủ công  
✅ **Retry logic** - Chờ dữ liệu nếu chưa sẵn sàng  
✅ **Placeholder** - Fallback graceful khi chưa có dữ liệu  
✅ **7 Pages** - Tất cả đều nhúng hình ảnh từ `/tmp/`  
✅ **Beautiful UI** - Vietnamese interface, responsive design  

**Bây giờ mỗi khi bạn chạy Spark analysis, dashboard sẽ tự động update!** 🚀
