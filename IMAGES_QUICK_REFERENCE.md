# 🎨 Hướng Dẫn Nhanh - Dashboard Hiển Thị 6 Ảnh

## Mapping: Trang → Ảnh từ code7.py

```
📱 DASHBOARD (index2_1.html)
│
├─ 🏠 Trang Chủ
│  └─ 🖼️ /tmp/ml_result_4_comprehensive_dashboard.png
│     (Dashboard tổng hợp: metrics, top countries, top products, ML predictions)
│
├─ 👥 Phân cụm Khách hàng (K-Means)
│  └─ 🖼️ /tmp/ml_result_1_customer_clustering.png
│     (Scatter plot, Distribution, Metrics, Box plot)
│
├─ 📈 Dự đoán Doanh thu (Regression)
│  └─ 🖼️ /tmp/ml_result_2_regression_analysis.png
│     (Actual vs Predicted, Residuals, Top 10, Model comparison)
│
├─ 📦 Phân loại Sản phẩm (Bisecting K-Means)
│  └─ 🖼️ /tmp/ml_result_3_product_clustering.png
│     (Scatter plot, Category distribution, Avg metrics, Transactions)
│
└─ 🔍 Phân tích Nâng cao
   ├─ 🖼️ /tmp/ml_result_5_advanced_analytics.png
   │  (Heatmaps: Country vs Segment, Country vs Category)
   │  (Feature Importance, Revenue breakdown)
   │
   └─ 🖼️ /tmp/ml_result_6_trends_comparison.png
      (Revenue percentiles, Country comparison, Product scatter)
      (Normalized model comparison)
```

## 📊 Chi tiết từng Ảnh

### 1. ml_result_1_customer_clustering.png
**Kích thước**: 16x12 inch, 300 DPI  
**Chứa 4 biểu đồ:**
- Scatter plot: Frequency vs Monetary
- Distribution pie chart: % khách ở mỗi segment
- Average metrics: Revenue, Quantity, Transactions
- Box plot hoặc metrics so sánh

### 2. ml_result_2_regression_analysis.png
**Kích thước**: 16x12 inch, 300 DPI  
**Chứa 4 biểu đồ:**
- Actual vs Predicted (scatter)
- Residuals analysis
- Top 10 products prediction
- Model comparison (Linear vs Random Forest)

### 3. ml_result_3_product_clustering.png
**Kích thước**: 16x12 inch, 300 DPI  
**Chứa 4 biểu đồ:**
- Scatter: Quantity vs Revenue (log scale)
- Pie: Tỷ lệ danh mục
- Bar: Avg revenue by category
- Bar: Avg transactions by category

### 4. ml_result_4_comprehensive_dashboard.png
**Kích thước**: 20x14 inch, 300 DPI  
**Chứa:**
- Header: 4 stat cards (Total Revenue, Transactions, Avg Order Value, R²)
- Row 2: Top 5 countries, Top 5 products
- Row 3: Customer segments pie, Product categories pie
- Row 4: Predictions vs Actual, Model performance

### 5. ml_result_5_advanced_analytics.png
**Kích thước**: 16x12 inch, 300 DPI  
**Chứa 4 heatmaps/charts:**
- Heatmap: Country vs Segment
- Heatmap: Country vs Product Category
- Horizontal bar: Feature Importance
- Histogram hoặc distribution chart

### 6. ml_result_6_trends_comparison.png
**Kích thước**: 16x12 inch, 300 DPI  
**Chứa 4 biểu đồ:**
- Bar: Revenue percentiles (25%, 50%, 75%, 90%, 95%)
- Combo: Top countries (Revenue + Transactions)
- Scatter 3D: Product performance (Quantity, Revenue, Transactions)
- Normalized comparison: Models metrics

## 🔄 Workflow Hoàn Chỉnh

```
1. Spark Runner Tab
   └─ Click "Run Spark Job"
      └─ code7.py chạy bên trong Docker
         └─ Tạo 6 ảnh + 1 JSON trong /tmp/ (Docker container)

2. ML Analytics Tab
   └─ Click "Run Analysis"
      └─ docker_results_extractor chạy
         └─ Copy 6 ảnh từ Docker /tmp/ → Host /tmp/
         └─ Tạo /tmp/ml_analysis_summary.json

3. Browser opens index2_1.html
   └─ JavaScript auto-load tất cả ảnh từ /tmp/
      └─ loadAnalysisData(): Fetch JSON
      └─ Display 6 ảnh trên 6 trang
      └─ Populate stat cards với dữ liệu real
```

## ⚙️ JavaScript Configuration trong index2_1.html

```javascript
const CONFIG = {
    dataFile: '/tmp/ml_analysis_summary.json',
    imageFile: '/tmp/ml_analysis_results.png',  // DEPRECATED (old)
    maxRetries: 5,
    retryDelay: 2000  // 2 giây
};
```

## 🖼️ Image Loading Mapping

```javascript
// JavaScript tự động fetch ảnh khi page load
// Mỗi page có src riêng:

Page "overview" → <img src="/tmp/ml_result_4_comprehensive_dashboard.png">
Page "customers" → <img src="/tmp/ml_result_1_customer_clustering.png">
Page "forecast" → <img src="/tmp/ml_result_2_regression_analysis.png">
Page "products" → <img src="/tmp/ml_result_3_product_clustering.png">
Page "advanced" → <img src="/tmp/ml_result_5_advanced_analytics.png">
               → <img src="/tmp/ml_result_6_trends_comparison.png">
```

## ✅ Checklist Verification

- [ ] code7.py generates 6 PNG files → /tmp/ (Docker container)
- [ ] docker_results_extractor copies files → /tmp/ (Host)
- [ ] Browser opens index2_1.html
- [ ] Sidebar navigation shows 6 pages
- [ ] Each page loads correct image
- [ ] Stat cards show real data from JSON
- [ ] No "failed to load image" errors
- [ ] All images have 300 DPI quality

## 🐛 Troubleshooting

**Problem: Images not loading**
- Solution: Check `/tmp/` on host machine for 6 PNG files
- Command: `ls -la /tmp/ml_result_*.png`

**Problem: Only 1 image showing**
- Solution: Verify code7.py generated all 6 images (check logs)
- Command: `docker exec <container> ls -la /tmp/ml_result_*.png`

**Problem: Images load but wrong size**
- Solution: Images are 300 DPI, may be large - wait for full load
- Browser DevTools → Network tab → check image sizes (should be 2-5 MB each)

---

**Last Updated**: 2025-10-24  
**Version**: 2.0 (6 Images)  
**Previous Version**: 1.0 (1 Image)
