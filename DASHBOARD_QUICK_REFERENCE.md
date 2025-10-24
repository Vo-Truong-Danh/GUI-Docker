# 📚 Quick Reference - Dashboard Auto-Load

## 🎯 TL;DR (Tóm Tắt Ngắn)

### Dữ Liệu Từ Đâu?
```
Spark (Docker /tmp/) 
    ↓
docker_results_extractor (copy files)
    ↓
Host /tmp/
    ↓
Browser (index2_1.html) 
    ↓
Dashboard Hiển Thị ✓
```

### Là Dữ Liệu Mẫu Hay Thật?
**100% THẬT** - Từ Spark analysis của bạn!

---

## 📝 Code Changes

### 1. JavaScript Added to index2_1.html
```javascript
// Auto-load configuration
const CONFIG = {
    dataFile: '/tmp/ml_analysis_summary.json',
    imageFile: '/tmp/ml_analysis_results.png',
    maxRetries: 5,
    retryDelay: 2000
};

// Load on page open
loadDataWithRetry();

// Functions added:
// - loadAnalysisData()     → fetch JSON
// - loadDataWithRetry()    → retry logic
// - populateDashboard()    → update stat cards
```

### 2. Image Sources Updated
**All 6 images changed from:**
```html
<img src="images/ml_result_*.png">
```

**To:**
```html
<img src="/tmp/ml_analysis_results.png" onerror="placeholder">
```

### 3. Stat Cards Updated
```javascript
// Auto-populate from JSON:
document.getElementById('total-revenue').innerText = '$' + data.total_revenue
document.getElementById('avg-order-value').innerText = '$' + data.avg_order_value
document.getElementById('best-model-r2').innerText = data.best_model_r2
```

---

## 🔄 Data Flow Diagram

```
┌──────────────────────────────────────────────────────────┐
│                   BROWSER (You)                          │
│                                                          │
│  1. Open ML Analytics Tab                              │
│     └─ Click "Run Analysis"                            │
│        └─ Calls: docker_results_extractor.py           │
│           └─ Copies files from Docker to /tmp/         │
│                                                          │
│  2. Dashboard Opens (index2_1.html)                    │
│     └─ JavaScript runs:                                │
│        ├─ fetch('/tmp/ml_analysis_summary.json')       │
│        │  └─ Get: total_revenue, avg_order_value, etc  │
│        │                                                │
│        ├─ <img src="/tmp/ml_analysis_results.png">     │
│        │  └─ Display: Chart from Spark                │
│        │                                                │
│        └─ populateDashboard(data)                      │
│           └─ Update stat cards                         │
│                                                          │
│  3. Result                                              │
│     └─ Beautiful dashboard with REAL data! ✓           │
└──────────────────────────────────────────────────────────┘
```

---

## 📊 JSON Structure

**File:** `/tmp/ml_analysis_summary.json`

```json
{
    "total_records": 797885,
    "total_revenue": 21416076.50,
    "avg_order_value": 26.84,
    "num_countries": 38,
    "num_products": 4000,
    "best_model_r2": 0.824,
    "top_countries": [...],
    "top_products": [...]
}
```

---

## ⚙️ Configuration

**Location:** Inside `<script>` tag in index2_1.html

```javascript
const CONFIG = {
    dataFile: '/tmp/ml_analysis_summary.json',  // Change this to use different JSON
    imageFile: '/tmp/ml_analysis_results.png',  // Change this for different image
    maxRetries: 5,                               // Increase for more retries
    retryDelay: 2000                            // Increase to wait longer between retries
};
```

---

## 🔍 What Gets Auto-Updated?

### Stat Cards (Dashboard Page)
- 💰 Total Revenue → `data.total_revenue`
- 🛒 Avg Order Value → `data.avg_order_value`
- 🧠 Best Model R² → `data.best_model_r2`
- 📈 Total Records → `data.total_records`

### Chart Images (All 7 Pages)
- ✅ Dashboard Tổng quan
- ✅ Phân cụm Khách hàng
- ✅ Dự đoán Doanh thu
- ✅ Phân loại Sản phẩm
- ✅ Phân tích Nâng cao (2 pages)

---

## 🛠️ Retry Logic

### What Happens?
```
Time 0s:  Fetch JSON → ❌ Not found (404)
          └─ Retry 1/5 scheduled
          
Time 2s:  Retry 1/5 → ❌ Not found
          └─ Retry 2/5 scheduled
          
Time 4s:  Retry 2/5 → ❌ Not found
          └─ Retry 3/5 scheduled
          
Time 6s:  Retry 3/5 → ✅ Success!
          └─ Load data & populate dashboard
```

### Why?
Sometimes extraction takes a moment. Dashboard waits automatically instead of showing error.

---

## 🎯 Use Cases

### ✅ Case 1: Spark Finishes Quickly
```
1. Click "Run Analysis"
2. Wait 1-2 seconds
3. Dashboard opens with data ✓
```

### ✅ Case 2: Spark Takes Longer
```
1. Click "Run Analysis"
2. Docker extraction in progress
3. Dashboard opens and retries...
4. After Spark finishes, data appears ✓
```

### ✅ Case 3: Data Already Exists
```
1. Previous Spark analysis ran before
2. Click "Run Analysis"
3. Dashboard opens immediately with data ✓
```

---

## 🐛 Common Issues

### Issue: "⏳ Chưa có dữ liệu" (Placeholder shows)

**Cause:** Spark analysis hasn't run yet

**Fix:**
1. Go to Spark Runner Tab
2. Click "Run Spark Job"
3. Wait for completion
4. Then click "Run Analysis" in ML Analytics Tab

---

### Issue: Stat cards show "..."

**Cause:** JSON file not found (Spark didn't run)

**Fix:**
```
1. Run Spark first (Spark Runner Tab)
2. Then "Run Analysis" (ML Analytics Tab)
3. Refresh browser if needed (Ctrl+R)
```

---

### Issue: Chart image doesn't appear

**Cause:** PNG file not generated yet

**Fix:**
```
1. Make sure Spark job completed
2. Check ML Analytics logs
3. Refresh dashboard (Ctrl+R)
```

---

## 📂 Related Files

| File | Purpose |
|------|---------|
| `index2_1.html` | Dashboard (updated with auto-load) |
| `/tmp/ml_analysis_summary.json` | Data file (created by Spark) |
| `/tmp/ml_analysis_results.png` | Chart image (created by Spark) |
| `docker_results_extractor.py` | Copies data from Docker |
| `ml_analytics_tab.py` | UI that calls extraction |

---

## 📋 Checklist Before Using

- ✅ index2_1.html exists in workspace root
- ✅ Spark Docker containers running
- ✅ ml_analytics_tab.py has extraction code
- ✅ Browser allows local file access (file:// protocol)

---

## 🚀 Quick Start

```
1. Open GUI Application (main.py)
2. Spark Runner Tab → Run Spark Job
3. ML Analytics Tab → Click "Run Analysis"
4. index2_1.html opens in browser
5. Dashboard shows real data! ✓
```

---

## 🎓 Key Points

| What | Details |
|------|---------|
| **Data Source** | Spark analysis in Docker |
| **Data Location** | `/tmp/` on host machine |
| **Auto-Load** | JavaScript fetch when page opens |
| **Update Trigger** | Each time "Run Analysis" is clicked |
| **Fallback** | Placeholder if data not ready |
| **Retry** | 5 attempts, 2 second delay |

---

## 📞 Support

### Console Logging
Open browser DevTools (F12) to see:
```
[INFO] Dashboard Initialized
[INFO] Bắt đầu tải dữ liệu với auto-retry...
[OK] Dữ liệu tải thành công
[SUCCESS] Dashboard rendered successfully
```

### Files to Check
```powershell
# Check if JSON exists
ls "C:\tmp\ml_analysis_summary.json"

# Check if PNG exists  
ls "C:\tmp\ml_analysis_results.png"

# View JSON content
cat "C:\tmp\ml_analysis_summary.json"
```

---

## ✨ Summary

✅ **Auto-loads real data** from Spark  
✅ **No manual data entry** needed  
✅ **All 7 pages populated** with charts  
✅ **Smart retry logic** if data not ready  
✅ **Beautiful, professional UI** with Vietnamese  

**Now every Spark analysis automatically updates the dashboard!** 🎉

---

**Quick Links:**
- Full Guide: `DASHBOARD_AUTO_LOAD_GUIDE.md`
- Test Page: `DASHBOARD_AUTO_LOAD_TEST.html`
- Integration Details: `DASHBOARD_INTEGRATION_SUMMARY.md`
