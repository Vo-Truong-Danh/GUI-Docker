# 🚀 Quy Trình Chạy & Copy Kết Quả ML

## 📝 Tóm Tắt Nhanh

```
Step 1: python code7.py              → Tạo tmp/ml_result_*.png + tmp/ml_analysis_summary.json
        ↓
Step 2: .\copy_results.ps1 (or .bat) → Copy tmp/ → dist/tmp/
        ↓
Step 3: Mở dist/unified_dashboard.html → View toàn bộ kết quả ✅
```

---

## ✅ Hướng Dẫn Chi Tiết

### **Bước 1: Chạy Phân Tích ML**

```bash
cd d:\BaiTapSinhVien\TH BigData\GUI-Docker
python code7.py
```

**Kết quả tạo ra:**
```
tmp/
├── ml_result_1_customer_clustering.png          (6.5 MB)
├── ml_result_2_regression_analysis.png          (7.2 MB)
├── ml_result_3_product_clustering.png           (8.1 MB)
├── ml_result_4_comprehensive_dashboard.png      (9.3 MB)
├── ml_result_5_advanced_analytics.png           (8.5 MB)
├── ml_result_6_trends_comparison.png            (6.8 MB)
└── ml_analysis_summary.json                     (2.5 KB) ← QUAN TRỌNG!
```

**Dấu hiệu thành công:**
- ✓ Thấy dòng `[7/6] Tạo file tổng kết JSON cho Dashboard...`
- ✓ Thấy dòng `✅ Đã lưu: .../ml_analysis_summary.json`
- ✓ Không có lỗi trong console

---

### **Bước 2: Copy Kết Quả sang `dist`**

#### **Cách 1: PowerShell (Recommended) ⭐**

```powershell
# Mở PowerShell
# Right-click → "Open in Terminal"
# Hoặc: Win + X → Windows PowerShell

# Chạy script
.\copy_results.ps1
```

**Output:**
```
========================================
   Copy ML Analysis Results
========================================

[1/3] Analyzing tmp folder...
   📊 PNG files found: 6
   📋 JSON files found: 1
   💾 Total size: 46.40 MB

[2/3] Copying to dist folder...
   ✓ Copy completed successfully!

[3/3] Verifying files...
   ✓ PNG files in dist: 6
   ✓ JSON files in dist: 1

   JSON files:
      • ml_analysis_summary.json

========================================
   ✅ COPY SUCCESSFUL!
========================================

📂 Files copied to: dist\tmp\

Next steps:
   1. Open: dist\unified_dashboard.html
   2. The dashboard will automatically load the JSON data
   3. All ML visualizations will be displayed
```

---

#### **Cách 2: Command Prompt (CMD)**

```cmd
# Mở CMD
# Right-click → "Open in Terminal"
# Hoặc: Win + R → cmd

# Chạy script
copy_results.bat
```

**Output:**
```
[1/3] Analyzing tmp folder...
   PNG files found: 6
   JSON files found: 1
   Files ready to copy

[2/3] Copying to dist folder...
   Copying tmp folder to dist...
   Copy completed successfully!

[3/3] Verifying files...
   PNG files in dist: 6
   JSON files in dist: 1

========================================
   COPY SUCCESSFUL!
========================================

Files copied to: dist\tmp\

Next steps:
   1. Open: dist\unified_dashboard.html
   2. The dashboard will automatically load the JSON data
   3. All ML visualizations will be displayed
```

---

#### **Cách 3: Manual Copy (Windows Explorer)**

1. **Mở File Explorer**
2. **Navigate** đến project folder
3. **Tìm folder `tmp`** (chứa 6 PNG + 1 JSON)
4. **Tìm folder `dist`**
5. **Kéo `tmp` vào `dist`** (Drag & Drop)
6. Click **"Replace"** nếu có prompt
7. **Done!** ✅

---

### **Bước 3: Xem Dashboard**

1. **Mở file:** `dist/unified_dashboard.html`
   - Double-click hoặc
   - Right-click → Open with → Browser

2. **Wait for loading:**
   - Dashboard sẽ tự động fetch `tmp/ml_analysis_summary.json`
   - 2-3 giây tải dữ liệu

3. **Xem các tab:**
   - 📊 **Dashboard Tổng quan** → Metrics + comprehensive_dashboard.png
   - 📋 **Dữ liệu Khoa học** → Bảng chi tiết từ JSON
   - 👥 **Phân cụm Khách hàng** → customer_clustering.png
   - 📈 **Dự đoán Doanh thu** → regression_analysis.png
   - 📦 **Phân loại Sản phẩm** → product_clustering.png
   - 🔍 **Phân tích Nâng cao** → advanced_analytics.png + trends_comparison.png

---

## 🔍 Verify Kết Quả

### **Check 1: File JSON tồn tại trong dist**
```powershell
# PowerShell
Test-Path "dist\tmp\ml_analysis_summary.json"
# Output: True (tốt) hoặc False (lỗi)

# CMD
if exist dist\tmp\ml_analysis_summary.json echo OK
```

### **Check 2: Xem nội dung JSON**
```powershell
# PowerShell
Get-Content "dist\tmp\ml_analysis_summary.json" | ConvertFrom-Json | Format-Table

# CMD
type dist\tmp\ml_analysis_summary.json
```

### **Check 3: Console Log**
- Mở dashboard → Press `F12`
- Tab **Console**
- Tìm dòng: `[OK] Cập nhật: ...`
- Không có dòng lỗi như `404 not found`

---

## ⚠️ Troubleshooting

### **❌ "tmp folder not found"**
```
Error: tmp folder not found!
Please run code7.py first to generate ML analysis results
```

**Giải pháp:**
```bash
# Chạy code7.py
python code7.py

# Verify
dir tmp
```

---

### **❌ "dist folder not found"**
```
Error: dist folder not found!
Please build the application first with build.bat or build.ps1
```

**Giải pháp:**
```bash
# Chạy build
.\build.ps1
# Hoặc
build.bat
```

---

### **❌ "Copy failed" hoặc "Permission denied"**

**Giải pháp:**
1. **Close all files** - Không được có file mở từ dist\tmp
2. **Run as Administrator:**
   ```powershell
   # Right-click PowerShell → Run as Administrator
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   .\copy_results.ps1
   ```
3. **Hoặc dùng CMD** (không cần admin):
   ```cmd
   copy_results.bat
   ```

---

### **❌ Dashboard mở nhưng không thấy dữ liệu**

**Kiểm tra:**
1. **Developer Tools (F12) → Console:**
   - Có error liên quan JSON không?
   - Error code 404? (file không tìm thấy)
   - Error code 403? (permission denied)

2. **File tồn tại chưa?**
   ```powershell
   ls dist\tmp\
   # Cần có: ml_analysis_summary.json + ml_result_*.png
   ```

3. **Clear cache + Reload:**
   - Ctrl + Shift + Del (Clear Browser Cache)
   - Reload: Ctrl + F5 (hard refresh)

4. **Check file size:**
   ```powershell
   (Get-ChildItem "dist\tmp\ml_analysis_summary.json").Length
   # Cần > 0 bytes
   ```

---

## 📊 Kết Quả Cuối Cùng

Sau khi copy thành công, folder structure sẽ như sau:

```
dist/
├── SparkRunnerGUI.exe
├── docker-compose.yml
├── spark_runner_config.json
├── unified_dashboard.html           ← Mở file này
├── README.md (nếu copy)
├── QUICKSTART.txt (nếu build tạo)
└── tmp/                             ← Folder được copy
    ├── ml_result_1_customer_clustering.png
    ├── ml_result_2_regression_analysis.png
    ├── ml_result_3_product_clustering.png
    ├── ml_result_4_comprehensive_dashboard.png
    ├── ml_result_5_advanced_analytics.png
    ├── ml_result_6_trends_comparison.png
    └── ml_analysis_summary.json     ← JSON data
```

---

## 💡 Pro Tips

| Tip | Mô Tả |
|-----|-------|
| 🔄 **Rerun** | Chạy `code7.py` → `copy_results.ps1` → Reload dashboard |
| 🖥️ **Server** | Đặt `dist` folder trên web server → Share URL |
| 📦 **ZIP** | Compress `dist` folder → Share như file |
| 🚀 **CI/CD** | Auto-run `copy_results.ps1` trong build pipeline |

---

## 🎯 Checklist

Trước khi kết thúc:

- [ ] Code7.py chạy xong (check console: ✅ SUCCESS)
- [ ] 6 PNG files tạo trong tmp/
- [ ] ml_analysis_summary.json tạo trong tmp/
- [ ] copy_results script chạy xong (check console: ✅ COPY SUCCESSFUL)
- [ ] 6 PNG + 1 JSON visible trong dist/tmp/
- [ ] Dashboard mở được (dist/unified_dashboard.html)
- [ ] Dữ liệu hiển thị (check Science Data tab)

---

## 📞 Liên Hệ

Nếu gặp vấn đề:
1. Check log console chi tiết
2. Verify file paths là absolute paths
3. Check permissions của folder
4. Try administrator mode
5. Xem `COPY_RESULTS_GUIDE.md` chi tiết hơn
