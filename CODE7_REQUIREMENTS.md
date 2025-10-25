# 📋 YÊU CẦU QUAN TRỌNG TRONG CODE7.PY

> **Tài liệu này liệt kê các yêu cầu PHẢI tuân thủ khi thay đổi code để đảm bảo kết quả đúng**

---

## 🎯 1. ĐƯỜNG DẪN & THƯ MỤC (CRITICAL)

### **OUTPUT_DIR - Thư mục lưu kết quả**

```python
# Dòng 39-43
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "tmp")
```

**Yêu cầu:**
- ✅ Phải tồn tại thư mục `tmp` trong project root
- ✅ Tự động tạo: `os.makedirs(OUTPUT_DIR, exist_ok=True)` (dòng 46)
- ⚠️ **QUAN TRỌNG:** Dashboard 3D load file từ đường dẫn này

**Cấu trúc thư mục:**
```
GUI-Docker/
├── run_spark_gui/
│   └── code7.py
└── tmp/                    ← OUTPUT_DIR trỏ vào đây
    ├── *.png (6 files)
    ├── customer_rfm_3d.json
    └── ml_analysis_summary.json
```

### **Input Data Path - Đường dẫn dữ liệu**

```python
# Dòng 60-62
possible_paths = [
    "hdfs://namenode:8020/input/online_retail_II.csv",
]
```

**Yêu cầu:**
- ✅ File `online_retail_II.csv` phải tồn tại trong HDFS
- ⚠️ **Lỗi phổ biến:** Path sai → code exit(1) (dòng 74)
- 💡 **Tip:** Có thể thêm nhiều path khác trong list để thử tuần tự

---

## 📊 2. TÊN FILE OUTPUT (PHẢI GIỮ NGUYÊN)

### **6 File Hình Ảnh ML**

| STT | Tên File | Dòng Code | Nội dung |
|-----|----------|-----------|----------|
| 1 | `ml_result_1_customer_clustering.png` | 446 | K-Means customer segmentation |
| 2 | `ml_result_2_regression_analysis.png` | 534 | Linear Regression predictions |
| 3 | `ml_result_3_product_clustering.png` | 607 | Bisecting K-Means products |
| 4 | `ml_result_4_comprehensive_dashboard.png` | 751 | Dashboard tổng quan |
| 5 | `ml_result_5_advanced_analytics.png` | 859 | Heatmaps & correlations |
| 6 | `ml_result_6_trends_comparison.png` | 953 | Time series & trends |

**Yêu cầu:**
- ❌ **KHÔNG được thay đổi tên file**
- 📌 **Lý do:** Dashboard HTML hardcode tên này
- ⚠️ **Nếu đổi tên:** Dashboard sẽ hiển thị ảnh lỗi (404)

**Code pattern:**
```python
plt.savefig(os.path.join(OUTPUT_DIR, 'ml_result_X_name.png'), dpi=300, bbox_inches='tight')
```

### **File JSON Tổng Kết**

```python
# Dòng 1003
json_path = os.path.join(OUTPUT_DIR, 'ml_analysis_summary.json')
```

**Yêu cầu:**
- ✅ Phải có tên chính xác `ml_analysis_summary.json`
- 📌 **Lý do:** Dashboard 3D fetch từ `tmp/ml_analysis_summary.json`
- 🔗 **Sử dụng:** Stats cards trong dashboard (dòng 150-180 trong HTML)

### **File RFM 3D Data** (CRITICAL!)

```python
# Dòng 243: Folder tạm
rfm_output_path = os.path.join(OUTPUT_DIR, "customer_rfm_3d_temp")

# Dòng 247-257: File cuối cùng
final_path = os.path.join(OUTPUT_DIR, "customer_rfm_3d.json")
```

**Yêu cầu:**
- ✅ File cuối cùng phải là `tmp/customer_rfm_3d.json`
- 📌 **Lý do:** Dashboard 3D load từ đường dẫn này
- ⚠️ **Không có file này:** Dashboard 3D hiển thị error screen

**Quy trình:**
1. Spark write → `customer_rfm_3d_temp/part-*.json`
2. Code tìm file part-*.json
3. Move → `customer_rfm_3d.json`
4. Delete folder temp

---

## 🔧 3. CẤU TRÚC DỮ LIỆU ĐẦU VÀO

### **Các Cột Bắt Buộc trong CSV**

| Cột | Bắt buộc | Mục đích |
|-----|----------|----------|
| `Quantity` | ✅ | Số lượng sản phẩm bán |
| `Price` | ✅ | Giá sản phẩm |
| `Invoice` | ✅ | Mã hóa đơn (count transactions) |
| `Country` | ✅ | Phân tích theo quốc gia |
| `Description` | ✅ | Tên sản phẩm |
| `Customer ID` | ⚠️ Tùy chọn | Customer segmentation |
| `InvoiceDate` | ⚠️ Tùy chọn | Tính Recency (3D data) |

### **Tìm Customer Column Tự Động**

```python
# Dòng 94-98
customer_col = None
for col_name in df_clean.columns:
    if 'customer' in col_name.lower():
        customer_col = col_name
        break
```

**Yêu cầu:**
- ✅ Tên cột chứa từ "customer" (không phân biệt hoa thường)
- ⚠️ **Nếu không có:** Code vẫn chạy nhưng bỏ qua phân cụm khách hàng
- 💡 **Hỗ trợ:** "Customer ID", "customer_id", "CUSTOMER", v.v.

### **Tìm Date Column Tự Động**

```python
# Dòng 218-222
date_col = None
for col_name in df_clean.columns:
    if 'date' in col_name.lower():
        date_col = col_name
        break
```

**Yêu cầu:**
- ✅ Tên cột chứa từ "date"
- ⚠️ **Nếu không có:** Không tính được Recency → Dashboard 3D hiển thị error
- 💡 **Hỗ trợ:** "InvoiceDate", "invoice_date", "DATE", v.v.

---

## 🎨 4. LABELS & CLUSTER NAMES (HARDCODED)

### **Customer Segments (K-Means k=3)**

```python
# Dòng 166-170
cluster_labels = {
    cluster_summary.iloc[0]['cluster']: 'VIP Customers',
    cluster_summary.iloc[1]['cluster']: 'Regular Customers',
    cluster_summary.iloc[2]['cluster']: 'Occasional Customers'
}
```

**Yêu cầu:**
- ✅ Phải có **đúng 3 labels** này
- 📌 **Lý do:** Dashboard 3D hardcode màu sắc theo tên

**Mapping màu sắc trong Dashboard:**

| Segment | Màu | Hex Code |
|---------|-----|----------|
| VIP Customers | 🟢 Xanh lá | #2ECC71 |
| Regular Customers | 🔵 Xanh dương | #3498DB |
| Occasional Customers | ⚪ Xám | #95A5A6 |

**⚠️ Nếu đổi tên:**
- Dashboard 3D sẽ không nhận diện được cluster
- Màu sắc sẽ không đúng
- Phải update cả file `unified_dashboard_3d.html`

### **Product Categories (Bisecting K-Means k=4)**

```python
# Dòng 398-400
all_labels = ['Bestsellers', 'Popular Items', 'Regular Items', 'Niche Products']
```

**Yêu cầu:**
- ✅ Phải có **đúng 4 labels** này (hoặc ít hơn nếu k nhỏ hơn)
- ⚠️ **Nếu đổi tên:** Heatmap trong VIZ 5 có thể lỗi màu
- 💡 **Có thể custom:** Nhưng phải đảm bảo số lượng = k

**Mapping tự động:**
```python
# Dòng 402-403
sorted_cluster_ids = product_cluster_summary['product_cluster'].tolist()
product_cluster_labels = dict(zip(sorted_cluster_ids, labels_to_use))
```

---

## 📈 5. ML MODEL PARAMETERS

### **K-Means Customer Clustering**

```python
# Dòng 134-141
for k in [3, 4, 5]:
    kmeans = KMeans(
        k=k, 
        seed=42,
        maxIter=20,
        featuresCol="features",
        predictionCol="cluster"
    )

optimal_k = 3  # Dòng 148
```

**Yêu cầu:**
- ✅ `optimal_k = 3` phải match với số lượng `cluster_labels`
- ⚠️ **Nếu đổi optimal_k:**
  - Cập nhật `cluster_labels` tương ứng (dòng 166-170)
  - Cập nhật màu sắc trong Dashboard HTML
- 💡 **Seed=42:** Đảm bảo reproducibility

### **Bisecting K-Means Product Clustering**

```python
# Dòng 378-383
bkmeans = BisectingKMeans(
    k=4,
    seed=42,
    featuresCol="features",
    predictionCol="product_cluster"
)
```

**Yêu cầu:**
- ✅ `k=4` phải match với `len(all_labels)`
- ⚠️ **Nếu đổi k:** Cập nhật `all_labels` (dòng 398)

### **Regression Models**

```python
# Linear Regression: dòng 330-335
lr = LinearRegression(
    featuresCol="features",
    labelCol="TotalRevenue",
    maxIter=100,
    regParam=0.1
)

# Random Forest: dòng 414-419
rf = RandomForestRegressor(
    featuresCol="features",
    labelCol="TotalRevenue",
    numTrees=20,
    maxDepth=5,
    seed=42
)
```

**Yêu cầu:**
- ✅ Giữ nguyên tên biến: `r2_score`, `rf_r2`, `rmse`, `rf_rmse`
- 📌 **Lý do:** JSON summary dùng các biến này (dòng 972-976)
- 💡 **Có thể tune:** maxIter, regParam, numTrees, maxDepth

---

## 🔍 6. DATA VALIDATION & FILTERING

### **Làm sạch dữ liệu**

```python
# Dòng 82-86
df_clean = df.dropna()
df_clean = df_clean.filter(col("Quantity") > 0)
df_clean = df_clean.filter(col("Price") > 0)
```

**Yêu cầu:**
- ✅ Loại bỏ giá trị null, âm, zero
- 📌 **Lý do:** Tránh lỗi khi train ML models
- ⚠️ **Không filter:** KMeans sẽ lỗi với giá trị NaN

### **RFM Export Validation**

```python
# Dòng 234-239
rfm_count = customer_rfm_with_cluster.count()
sample_df = customer_rfm_with_cluster.limit(5).toPandas()
print(f"📊 Tổng số khách hàng có RFM: {rfm_count:,}")
print(f"📈 Recency range: {sample_df['Recency'].min():.0f} - {sample_df['Recency'].max():.0f} ngày")
print(f"📈 Frequency range: {sample_df['Frequency'].min():.0f} - {sample_df['Frequency'].max():.0f} lần")
print(f"📈 Monetary range: £{sample_df['Monetary'].min():.2f} - £{sample_df['Monetary'].max():.2f}")
```

**Yêu cầu:**
- ✅ In ra thống kê để verify data OK
- ⚠️ **Nếu count=0:** Dashboard 3D sẽ hiển thị error
- 💡 **Debug:** Kiểm tra console logs

### **Cache Strategy**

```python
# Dòng 92
df_clean.cache()

# Dòng 129
customer_scaled.cache()

# Dòng 1075
df_clean.unpersist()
```

**Yêu cầu:**
- ✅ Cache DataFrame được dùng nhiều lần
- ✅ Unpersist sau khi xong
- 📌 **Lý do:** Tối ưu performance với Big Data

---

## 🎯 7. JSON SUMMARY FORMAT

### **Cấu trúc JSON bắt buộc**

```python
# Dòng 961-1019
summary_data = {
    # Metrics cơ bản
    "total_revenue": float,           # Tổng doanh thu
    "total_transactions": int,        # Tổng giao dịch
    "avg_order_value": float,         # Giá trị trung bình/đơn
    "total_records": int,             # Số records
    
    # Thông tin tổng quan
    "num_countries": int,             # Số quốc gia
    "num_products": int,              # Số sản phẩm
    "num_customers": int,             # Số khách hàng
    
    # Customer segments
    "num_vip": int,
    "num_regular": int,
    "num_occasional": int,
    
    # ML Model Performance
    "lr_r2_score": float,             # Linear Regression R²
    "lr_rmse": float,                 # Linear Regression RMSE
    "rf_r2_score": float,             # Random Forest R²
    "rf_rmse": float,                 # Random Forest RMSE
    "best_model": str,                # "Linear Regression" hoặc "Random Forest"
    "best_model_r2": float,           # R² của model tốt nhất
    
    # Top performers
    "top_country": str,
    "top_country_revenue": float,
    "top_product": str,
    "top_product_revenue": float,
    
    # Chi tiết phân cụm
    "customer_segments": {
        "VIP": {"count": int, "percentage": float},
        "Regular": {"count": int, "percentage": float},
        "Occasional": {"count": int, "percentage": float}
    },
    "product_categories": {
        "Bestsellers": {"count": int, "percentage": float},
        "Popular Items": {"count": int, "percentage": float},
        "Regular Items": {"count": int, "percentage": float},
        "Niche Products": {"count": int, "percentage": float}
    },
    
    # Metadata
    "analysis_date": str,             # ISO format
    "data_points": int,
    "analysis_status": "completed"
}
```

**Yêu cầu:**
- ✅ Dashboard đọc các key này → **KHÔNG được đổi tên**
- ✅ Data types phải đúng (int, float, str)
- ⚠️ **Nếu thiếu key:** Dashboard có thể crash hoặc hiển thị undefined

**Dashboard mapping:**

| JSON Key | Dashboard Component | HTML Line |
|----------|---------------------|-----------|
| `total_revenue` | Stat Card 1 | ~200 |
| `total_transactions` | Stat Card 2 | ~210 |
| `avg_order_value` | Stat Card 3 | ~220 |
| `best_model_r2` | Stat Card 4 | ~230 |
| `customer_segments` | Segments Table | 350-380 |
| `product_categories` | Categories Chart | 400-430 |

---

## ⚠️ 8. CÁC LỖI PHỔ BIẾN CẦN TRÁNH

### **1. Thay đổi tên file output**

```python
❌ KHÔNG:
plt.savefig(os.path.join(OUTPUT_DIR, 'ml_result_1_new.png'))
plt.savefig(os.path.join(OUTPUT_DIR, 'customer_clustering.png'))

✅ PHẢI:
plt.savefig(os.path.join(OUTPUT_DIR, 'ml_result_1_customer_clustering.png'))
```

### **2. Đổi tên cột trong RFM JSON**

```python
❌ KHÔNG:
col(customer_col).alias("CustomerID")      # Thiếu underscore
col(customer_col).alias("customer_id")     # Lowercase

✅ PHẢI:
col(customer_col).alias("Customer_ID")     # Đúng format
```

### **3. Đổi tên segment labels**

```python
❌ KHÔNG:
cluster_labels = {
    0: 'High Value Customers',     # Tên khác
    1: 'Medium Customers',
    2: 'Low Value Customers'
}

✅ PHẢI:
cluster_labels = {
    cluster_summary.iloc[0]['cluster']: 'VIP Customers',
    cluster_summary.iloc[1]['cluster']: 'Regular Customers',
    cluster_summary.iloc[2]['cluster']: 'Occasional Customers'
}
```

### **4. Thiếu file trong tmp/**

```bash
❌ THIẾU:
tmp/
├── ml_result_1_customer_clustering.png  ← Thiếu
└── ml_analysis_summary.json

KẾT QUẢ:
→ Dashboard 3D: Error "RFM data not found"
→ Stat cards: Rỗng
→ Gallery: Broken images (404)

✅ ĐẦY ĐỦ:
tmp/
├── customer_rfm_3d.json                     ← CRITICAL
├── ml_analysis_summary.json                 ← CRITICAL
├── ml_result_1_customer_clustering.png
├── ml_result_2_regression_analysis.png
├── ml_result_3_product_clustering.png
├── ml_result_4_comprehensive_dashboard.png
├── ml_result_5_advanced_analytics.png
└── ml_result_6_trends_comparison.png
```

### **5. Sai format JSON**

```python
❌ KHÔNG:
customer_rfm_with_cluster.select(
    "Recency",           # String type
    "Frequency",
    "Monetary",
    "prediction"
).write.json(path)

✅ PHẢI:
customer_rfm_with_cluster.select(
    col("Recency").cast("integer"),      # Cast to int
    col("Frequency").cast("integer"),
    col("Monetary").cast("double"),
    col("prediction").cast("integer")
).write.json(path)
```

### **6. Không kiểm tra customer_col**

```python
❌ KHÔNG:
customer_rfm = df_clean.groupBy(customer_col).agg(...)  # Crash nếu None

✅ PHẢI:
if customer_col:
    customer_rfm = df_clean.groupBy(customer_col).agg(...)
else:
    print("⚠️ Không tìm thấy cột Customer ID")
```

---

## ✅ CHECKLIST TRƯỚC KHI CHẠY CODE

### **Môi trường**

- [ ] HDFS đang chạy (namenode accessible)
- [ ] Spark đã cài đặt và config đúng
- [ ] Python packages: `pyspark`, `matplotlib`, `seaborn`, `pandas`, `numpy`
- [ ] Thư mục `tmp` có quyền ghi

### **Dữ liệu**

- [ ] File `online_retail_II.csv` tồn tại trong HDFS path
- [ ] File có đủ các cột bắt buộc: `Quantity`, `Price`, `Invoice`, `Country`, `Description`
- [ ] File có cột Customer (tùy chọn nhưng quan trọng)
- [ ] File có cột Date (tùy chọn nhưng quan trọng cho 3D)
- [ ] Dữ liệu đã làm sạch (không có giá trị âm/zero)

### **Sau khi chạy - Verify**

```bash
# 1. Kiểm tra 8 files output
ls tmp/

# 2. Verify RFM JSON format
head -n 3 tmp/customer_rfm_3d.json
# Output mong đợi:
# {"Customer_ID":12345,"Recency":10,"Frequency":25,"Monetary":1250.5,"prediction":0}
# {"Customer_ID":12346,"Recency":45,"Frequency":8,"Monetary":450.0,"prediction":2}
# ...

# 3. Verify JSON summary
cat tmp/ml_analysis_summary.json | jq '.total_revenue'

# 4. Kiểm tra file size
du -h tmp/*.png tmp/*.json
```

### **Console logs phải thấy**

```
✅ Đọc file thành công từ: hdfs://namenode:8020/input/online_retail_II.csv
✅ Dữ liệu đã sạch: X,XXX hàng
✅ Phân cụm thành công X,XXX khách hàng
✅ Đã xuất X,XXX records RFM
📂 File: d:\...\tmp\customer_rfm_3d.json
💾 Size: XX.X KB
✅ Đã lưu: d:\...\tmp\ml_result_1_customer_clustering.png
✅ Đã lưu: d:\...\tmp\ml_result_2_regression_analysis.png
...
✅ Đã lưu: d:\...\tmp\ml_analysis_summary.json
```

---

## 🚀 QUICK REFERENCE

### **Nếu muốn thay đổi k clusters:**

1. Thay `optimal_k = 3` → k mới (dòng 148)
2. Cập nhật `cluster_labels` với số lượng labels tương ứng (dòng 166-170)
3. Cập nhật màu sắc trong `unified_dashboard_3d.html`

### **Nếu muốn thay đổi tên file output:**

1. Đổi tên trong `code7.py` (6 chỗ)
2. Đổi tên trong `unified_dashboard_3d.html` (6 chỗ tương ứng)
3. Rebuild và test

### **Nếu dữ liệu không có Customer ID:**

- Code vẫn chạy được (dòng 100-101: `if customer_col`)
- Không có customer segmentation
- Không có RFM 3D data
- Dashboard 3D hiển thị error "RFM data not found"
- 4/6 biểu đồ vẫn được tạo (trừ VIZ 1 & một số subplot)

### **Nếu dữ liệu không có Date:**

- Customer clustering vẫn chạy (dùng Frequency + Monetary only)
- Không tính Recency → `customer_rfm_3d.json` không được tạo
- Dashboard 3D hiển thị error với hướng dẫn khắc phục
- Console log: "⚠️ Không tìm thấy cột Date - Dashboard sẽ dùng dữ liệu mẫu"

---

## 📚 DEPENDENCIES

### **Python Packages**

```bash
pip install pyspark==3.3.0
pip install matplotlib==3.7.1
pip install seaborn==0.12.2
pip install pandas==2.0.1
pip install numpy==1.24.3
```

### **External Services**

- HDFS (Hadoop Distributed File System)
- Spark (Apache Spark 3.x)
- HTTP Server (Python http.server hoặc từ GUI)

---

## 🔗 RELATED FILES

| File | Mục đích | Liên quan |
|------|----------|-----------|
| `code7.py` | Phân tích ML & export data | File chính |
| `code_v2_with_3d_export.py` | Phiên bản nâng cao với GMM | Tương tự code7.py |
| `unified_dashboard_3d.html` | Dashboard hiển thị 3D | Load files từ tmp/ |
| `dashboard_tab.py` | GUI tab quản lý dashboard | Open dashboard 3D |
| `ml_analytics_tab.py` | GUI tab chạy ML analysis | Trigger code7.py |

---

## 🎯 TÓM LẮC QUAN TRỌNG

### **🔴 CRITICAL (Không được thay đổi)**

- ✅ Tên 8 file output (6 PNG + 2 JSON)
- ✅ Format JSON (keys & data types)
- ✅ Cluster labels: "VIP Customers", "Regular Customers", "Occasional Customers"
- ✅ Đường dẫn: `tmp/customer_rfm_3d.json`, `tmp/ml_analysis_summary.json`

### **🟡 QUAN TRỌNG (Cần tuân thủ)**

- ✅ Đường dẫn HDFS data
- ✅ Có cột Customer/Date trong CSV
- ✅ Data validation & filtering
- ✅ Cache strategy cho Big Data

### **🟢 TÙY CHỌN (Có thể custom)**

- ✅ ML parameters (k, maxIter, seed, numTrees, maxDepth)
- ✅ DPI của ảnh (mặc định 300)
- ✅ Số lượng top products/countries hiển thị
- ✅ Màu sắc biểu đồ (nếu không ảnh hưởng Dashboard)

---

## 📝 VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-25 | Initial documentation |

---

## 🆘 TROUBLESHOOTING

### **Lỗi: "RFM data not found" trong Dashboard**

**Nguyên nhân:**
- File `customer_rfm_3d.json` không được tạo
- Không có cột Customer ID hoặc Date
- Lỗi trong quá trình export

**Khắc phục:**
1. Kiểm tra console logs của code7.py
2. Verify file tồn tại: `ls tmp/customer_rfm_3d.json`
3. Kiểm tra format: `head -n 1 tmp/customer_rfm_3d.json`
4. Re-run code7.py với đầy đủ Customer ID & Date

### **Lỗi: "Analysis data not found" trong Dashboard**

**Nguyên nhân:**
- File `ml_analysis_summary.json` không được tạo
- Lỗi JSON serialization

**Khắc phục:**
1. Kiểm tra dòng 961-1019 trong code7.py
2. Verify JSON valid: `cat tmp/ml_analysis_summary.json | jq`
3. Re-run code7.py

### **Lỗi: Ảnh không hiển thị trong Dashboard**

**Nguyên nhân:**
- Tên file PNG không đúng
- File không được tạo
- HTTP server không chạy

**Khắc phục:**
1. Kiểm tra 6 file PNG trong `tmp/`
2. Verify tên file chính xác
3. Start HTTP server: `python -m http.server 8000`

---

**📌 Lưu ý cuối cùng:**

> Tài liệu này được tạo để đảm bảo tính nhất quán khi thay đổi code. 
> Mọi thay đổi về tên file, labels, hoặc JSON format đều phải cập nhật 
> đồng bộ giữa `code7.py` và `unified_dashboard_3d.html`.

**Liên hệ:** Vo-Truong-Danh (GitHub: GUI-Docker)
