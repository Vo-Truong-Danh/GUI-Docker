# 📋 Hướng Dẫn Copy ML Analysis Results

## 🎯 Mục Đích
Copy các file kết quả phân tích ML (images + JSON) từ `tmp` folder sang `dist` folder để có thể view được trên dashboard.

## ⚠️ Vấn Đề Hiện Tại
- `code7.py` tạo kết quả ở thư mục `tmp`
- File `unified_dashboard.html` cần đọc file `tmp/ml_analysis_summary.json`
- Khi copy code sang `dist`, nếu không copy folder `tmp` thì dashboard không view được dữ liệu

## 🚀 Giải Pháp

### **Option 1: Dùng PowerShell Script (Recommended)**
```powershell
.\copy_results.ps1
```

**Advantages:**
- ✅ Detailed output với statistics
- ✅ Validate files trước/sau copy
- ✅ Show size of files
- ✅ Error handling

**Output:**
```
[1/3] Analyzing tmp folder...
   📊 PNG files found: 6
   📋 JSON files found: 1
   💾 Total size: 45.23 MB

[2/3] Copying to dist folder...
   ✓ Copy completed successfully!

[3/3] Verifying files...
   ✓ PNG files in dist: 6
   ✓ JSON files in dist: 1
```

---

### **Option 2: Dùng Batch File (Windows)**
```cmd
copy_results.bat
```

**Advantages:**
- ✅ Simple và nhanh
- ✅ Không cần PowerShell execution policy
- ✅ Works on older Windows versions

---

### **Option 3: Manual Copy (Windows Explorer)**
1. Mở **File Explorer**
2. Navigate đến project folder
3. **Drag & drop** folder `tmp` vào folder `dist`
4. Replace files if prompted

---

## 📊 Kết Quả Sau Khi Copy

```
dist/
├── SparkRunnerGUI.exe
├── docker-compose.yml
├── spark_runner_config.json
├── unified_dashboard.html
└── tmp/                          ← Copied from root
    ├── ml_result_1_customer_clustering.png
    ├── ml_result_2_regression_analysis.png
    ├── ml_result_3_product_clustering.png
    ├── ml_result_4_comprehensive_dashboard.png
    ├── ml_result_5_advanced_analytics.png
    ├── ml_result_6_trends_comparison.png
    └── ml_analysis_summary.json  ← JSON data for dashboard
```

---

## ✅ Verify Kết Quả

Sau khi copy, kiểm tra:

1. **File JSON có trong dist/tmp không?**
   ```powershell
   Test-Path "dist\tmp\ml_analysis_summary.json"
   ```

2. **Mở dashboard test:**
   - Double-click `dist\unified_dashboard.html`
   - Navigate to "Dữ liệu Khoa học" tab
   - Xem có dữ liệu hiển thị không

3. **Check console:**
   - Press `F12` để mở Developer Tools
   - Xem "Console" tab
   - Không có error liên quan đến JSON fetch

---

## 🔧 Troubleshooting

### ❌ "tmp folder not found"
- **Giải pháp:** Chạy `code7.py` trước
  ```bash
  python code7.py
  ```

### ❌ "dist folder not found"
- **Giải pháp:** Chạy `build.ps1` hoặc `build.bat` trước

### ❌ "Copy failed" hoặc "Permission denied"
- **Giải pháp:** 
  - Close all files in `dist\tmp`
  - Run PowerShell as Administrator
  - Chạy: `.\copy_results.ps1 -Force`

### ❌ Dashboard mở nhưng không thấy dữ liệu
- **Giải pháp:**
  1. Check console (F12 → Console tab)
  2. Verify JSON file tồn tại: `dist\tmp\ml_analysis_summary.json`
  3. Clear browser cache (Ctrl+Shift+Del)
  4. Reload page (F5)

---

## 📝 Tự Động Copy Trong Build Process

Các script build đã được cập nhật:
- ✅ `build.ps1` - Automatically copy `tmp` folder nếu tồn tại
- ✅ `build.bat` - Automatically copy `tmp` folder nếu tồn tại

Nên khi chạy build, nó sẽ tự động copy folder `tmp` sang `dist`.

---

## 🎯 Workflow Đầy Đủ

```
1. Chạy code7.py → tạo tmp/ml_result_*.png + tmp/ml_analysis_summary.json
                ↓
2. Chạy build script → tạo dist/ folder
                ↓
3. Chạy copy_results.ps1 → copy tmp/ → dist/tmp/
                ↓
4. Mở dist/unified_dashboard.html
                ↓
5. Dashboard load JSON từ dist/tmp/ml_analysis_summary.json
                ↓
6. View tất cả ML analysis results ✅
```

---

## 💡 Tips

- **Size không lo:** Toàn bộ kết quả ~50MB là bình thường
- **Reuse:** Sau khi copy, không cần copy lại nếu không thay đổi data
- **Multiple runs:** Chạy lại `code7.py` → `copy_results.ps1` để update results

---

## 📞 Support

Nếu gặp vấn đề:
1. Check error message carefully
2. Verify paths trong error
3. Check file permissions
4. Run PowerShell as Administrator
