# 📑 Hướng Dẫn - Chỉ Mục (Index)

## 🎯 Tôi muốn ... thì xem file nào?

### 🚀 **Chạy Phân Tích & Xem Dashboard**
→ **[RUN_AND_COPY.md](RUN_AND_COPY.md)** ⭐ **RECOMMENDED**
- ✅ Step-by-step guide
- ✅ Tất cả options (PowerShell, Batch, Manual)
- ✅ Detailed output examples
- ✅ Complete workflow

### 🔧 **Troubleshoot Vấn Đề**
→ **[COPY_RESULTS_GUIDE.md](COPY_RESULTS_GUIDE.md)**
- ✅ Common errors + solutions
- ✅ Verification steps
- ✅ Performance tips
- ✅ FAQs

### 📋 **Xem Summary Của Fix**
→ **[COPY_FIX_SUMMARY.md](COPY_FIX_SUMMARY.md)**
- ✅ Vấn đề & giải pháp
- ✅ Files created/modified
- ✅ Verification checklist
- ✅ Feature overview

### 📚 **Tìm Hiểu Kỹ Thuật**
→ **[README.md](README.md)** - ML Analysis Dashboard section
- ✅ Architecture
- ✅ Integration details
- ✅ Links to guides

---

## 🛠️ Scripts Có Sẵn

### **Copy Results - Choose One:**

| Script | OS | Lệnh | Ưu Điểm |
|--------|----|----|---------|
| `copy_results.ps1` | Windows | `.\copy_results.ps1` | 🟦 Detailed output |
| `copy_results.bat` | Windows | `copy_results.bat` | 🟩 Simple, no admin needed |
| Manual | Windows | Drag & drop | 🔵 Easiest |

### **Build Scripts - Updated:**

| Script | Mục Đích |
|--------|----------|
| `build.ps1` | PowerShell build + auto-copy tmp |
| `build.bat` | Batch build + auto-copy tmp |

---

## 📊 Complete File List

### 📖 **Documentation Files**
```
RUN_AND_COPY.md              ← Start here! Full workflow
COPY_RESULTS_GUIDE.md        ← Troubleshooting + detail
COPY_FIX_SUMMARY.md          ← Overview of fix
README.md                    ← Updated with ML section
```

### 🔧 **Script Files**
```
copy_results.ps1             ← PowerShell copy script
copy_results.bat             ← Batch copy script
build.ps1                    ← Updated (auto-copy added)
build.bat                    ← Updated (auto-copy added)
```

### 🌐 **Dashboard Files**
```
unified_dashboard.html       ← Updated (alert box added)
tmp/ml_analysis_summary.json ← JSON data (created by code7.py)
```

### 🐍 **Python Analysis**
```
code7.py                     ← Creates ml_analysis_summary.json
```

---

## ⚡ Quick Start (Fastest Way)

```bash
# 1. Run analysis
python code7.py

# 2. Copy results (pick ONE)
.\copy_results.ps1           # PowerShell (recommended)
# OR
copy_results.bat             # Batch
# OR manually: Drag tmp → dist

# 3. View
# Double-click: dist\unified_dashboard.html
```

**Total time:** ~5 minutes

---

## 🎓 Learning Path

### **Beginner** (Just want to see dashboard)
1. Read: [RUN_AND_COPY.md](RUN_AND_COPY.md) - Section "Quick Start"
2. Run: `python code7.py` + `.\copy_results.ps1`
3. Open: `dist\unified_dashboard.html`

### **Intermediate** (Want to understand process)
1. Read: [COPY_FIX_SUMMARY.md](COPY_FIX_SUMMARY.md)
2. Read: [COPY_RESULTS_GUIDE.md](COPY_RESULTS_GUIDE.md)
3. Try: Different copy methods
4. Verify: Using PowerShell commands

### **Advanced** (Want to customize)
1. Read: [README.md](README.md) - ML section
2. Inspect: `copy_results.ps1` script
3. Modify: Build scripts or dashboard
4. Test: Custom workflows

---

## ✅ Verification Commands

```powershell
# Check JSON file exists
Test-Path "dist\tmp\ml_analysis_summary.json"

# Count PNG files
(Get-ChildItem "dist\tmp\" -Filter *.png).Count

# View JSON data
Get-Content "dist\tmp\ml_analysis_summary.json" | ConvertFrom-Json | Format-Table

# Check folder size
"{0:N2} MB" -f ((Get-ChildItem -Path "dist\tmp\" -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB)
```

---

## 🐛 If Something Goes Wrong

1. **Script won't run?**
   → Try with `.bat` version instead
   → Or run PowerShell as Administrator

2. **Dashboard shows no data?**
   → Check: `dist\tmp\ml_analysis_summary.json` exists
   → Press F12 → Console → Check for errors
   → Clear browser cache + reload

3. **Copy failed?**
   → Close all files in `dist\tmp`
   → Run as Administrator
   → Check disk space

4. **Still stuck?**
   → Read: [COPY_RESULTS_GUIDE.md](COPY_RESULTS_GUIDE.md) Troubleshooting section
   → Or try manual copy (drag & drop)

---

## 📞 File Purpose Summary

| File | Purpose | When to Read |
|------|---------|--------------|
| `RUN_AND_COPY.md` | Full workflow | First time setup |
| `COPY_RESULTS_GUIDE.md` | Detailed guide | When stuck |
| `COPY_FIX_SUMMARY.md` | Overview | Want quick summary |
| `README.md` | Project overview | General info |
| `COPY_FILE_INDEX.md` | This file | Navigation |

---

## 🎯 Use Cases

### **Case 1: "I just want to see the dashboard"**
→ `RUN_AND_COPY.md` Quick Start section

### **Case 2: "I get an error"**
→ `COPY_RESULTS_GUIDE.md` Troubleshooting section

### **Case 3: "How does the copy work?"**
→ `COPY_FIX_SUMMARY.md` + `README.md`

### **Case 4: "I want to integrate this"**
→ `COPY_RESULTS_GUIDE.md` + Inspect scripts

### **Case 5: "I need to share with team"**
→ Share `RUN_AND_COPY.md` link

---

## 🔄 Typical Workflow

```
1. Open: RUN_AND_COPY.md
         ↓
2. Follow: Step 1-3 in "Quick Start"
         ↓
3. Run: python code7.py
         ↓
4. Run: .\copy_results.ps1
         ↓
5. Open: dist\unified_dashboard.html
         ↓
6. View: 6 charts + data table ✅
```

---

## 💡 Pro Tips

✅ **Bookmark:** Bookmark `RUN_AND_COPY.md` for quick reference

✅ **Share:** Share `COPY_RESULTS_GUIDE.md` link when someone asks for help

✅ **Automate:** Build scripts auto-copy now, so less manual work

✅ **Verify:** Use PowerShell commands to verify success

✅ **Debug:** Press F12 in dashboard to check console errors

---

## 🎉 You're All Set!

1. ✅ Copy scripts created
2. ✅ Build scripts updated
3. ✅ Dashboard enhanced
4. ✅ Documentation complete
5. ✅ Troubleshooting guide ready

**Start with:** [RUN_AND_COPY.md](RUN_AND_COPY.md) ⭐

---

**Last Updated:** 2025-10-25  
**Status:** ✅ Complete  
**Version:** 1.0
