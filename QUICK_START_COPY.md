# 🚀 QUICK REFERENCE CARD

## One-Minute Summary

**Problem:** Dashboard JSON file not copied ❌  
**Solution:** Copy scripts + auto-copy in build ✅

---

## ⚡ Get Started in 3 Steps

```bash
# 1. Generate
python code7.py

# 2. Copy (pick one)
.\copy_results.ps1              # PowerShell
# OR
copy_results.bat                # CMD
# OR drag folder manually

# 3. View
# Double-click: dist\unified_dashboard.html
```

**Time:** 5 minutes ⏱️

---

## 📚 Documentation Map

```
I want to...                        → Read this file

Run the analysis & copy files       → RUN_AND_COPY.md ⭐
Fix an error                        → COPY_RESULTS_GUIDE.md
Understand the fix                  → COPY_FIX_SUMMARY.md
Find the right file                 → COPY_FILE_INDEX.md
See what was done                   → TASK_COMPLETED.md
Quick checklist                     → This file (QUICK_START.md)
```

---

## ✅ Scripts Available

```
copy_results.ps1        ← PowerShell (recommended)
copy_results.bat        ← Batch (simple)
Manual copy             ← Drag & drop in Explorer
```

---

## 🔍 Quick Check

```powershell
# Files copied?
Test-Path "dist\tmp\ml_analysis_summary.json"

# Dashboard works?
# Open: dist\unified_dashboard.html
# Check "Dữ liệu Khoa học" tab
```

---

## 🛠️ If Something Breaks

| Error | Fix |
|-------|-----|
| Script won't run | Try `.bat` instead |
| Permission denied | Run PowerShell as admin |
| No data shown | Press F5 (reload page) |
| File not found | Run `python code7.py` first |

---

## 📋 Files Created

```
✅ copy_results.ps1
✅ copy_results.bat
✅ RUN_AND_COPY.md
✅ COPY_RESULTS_GUIDE.md
✅ COPY_FIX_SUMMARY.md
✅ COPY_FILE_INDEX.md
✅ TASK_COMPLETED.md
✅ FINAL_CHECKLIST.md (this)
```

---

## 🎯 Common Commands

```powershell
# Copy files
.\copy_results.ps1

# Check if JSON exists
Test-Path "dist\tmp\ml_analysis_summary.json"

# Check file size
(Get-ChildItem "dist\tmp\ml_analysis_summary.json").Length

# View JSON
Get-Content "dist\tmp\ml_analysis_summary.json" | ConvertFrom-Json
```

---

## 💡 Pro Tips

✅ Bookmark `RUN_AND_COPY.md` for next time

✅ Build script auto-copies now (less work)

✅ Use PowerShell for detailed output

✅ Press F12 in dashboard to debug

✅ Clear browser cache if data doesn't update

---

## 🔄 Workflow

```
code7.py
    ↓
copy_results script
    ↓
dist/unified_dashboard.html
    ↓
✅ All data visible
```

---

## 📞 Need Help?

1. **Quick help:** `RUN_AND_COPY.md` Quick Start
2. **Detailed help:** `COPY_RESULTS_GUIDE.md`
3. **Understanding:** `COPY_FILE_INDEX.md`
4. **Overview:** `COPY_FIX_SUMMARY.md`

---

**Status:** ✅ Complete  
**Version:** 1.0  
**Date:** 2025-10-25
