# 🎨 Dashboard 3D Visualization - Hướng dẫn sử dụng

## 📋 Tổng quan

Dashboard 3D là giao diện trực quan hóa nâng cao sử dụng **ECharts GL** để hiển thị phân khúc khách hàng (Customer Segmentation) trong không gian 3 chiều với các trục:
- **X-axis (Recency)**: Số ngày kể từ lần mua gần nhất
- **Y-axis (Frequency)**: Số lần mua hàng
- **Z-axis (Monetary)**: Tổng giá trị đơn hàng (£)

## 🚀 Cách sử dụng

### Bước 1: Chạy code7.py để tạo dữ liệu

```bash
cd run_spark_gui
python code7.py
```

**Code7.py sẽ tự động:**
- ✅ Phân tích dữ liệu với PySpark
- ✅ Thực hiện K-Means clustering
- ✅ Tạo file `tmp/customer_rfm_3d.json` chứa dữ liệu RFM
- ✅ Tạo file `tmp/ml_analysis_summary.json` chứa tổng kết
- ✅ Tạo 6 file hình ảnh phân tích ML

### Bước 2: Khởi động Dashboard

#### **Cách 1: Qua GUI (Khuyến nghị)**

1. Chạy ứng dụng:
   ```bash
   cd run_spark_gui
   python main.py
   ```

2. Vào tab **"Dashboard"**

3. Click **"🚀 Khởi Động Server"**

4. Click **"🎨 Mở Dashboard 3D"**

#### **Cách 2: Trực tiếp qua HTTP Server**

```bash
# Từ thư mục gốc
cd "d:\BaiTapSinhVien\TH BigData\GUI-Docker"
python -m http.server 8000

# Mở browser:
# http://localhost:8000/unified_dashboard_3d.html
```

## 🎯 Tính năng Dashboard 3D

### 1️⃣ **Biểu đồ 3D Scatter Plot (ECharts GL)**
- 🔄 **Auto-rotation**: Biểu đồ tự động xoay để dễ quan sát
- 🖱️ **Interactive**: 
  - Kéo chuột để xoay
  - Cuộn chuột để zoom
  - Hover để xem chi tiết khách hàng
- 🎨 **Color-coded clusters**:
  - 🟢 Xanh lá: Khách hàng Vàng (Gold)
  - 🔵 Xanh dương: Khách hàng Trung thành (Loyal)
  - ⚪ Xám: Khách hàng đã mất (Lost)

### 2️⃣ **Stat Cards**
Hiển thị 4 chỉ số quan trọng:
- 💰 Tổng Doanh Thu
- 📊 Tổng Giao Dịch
- 📈 Giá Trị TB/Đơn
- 🎯 ML Accuracy (R² Score)

### 3️⃣ **Customer Segments Table**
Bảng chi tiết phân khúc khách hàng với:
- Số lượng khách hàng
- Trung bình Recency
- Trung bình Frequency
- Trung bình Monetary

### 4️⃣ **ML Analysis Images**
Gallery 6 hình ảnh phân tích ML:
1. Customer Clustering
2. Regression Analysis
3. Product Clustering
4. Comprehensive Dashboard
5. Advanced Analytics
6. Trends Comparison

### 5️⃣ **Code Snippet & Insights**
- 📝 Code Python minh họa K-Means clustering
- 💡 Giải thích về phân khúc khách hàng
- 📚 Quote box giải thích RFM

## 📊 Dữ liệu cần thiết

Dashboard cần 2 file JSON:

### 1. `tmp/customer_rfm_3d.json` (Bắt buộc cho 3D chart)
Format: JSON Lines (mỗi dòng là 1 JSON object)

```json
{"Customer_ID":"12345","Recency":45,"Frequency":12,"Monetary":5432.50,"prediction":0}
{"Customer_ID":"67890","Recency":321,"Frequency":2,"Monetary":150.00,"prediction":1}
```

**Các trường:**
- `Customer_ID`: ID khách hàng
- `Recency`: Số ngày từ lần mua gần nhất
- `Frequency`: Tổng số lần mua
- `Monetary`: Tổng giá trị đơn hàng (£)
- `prediction`: Cluster ID (0, 1, 2)

### 2. `tmp/ml_analysis_summary.json` (Cho stats & table)
Format: JSON object

```json
{
  "timestamp": "2025-10-25T10:30:00",
  "total_revenue": 8294000.50,
  "total_transactions": 541909,
  "avg_order_value": 15.30,
  "ml_models": {
    "linear_regression": {
      "r2_score": 0.857
    }
  },
  "customer_segments": [
    {
      "Segment": "VIP Customers",
      "Count": 3876,
      "Avg_Recency": 45.2,
      "Avg_Frequency": 15.8,
      "Avg_Monetary": 12543.67
    }
  ]
}
```

## ⚠️ Xử lý lỗi

### ❌ **Lỗi: "RFM data not found"**
**Nguyên nhân:** Chưa chạy code7.py hoặc file JSON chưa được tạo

**Giải pháp:**
1. Chạy code7.py để tạo dữ liệu
2. Dashboard sẽ tự động fallback sang dữ liệu mẫu (sample data)

### ❌ **Lỗi: "Analysis data not found"**
**Nguyên nhân:** File ml_analysis_summary.json không tồn tại

**Giải pháp:**
1. Chạy code7.py
2. Kiểm tra thư mục `tmp/`

### ❌ **Lỗi: Biểu đồ 3D không hiển thị**
**Giải pháp:**
1. Kiểm tra console (F12) xem có lỗi JavaScript
2. Đảm bảo CDN ECharts GL đã load: `echarts-gl.min.js`
3. Thử hard refresh: `Ctrl + Shift + R`

### ❌ **Lỗi: Server won't start (Port 8000 đã được sử dụng)**
**Giải pháp:**
```bash
# Windows PowerShell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process

# Hoặc đổi port
python -m http.server 8080
# Rồi truy cập: http://localhost:8080/unified_dashboard_3d.html
```

## 🎓 Kiến thức nâng cao

### RFM Analysis
**RFM** là phương pháp phân khúc khách hàng dựa trên:

- **R (Recency)**: Khách hàng mua gần đây → Có khả năng mua lại cao
- **F (Frequency)**: Khách hàng mua thường xuyên → Trung thành
- **M (Monetary)**: Khách hàng chi nhiều → Giá trị cao

### K-Means Clustering
Thuật toán phân cụm unsupervised learning:
- Tự động nhóm khách hàng có đặc điểm tương tự
- k=3: Tạo 3 nhóm khách hàng (Gold, Loyal, Lost)
- Sử dụng StandardScaler để chuẩn hóa features

### ECharts GL
Thư viện JavaScript 3D visualization:
- Hỗ trợ WebGL rendering
- Smooth rotation & zoom
- Interactive tooltips
- Mobile-friendly

## 📱 Responsive Design

Dashboard tương thích với nhiều kích thước màn hình:

- **Desktop (>1200px)**: Layout 2 cột
- **Tablet (768px-1200px)**: Layout 1-2 cột
- **Mobile (<768px)**: Layout 1 cột, stack vertically

## 🔧 Tùy chỉnh

### Thay đổi tốc độ xoay 3D chart
File: `unified_dashboard_3d.html`

```javascript
viewControl: {
    autoRotate: true,
    autoRotateSpeed: 8,  // Thay đổi giá trị này (mặc định: 8)
    distance: 180
}
```

### Thay đổi màu sắc clusters
```javascript
const clusterInfo = {
    0: { name: 'Khách hàng Vàng', color: '#2ECC71' },     // Thay màu ở đây
    1: { name: 'Khách hàng đã mất', color: '#95A5A6' },
    2: { name: 'Khách hàng Trung thành', color: '#3498DB' }
};
```

### Thay đổi kích thước điểm
```javascript
series: [{
    symbolSize: 6,  // Thay đổi giá trị này (mặc định: 6)
    ...
}]
```

## 📚 Tài liệu tham khảo

- **ECharts Documentation**: https://echarts.apache.org/
- **ECharts GL**: https://github.com/ecomfe/echarts-gl
- **Tailwind CSS**: https://tailwindcss.com/
- **RFM Analysis**: https://en.wikipedia.org/wiki/RFM_(market_research)

## 🎉 Checklist hoàn thành

- ✅ Dashboard 3D HTML đã tạo
- ✅ Code7.py xuất dữ liệu RFM
- ✅ Tích hợp vào GUI (dashboard_tab.py)
- ✅ Sample data fallback
- ✅ Responsive design
- ✅ Error handling
- ✅ Documentation

## 🆘 Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra console log (F12)
2. Xem file log trong GUI
3. Đảm bảo đã chạy code7.py
4. Thử hard refresh (Ctrl+Shift+R)

---

**Version:** 1.0  
**Last Updated:** 25/10/2025  
**Author:** Big Data Analytics Team  
**Status:** ✅ PRODUCTION READY
