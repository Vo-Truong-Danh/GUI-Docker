🤖 ML ANALYTICS TAB - HƯỚNG DẪN SỬ DỤNG
==========================================

📋 GIỚI THIỆU
=============
Tab "ML Analytics" (🤖 ML Analytics) là tab mới được thêm vào ứng dụng GUI-Docker để thực hiện phân tích Big Data nâng cao với Machine Learning.

Chức năng chính:
✓ Phân tích dữ liệu lớn từ HDFS hoặc file CSV local
✓ K-Means Clustering cho phân khúc khách hàng
✓ Linear Regression & Random Forest cho dự đoán doanh thu
✓ Bisecting K-Means cho phân cụm sản phẩm
✓ Visualization nâng cao (6 biểu đồ chuyên nghiệp)
✓ Chi tiết báo cáo và thống kê


🚀 CÁCH SỬ DỤNG
================

1️⃣ MỞ TAB ML ANALYTICS
   - Nhấp vào tab "🤖 ML Analytics" trong giao diện chính
   - Tab sẽ hiển thị form cấu hình phân tích

2️⃣ CẤU HÌNH DỮ LIỆU ĐẦU VÀO
   
   📁 Input File:
   - Nhập đường dẫn file CSV hoặc HDFS path
   - Ví dụ: 
     * hdfs://namenode:8020/input/online_retail_II.csv (HDFS)
     * C:\data\sales_data.csv (Local file)
   
   📂 Output Directory:
   - Chỉ định thư mục lưu kết quả
   - Ví dụ:
     * /tmp/ (Linux/Mac)
     * C:\temp\ (Windows)
     * /home/user/output/

3️⃣ CHỌN LOẠI PHÂN TÍCH
   ✓ Customer Segmentation (K-Means) - Phân khúc khách hàng
   ✓ Revenue Prediction (Linear Regression + Random Forest) - Dự đoán doanh thu
   ✓ Advanced Visualization (6 charts) - Biểu đồ trực quan

   Bạn có thể chọn một hoặc nhiều loại phân tích

4️⃣ CHẠY PHÂN TÍCH
   - Nhấp nút "▶️ Run Analysis"
   - Ứng dụng sẽ hiển thị tiến trình thực hiện
   - Console sẽ in ra các bước đang xử lý

5️⃣ XEM KẾT QUẢ
   - Phần "📊 Progress" hiển thị % hoàn thành
   - Phần "📝 Console Output" in chi tiết từng bước
   - Phần "📈 Results" tóm tắt kết quả phân tích chính

6️⃣ XEM TẬP TIN KẾT QUẢ
   - Nhấp "📂 Open Output Folder" để mở folder chứa kết quả
   - Các file sẽ được lưu với các tên:
     * ml_analysis_results.png (Biểu đồ chính)
     * ml_analysis_summary.json (Thống kê chi tiết)


📊 CÁC PHÂN TÍCH CHI TIẾT
==========================

1️⃣ CUSTOMER SEGMENTATION (K-MEANS)
   Mục đích: Phân chia khách hàng thành các nhóm có hành vi tương tự
   
   Kết quả:
   - 3 phân khúc: VIP Customers, Regular Customers, Occasional Customers
   - Metrics: Monetary, Frequency, Average Order Value
   - Biểu đồ: Scatter plot, Distribution pie chart, Metrics comparison, Box plot
   
   Ứng dụng:
   → Xác định khách hàng VIP để tăng chăm sóc
   → Tạo chiến lược marketing riêng cho từng phân khúc
   → Dự đoán lifetime value của khách hàng

2️⃣ REVENUE PREDICTION (REGRESSION)
   Mục đích: Dự đoán doanh thu từ các đặc trưng sản phẩm
   
   Mô hình:
   - Linear Regression (R² Score, RMSE metrics)
   - Random Forest Regression (So sánh hiệu suất)
   
   Kết quả:
   - R² Score: Mức độ phù hợp của mô hình (0-1, cao hơn là tốt)
   - RMSE: Sai số dự đoán (thấp hơn là tốt)
   
   Biểu đồ:
   - Actual vs Predicted scatter plot
   - Residuals analysis
   - Top 10 predictions comparison
   - Model comparison

3️⃣ PRODUCT CLUSTERING (BISECTING K-MEANS)
   Mục đích: Phân cụm sản phẩm thành các danh mục
   
   Kết quả:
   - 4 danh mục: Bestsellers, Popular Items, Regular Items, Niche Products
   - Tính toán dựa trên: Quantity, Revenue, Transactions
   - Biểu đồ: Scatter (log scale), Distribution pie, Average metrics, Transactions


⚙️ CẤU HÌNH NÂNG CAO
=====================

File cấu hình: run_spark_gui/ml_analytics_tab.py

Bạn có thể tùy chỉnh:
- Số lượng clusters (K-means: thay đổi k=3 thành k=4, 5...)
- Loại visualization (thêm/bớt biểu đồ)
- Thông số machine learning (learning rate, iterations...)
- Output format (PNG, PDF, SVG...)


📈 KẾT QUẢ PHÂN TÍCH
====================

File ml_analysis_summary.json sẽ chứa:
{
  "timestamp": "2025-10-24T15:30:45.123456",
  "total_records": 500000,
  "total_revenue": 1500000.50,
  "num_countries": 38,
  "num_products": 4000,
  "top_countries": [
    {"Country": "United Kingdom", "Total_Revenue": 500000},
    ...
  ],
  "top_products": [
    {"Description": "Product Name", "Total_Revenue": 50000},
    ...
  ]
}

File ml_analysis_results.png:
- Biểu đồ tóm tắt Top Countries & Top Products
- DPI 300 - Chất lượng cao cho báo cáo


🛠️ TROUBLESHOOTING
===================

❌ Lỗi: "Analysis is already running"
✅ Giải pháp: Đợi phân tích hiện tại hoàn thành hoặc nhấp "⏹️ Stop"

❌ Lỗi: "Input file not found"
✅ Giải pháp: Kiểm tra đường dẫn file HDFS hoặc local path

❌ Lỗi: "Permission denied"
✅ Giải pháp: 
   - Kiểm tra quyền truy cập file
   - Kiểm tra quyền ghi folder output
   - Chạy với quyền admin nếu cần

❌ Lỗi: "Spark not available"
✅ Giải pháp:
   - Kiểm tra Docker Spark container đang chạy
   - Cài đặt PySpark: pip install pyspark

❌ Lỗi: "Library import error"
✅ Giải pháp:
   Cài đặt dependencies:
   pip install matplotlib seaborn pandas numpy scikit-learn


📚 THAM KHẢO
=============

File gốc: code7.py (1022 dòng code ML nâng cao)
- Chứa toàn bộ logic phân tích ML
- Có thể chạy standalone từ terminal

Ứng dụng tích hợp: main.py
- Tích hợp ML Analytics Tab vào GUI
- Gọi hàm từ ml_analytics_tab.py

Framework: Tkinter (Python GUI)
- Modern theme Light/Dark
- Responsive UI design


💡 MẸO VÀ TRICK
================

1️⃣ Phân tích nhanh:
   - Input: HDFS path để xử lý trực tiếp trên cluster
   - Chọn: Chỉ "Revenue Prediction" nếu chỉ cần dự đoán
   - Output: SSD hoặc RAM disk để tăng tốc độ lưu

2️⃣ Phân tích chi tiết:
   - Chọn cả 3 loại phân tích
   - Lưu kết quả vào NFS hoặc cloud storage
   - Tạo dashboard từ kết quả PNG

3️⃣ Batch processing:
   - Chuẩn bị danh sách file input
   - Chạy lần lượt từng file
   - Tập hợp kết quả để so sánh

4️⃣ Tích hợp CI/CD:
   - Chạy ml_analytics_tab.py qua subprocess
   - Tự động hóa báo cáo hàng ngày
   - Gửi alert nếu phát hiện anomaly


📞 HỖ TRỢ
==========

Nếu gặp vấn đề:
1. Kiểm tra console output để xem lỗi chi tiết
2. Đọc lại hướng dẫn này
3. Kiểm tra file code7.py gốc (nếu cần chỉnh sửa)
4. Xem logs trong folder run_spark_gui/logs/

Version: 1.0
Last Updated: 2025-10-24
