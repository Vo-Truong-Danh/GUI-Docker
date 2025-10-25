# 🎯 QUICK REFERENCE: CODE15.PY OUTPUT

## ✅ 8 FILES XUẤT RA

```bash
/tmp/
├── customer_rfm_3d.json                     # 245 KB - 4,372 records
├── ml_analysis_summary.json                 # 3 KB
├── ml_result_1_customer_clustering.png      # 800 KB - 5 segments
├── ml_result_2_regression_analysis.png      # 750 KB - LR vs RF
├── ml_result_3_product_clustering.png       # 780 KB - 4 categories
├── ml_result_4_comprehensive_dashboard.png  # 1.2 MB
├── ml_result_5_advanced_analytics.png       # 900 KB
└── ml_result_6_trends_comparison.png        # 850 KB
```

---

## 📊 CUSTOMER_RFM_3D.JSON FORMAT

```json
{"Customer_ID":12346,"Recency":326,"Frequency":2,"Monetary":1275.0,"prediction":4}
{"Customer_ID":12347,"Recency":2,"Frequency":182,"Monetary":4310.0,"prediction":0}
{"Customer_ID":12348,"Recency":76,"Frequency":31,"Monetary":1797.24,"prediction":2}
```

**Fields:**
- `Customer_ID`: int - ID khách hàng
- `Recency`: int - Số ngày từ lần mua cuối (0-373)
- `Frequency`: int - Số lần mua (2-210)
- `Monetary`: double - Tổng chi tiêu ($3.75 - $279,489)
- `prediction`: int - Cluster ID (0-4)

---

## 🎨 5 CUSTOMER SEGMENTS (CODE15)

| Cluster | Label | Đặc điểm | Màu Code | Màu Dashboard |
|---------|-------|----------|----------|---------------|
| 0 | VIP Customers | High M, High F, Low R | #e74c3c (Red) | ✅ Green (#2ECC71) |
| 1 | High-Value | Medium-High M, Medium F | #f39c12 (Orange) | ❌ Red (#E74C3C) |
| 2 | Regular | Medium M, Medium F | #3498db (Blue) | ✅ Blue (#3498DB) |
| 3 | Growing | Low-Medium M, Low F | #2ecc71 (Green) | ⚠️ Gray (default) |
| 4 | New | Low M, Very Low F | #9b59b6 (Purple) | ⚠️ Gray (default) |

**⚠️ MÀU KHÔNG KHỚP:** Dashboard 3D chỉ map 3 clusters (0,1,2), cần update!

---

## 🔧 CÁCH SỬA DASHBOARD 3D (OPTIONAL)

### **File:** `unified_dashboard_3d.html`

**Tìm dòng ~250-260:**
```javascript
// CŨ (3 màu):
const clusterColors = {
    0: '#2ECC71',  // Green
    1: '#E74C3C',  // Red
    2: '#3498DB'   // Blue
};
```

**Sửa thành (5 màu):**
```javascript
// MỚI (5 màu - khớp với code15):
const clusterColors = {
    0: '#e74c3c',  // VIP - Red
    1: '#f39c12',  // High-Value - Orange
    2: '#3498db',  // Regular - Blue
    3: '#2ecc71',  // Growing - Green
    4: '#9b59b6'   // New - Purple
};
```

**Tìm dòng ~280-300 (Legend labels):**
```javascript
// CŨ:
const clusterLabels = {
    0: 'VIP Customers',
    1: 'Lost Customers',
    2: 'Loyal Customers'
};
```

**Sửa thành:**
```javascript
// MỚI:
const clusterLabels = {
    0: 'VIP Customers',
    1: 'High-Value Customers',
    2: 'Regular Customers',
    3: 'Growing Customers',
    4: 'New Customers'
};
```

---

## 🚀 WORKFLOW HOÀN CHỈNH

### **1. Chạy ML Analysis**
```bash
cd "d:\BaiTapSinhVien\TH BigData\GUI-Docker"
spark-submit code15.py
# Hoặc: python code15.py
```

### **2. Kiểm tra Output**
```bash
# Check files
ls /tmp/*.{png,json}

# Verify RFM JSON
head -n 3 /tmp/customer_rfm_3d.json

# Check file size
du -h /tmp/customer_rfm_3d.json
# Expected: ~245 KB
```

### **3. Start HTTP Server**
```bash
# Từ GUI hoặc manual:
cd "d:\BaiTapSinhVien\TH BigData\GUI-Docker"
python -m http.server 8000
```

### **4. Mở Dashboards**
```
2D: http://localhost:8000/unified_dashboard.html
3D: http://localhost:8000/unified_dashboard_3d.html
```

---

## ✅ CHECKLIST VERIFY

### **Console Logs phải có:**
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
     🔍 Sample JSON: {"Customer_ID":12346,...}
```

### **Dashboard 3D phải có:**
```
✅ Stats Cards (4 cards): Revenue, Transactions, Avg Order, ML Accuracy
✅ 3D Scatter Plot: Auto-rotating, interactive
✅ Legend: 5 segments với màu sắc (nếu đã sửa HTML)
✅ Segments Table: 5 rows với count & percentage
✅ Console log: "✅ Loaded 4,372 customer records..."
```

### **Dashboard 2D phải có:**
```
✅ Header: Big Data Analytics Dashboard
✅ Stats Cards: 4 cards
✅ Gallery: 6 ảnh ML results
✅ Segments Table: 5 segments
✅ Footer: Timestamp
```

---

## 🆘 TROUBLESHOOTING

### **Q1: Dashboard 3D hiển thị "RFM data not found"**

**A:** Kiểm tra:
```bash
# 1. File có tồn tại?
ls /tmp/customer_rfm_3d.json

# 2. Format JSON đúng?
cat /tmp/customer_rfm_3d.json | head -n 1 | jq

# 3. Re-run code15
python code15.py
```

### **Q2: 3D Chart chỉ hiển thị 3 màu**

**A:** Bình thường! Dashboard hardcode 3 màu.
- **Option 1:** Sửa HTML (xem phần "Cách sửa Dashboard 3D" ở trên)
- **Option 2:** Chấp nhận cluster 3,4 dùng màu xám

### **Q3: Console error "Failed to fetch customer_rfm_3d.json"**

**A:** Kiểm tra:
```bash
# 1. HTTP server đang chạy?
netstat -an | findstr 8000

# 2. File path đúng?
# Dashboard fetch: http://localhost:8000/tmp/customer_rfm_3d.json
# File phải ở: d:\BaiTapSinhVien\...\tmp\customer_rfm_3d.json

# 3. CORS issue? (Nếu file:///)
# Phải dùng http://localhost, KHÔNG dùng file:///
```

---

## 📋 SO SÁNH 3 CODE FILES

| Feature | code7.py | code15.py | code_v2_with_3d_export.py |
|---------|----------|-----------|---------------------------|
| Customer K | 3 | 5 | 3 (GMM) |
| Product K | 4 (BKM) | 4 (KM Enhanced) | 4 (BKM) |
| RFM Export | ✅ | ✅ | ✅ |
| Outlier Handle | Basic | IQR+P95 | Basic |
| Scaler | Standard | Log+Robust | Standard |
| Best for | Demo | Real data | Advanced ML |

---

## 💡 TIPS

1. **Path Windows:**
   ```python
   # Sửa OUTPUT_DIR trong code15.py dòng 25:
   OUTPUT_DIR = "d:/BaiTapSinhVien/TH BigData/GUI-Docker/tmp/"
   ```

2. **Test nhanh không cần Spark:**
   ```python
   # Tạo file JSON mẫu
   echo '{"Customer_ID":12345,"Recency":10,"Frequency":25,"Monetary":1250.5,"prediction":0}' > /tmp/customer_rfm_3d.json
   ```

3. **Backup files:**
   ```bash
   # Trước khi re-run
   cp /tmp/*.{png,json} /tmp/backup_$(date +%Y%m%d_%H%M%S)/
   ```

---

**Last updated:** 2025-10-26  
**Status:** ✅ Code15.py đã được sửa và test thành công!
