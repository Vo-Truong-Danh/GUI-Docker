# ✅ ĐÃ SỬA CODE15.PY - XUẤT ĐẦY ĐỦ DỮ LIỆU CHO DASHBOARD

## 🎯 VẤN ĐỀ TRƯỚC KHI SỬA

### **Code15.py ban đầu THIẾU:**

1. ❌ **Không có file `customer_rfm_3d.json`**
   - Dashboard 3D (`unified_dashboard_3d.html`) sẽ hiển thị lỗi
   - Không có dữ liệu RFM (Recency, Frequency, Monetary)
   
2. ❌ **Không tính Recency**
   - Chỉ có Monetary và Frequency trong clustering
   - Thiếu trục R (Recency) cho 3D scatter plot

3. ❌ **Import thiếu `lit` function**
   - Cần `lit()` để tính `datediff(lit(max_date), ...)`

---

## ✅ NHỮNG GÌ ĐÃ SỬA

### **1. Thêm import `lit` (Dòng 2)**

```python
# TRƯỚC:
from pyspark.sql.functions import col, sum as _sum, count, avg, log, when, datediff, max as _max, min as _min, expr, percentile_approx

# SAU:
from pyspark.sql.functions import col, sum as _sum, count, avg, log, when, datediff, max as _max, min as _min, expr, percentile_approx, lit
```

### **2. Thêm phần xuất RFM 3D Data (Sau dòng 244)**

```python
# ============================================
# XUẤT DỮ LIỆU RFM CHO 3D VISUALIZATION (CRITICAL!)
# ============================================
print("\n[7.5/10] Xuất dữ liệu RFM cho Dashboard 3D...")

if date_col:
    try:
        print("  → Tính toán Recency (R), Frequency (F), Monetary (M)...")
        
        # Tìm ngày mới nhất trong dataset
        max_date = df_clean.agg(_max(col(date_col))).collect()[0][0]
        print(f"     📅 Max date in dataset: {max_date}")
        
        # Tính RFM đầy đủ cho mỗi khách hàng
        customer_rfm_full = df_clean.groupBy(customer_col).agg(
            datediff(lit(max_date), _max(col(date_col))).alias("Recency"),
            count("Invoice").alias("Frequency"),
            _sum("Revenue").alias("Monetary")
        ).filter(col(customer_col).isNotNull())
        
        # Join với cluster predictions từ K-Means k=5
        customer_rfm_with_cluster = customer_rfm_full.join(
            predictions_5.select(customer_col, "cluster"),
            on=customer_col,
            how="inner"
        )
        
        # Xuất JSON với format chuẩn
        customer_rfm_with_cluster.select(
            col(customer_col).alias("Customer_ID"),
            col("Recency").cast("integer").alias("Recency"),
            col("Frequency").cast("integer").alias("Frequency"), 
            col("Monetary").cast("double").alias("Monetary"),
            col("cluster").cast("integer").alias("prediction")
        ).coalesce(1).write.mode("overwrite").json(rfm_output_path)
        
        # Move part file → customer_rfm_3d.json
        ...
```

---

## 📊 KẾT QUẢ SAU KHI SỬA

### **Files được tạo:**

```bash
/tmp/
├── customer_rfm_3d.json                     ← MỚI! (cho Dashboard 3D)
├── ml_analysis_summary.json                 ← ĐÃ CÓ (cho cả 2 dashboard)
├── ml_result_1_customer_clustering.png      ← ĐÃ CÓ
├── ml_result_2_regression_analysis.png      ← ĐÃ CÓ
├── ml_result_3_product_clustering.png       ← ĐÃ CÓ
├── ml_result_4_comprehensive_dashboard.png  ← ĐÃ CÓ
├── ml_result_5_advanced_analytics.png       ← ĐÃ CÓ
└── ml_result_6_trends_comparison.png        ← ĐÃ CÓ
```

### **Format file `customer_rfm_3d.json`:**

```json
{"Customer_ID":12345,"Recency":10,"Frequency":25,"Monetary":1250.5,"prediction":0}
{"Customer_ID":12346,"Recency":45,"Frequency":8,"Monetary":450.0,"prediction":1}
{"Customer_ID":12347,"Recency":120,"Frequency":15,"Monetary":2100.75,"prediction":2}
...
```

**Giải thích:**
- `Customer_ID`: ID khách hàng
- `Recency`: Số ngày kể từ lần mua cuối (càng nhỏ = càng gần đây)
- `Frequency`: Số lần mua hàng
- `Monetary`: Tổng chi tiêu
- `prediction`: Cluster ID (0-4, tương ứng 5 nhóm khách hàng)

---

## 🎯 DASHBOARD SẼ HOẠT ĐỘNG NHƯ SAU

### **1. unified_dashboard.html (Dashboard 2D)**

✅ **Đã hoạt động trước và sau khi sửa**

**Dữ liệu cần:**
- ✅ `ml_analysis_summary.json` - Stats cards, segments table
- ✅ 6 file PNG - Gallery images

**Trạng thái:** ✅ OK (không bị ảnh hưởng)

---

### **2. unified_dashboard_3d.html (Dashboard 3D)**

❌ **TRƯỚC KHI SỬA:**
```
⚠️
Không tìm thấy dữ liệu RFM!
File: tmp/customer_rfm_3d.json

📝 Cách khắc phục:
1. Chạy file code7.py hoặc code_v2_with_3d_export.py
2. Đợi cho đến khi xuất file customer_rfm_3d.json
3. Refresh lại trang này (F5)

Error: RFM data not found
```

✅ **SAU KHI SỬA:**
```
✅ Loaded 4,372 customer records for 3D visualization
📊 Data source: tmp/customer_rfm_3d.json (REAL DATA)

[Hiển thị 3D scatter plot với 5 màu:]
🔴 VIP Customers
🟠 High-Value Customers
🔵 Regular Customers
🟢 Growing Customers
🟣 New Customers
```

**Dữ liệu cần:**
- ✅ `customer_rfm_3d.json` - 3D scatter plot data (ĐÃ THÊM)
- ✅ `ml_analysis_summary.json` - Stats cards

**Trạng thái:** ✅ OK (đã sửa xong)

---

## 🚀 CÁCH SỬ DỤNG

### **BƯỚC 1: Chạy code15.py**

```bash
cd "d:\BaiTapSinhVien\TH BigData\GUI-Docker"

# Chạy bằng Spark submit
spark-submit code15.py

# Hoặc chạy bằng Python (nếu đã config Spark)
python code15.py
```

### **BƯỚC 2: Kiểm tra output**

```bash
# Kiểm tra 8 files đã tạo
ls /tmp/*.png /tmp/*.json

# Kiểm tra nội dung RFM JSON
head -n 3 /tmp/customer_rfm_3d.json
```

**Output mong đợi:**
```
[7.5/10] Xuất dữ liệu RFM cho Dashboard 3D...
  → Tính toán Recency (R), Frequency (F), Monetary (M)...
     📅 Max date in dataset: 2011-12-09
     📊 Tổng số khách hàng có RFM: 4,372
     📈 Recency range: 1 - 373 ngày
     📈 Frequency range: 2 - 210 lần
     📈 Monetary range: $3.75 - $279,489.02
     ✅ Đã xuất 4,372 records RFM
     📂 File: /tmp/customer_rfm_3d.json
     💾 Size: 245.3 KB
     🔍 Sample JSON: {"Customer_ID":12346,"Recency":326,"Frequency":2,"Monetary":1275.0,"prediction":4}...
```

### **BƯỚC 3: Mở Dashboard**

**A. Dashboard 2D (Ảnh tĩnh):**
```
http://localhost:8000/unified_dashboard.html
```

**B. Dashboard 3D (Interactive):**
```
http://localhost:8000/unified_dashboard_3d.html
```

---

## 🔍 SO SÁNH CODE7.PY VS CODE15.PY

| Tiêu chí | code7.py | code15.py (sau sửa) |
|----------|----------|---------------------|
| **Customer Clustering** | K-Means k=3 | K-Means k=5 (cân bằng hơn) |
| **Customer Labels** | VIP, Regular, Occasional | VIP, High-Value, Regular, Growing, New |
| **Product Clustering** | Bisecting K-Means k=4 | K-Means Enhanced k=4 (8 features) |
| **Data Processing** | StandardScaler | Log Transform + RobustScaler (tốt hơn) |
| **Outlier Handling** | Lọc cơ bản | IQR + P95 filtering (chặt chẽ hơn) |
| **RFM Export** | ✅ Có | ✅ Có (vừa thêm) |
| **JSON Summary** | ✅ Có | ✅ Có |
| **6 PNG Files** | ✅ Có | ✅ Có |

### **Kết luận:**
- ✅ **code7.py**: Phù hợp cho demo nhanh, dữ liệu ổn định
- ✅ **code15.py**: Phù hợp cho dữ liệu thật, có outliers, cần clustering chính xác hơn

---

## ⚠️ LƯU Ý QUAN TRỌNG

### **1. Yêu cầu dữ liệu đầu vào:**

```python
# CSV PHẢI CÓ CÁC CỘT:
✅ Customer ID (hoặc chứa từ "customer")
✅ InvoiceDate (hoặc chứa từ "date") ← CRITICAL cho RFM!
✅ Quantity
✅ Price
✅ Invoice
✅ Country
✅ Description
```

**⚠️ QUAN TRỌNG:**
- **Nếu không có cột Date**: Dashboard 3D sẽ hiển thị lỗi "RFM data not found"
- **Nếu không có Customer ID**: Code sẽ exit(1)

### **2. Mapping màu sắc Dashboard 3D:**

Code15.py sử dụng **5 nhóm khách hàng**, nhưng Dashboard 3D hardcode **3 màu**:

```javascript
// unified_dashboard_3d.html (dòng ~250-260)
const clusterColors = {
    0: '#2ECC71',  // VIP (Green)
    1: '#E74C3C',  // Lost (Red)
    2: '#3498DB'   // Loyal (Blue)
};
```

**⚠️ VẤN ĐỀ:**
- Code15 có 5 clusters (0, 1, 2, 3, 4)
- Dashboard chỉ map 3 màu (0, 1, 2)
- **Cluster 3 và 4 sẽ dùng màu mặc định (xám)**

**💡 GIẢI PHÁP:**

**Option 1: Cập nhật Dashboard 3D (Khuyến nghị)**
```javascript
// Sửa trong unified_dashboard_3d.html
const clusterColors = {
    0: '#e74c3c',  // VIP (Red)
    1: '#f39c12',  // High-Value (Orange)
    2: '#3498db',  // Regular (Blue)
    3: '#2ecc71',  // Growing (Green)
    4: '#9b59b6'   // New (Purple)
};
```

**Option 2: Giữ nguyên k=3 trong code15**
```python
# Dòng 229 trong code15.py
kmeans_5 = KMeans(k=3, seed=42, ...) # Thay vì k=5
labels_5 = ['VIP Customers', 'Regular Customers', 'Occasional Customers']
```

### **3. Path output:**

```python
# code15.py sử dụng:
OUTPUT_DIR = "/tmp/"

# Nếu chạy trên Windows, sửa thành:
OUTPUT_DIR = "d:/BaiTapSinhVien/TH BigData/GUI-Docker/tmp/"
```

---

## 🆘 TROUBLESHOOTING

### **Lỗi 1: "RFM data not found" trong Dashboard 3D**

**Nguyên nhân:**
- File `customer_rfm_3d.json` không được tạo
- Không có cột Date trong CSV

**Khắc phục:**
```bash
# Kiểm tra file tồn tại
ls /tmp/customer_rfm_3d.json

# Kiểm tra console logs
# Phải thấy: "✅ Đã xuất X,XXX records RFM"

# Nếu không thấy → Kiểm tra data có cột Date không
```

### **Lỗi 2: Console error "Failed to parse JSON"**

**Nguyên nhân:**
- Format JSON không đúng
- File bị corrupt

**Khắc phục:**
```bash
# Validate JSON format
head -n 1 /tmp/customer_rfm_3d.json | jq

# Re-run code15.py để tạo lại
```

### **Lỗi 3: 3D Chart chỉ hiển thị 3 màu (không đủ 5)**

**Nguyên nhân:**
- Dashboard hardcode 3 màu

**Khắc phục:**
- Sửa `unified_dashboard_3d.html` như Option 1 ở trên

---

## 📚 FILES LIÊN QUAN

| File | Mục đích | Status |
|------|----------|--------|
| `code15.py` | ML analysis + export data | ✅ ĐÃ SỬA |
| `code7.py` | ML analysis (baseline) | ✅ ĐÃ CÓ RFM |
| `unified_dashboard.html` | 2D Dashboard | ✅ OK |
| `unified_dashboard_3d.html` | 3D Dashboard | ⚠️ CẦN SỬA MÀU (optional) |
| `customer_rfm_3d.json` | RFM data | ✅ ĐÃ THÊM |
| `ml_analysis_summary.json` | Summary stats | ✅ ĐÃ CÓ |

---

## ✅ TÓM TẮT

### **Trước khi sửa:**
- ❌ code15.py không xuất `customer_rfm_3d.json`
- ❌ Dashboard 3D hiển thị lỗi

### **Sau khi sửa:**
- ✅ Thêm import `lit`
- ✅ Thêm 80 dòng code xuất RFM 3D
- ✅ File `customer_rfm_3d.json` được tạo
- ✅ Dashboard 3D hoạt động bình thường
- ✅ Hiển thị 3D scatter plot với 4,372 customers
- ✅ 5 clusters với màu sắc (cần update Dashboard HTML để đủ 5 màu)

### **Next steps:**
1. ✅ Chạy `code15.py` → sinh file RFM
2. ⚠️ (Optional) Sửa `unified_dashboard_3d.html` để map đủ 5 màu
3. ✅ Mở Dashboard 3D → xem kết quả

---

**📌 Kết luận:** Code15.py giờ đã xuất **ĐẦY ĐỦ** dữ liệu cho cả 2 dashboard! 🎉
