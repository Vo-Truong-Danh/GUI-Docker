# 🚀 ML Analytics Tab - Quick Start Guide

## What Was Fixed

### ❌ Problem 1: "Analysis data not found" Error
**Root Cause**: Analysis script was being created but NOT actually executed.

**Solution**: 
- ✅ Changed from simulated execution to real `subprocess.run()` 
- ✅ Added fallback mechanism that checks `/tmp/` for output files
- ✅ Auto-copies files from `/tmp/` if needed

### ❌ Problem 2: No way to use custom ML scripts
**Root Cause**: Program only used default `code7.py`

**Solution**:
- ✅ Added "🐍 ML Script (.py):" field in GUI
- ✅ Added "📁 Browse" button to select custom Python scripts
- ✅ Script automatically gets required variables injected

---

## How to Use the Fixed Version

### Step 1: Open the App
```powershell
cd "d:\BaiTapSinhVien\TH BigData\GUI-Docker\run_spark_gui"
python main.py
```

### Step 2: Go to "ML Analytics" Tab

### Step 3: Select Input CSV File
Click "📁 Browse" next to "Input CSV File" and select your data file.

### Step 4: (Optional) Select Custom ML Script
**Option A: Use default (code7.py)**
- Leave "🐍 ML Script (.py):" as "code7.py"
- Click "▶ Run Analysis"

**Option B: Use custom script**
- Click "📁 Browse" next to "🐍 ML Script (.py):"
- Select your `.py` file
- Click "▶ Run Analysis"

### Step 5: Watch the Execution
The console will show:
```
✍️ Script created: C:\Users\...\temp_ml_analysis.py
🚀 Executing PySpark job...
[1/4] Setting up Spark...
[2/4] Loading data...
✅ Loaded 500,000 records
[3/4] Running analysis...
✅ Processed 450,000 clean records
✅ Total Revenue: $12,345,678.90
[4/4] Creating visualizations...
✅ Chart saved: /tmp/ml_analysis_results.png
✅ Summary saved: /tmp/ml_analysis_summary.json
✅ ANALYSIS COMPLETED SUCCESSFULLY!
```

### Step 6: View the Results
- Results appear in the "📊 Analysis Results" section
- Click "🌐 Open HTML Dashboard" to open interactive visualization in your browser

---

## What the Program Does Now

### Real Execution
✅ **Actually runs** PySpark and ML algorithms  
✅ Shows **real output** in the console  
✅ **Doesn't fake it** anymore  

### Smart File Handling
✅ Checks **output directory** for results  
✅ **Falls back to `/tmp/`** if needed  
✅ **Auto-copies files** when found in fallback location  
✅ **No more "Analysis data not found" errors**  

### Custom Scripts
✅ **Browse and select** any Python ML script  
✅ Script gets **INPUT_FILE** and **OUTPUT_DIR** automatically injected  
✅ Perfect for testing different analysis approaches  

### Better Logging
✅ **Real-time output** from Spark execution  
✅ **Error messages** shown when things go wrong  
✅ **Progress updates** as analysis runs  

---

## Example: Using a Custom ML Script

### 1. Create custom script (e.g., `my_analysis.py`)
```python
# Optional - these get injected automatically if missing:
# INPUT_FILE = 'input.csv'
# OUTPUT_DIR = '/tmp/'

from pyspark.sql import SparkSession
import json

spark = SparkSession.builder.appName("MyAnalysis").getOrCreate()
df = spark.read.csv(INPUT_FILE, header=True, inferSchema=True)

# Your custom analysis logic here...
results = {
    'total_records': df.count(),
    'custom_metric': 123.45
}

with open(OUTPUT_DIR + '/ml_analysis_summary.json', 'w') as f:
    json.dump(results, f)

spark.stop()
```

### 2. In ML Analytics Tab
- Set "Input CSV File" to your data file
- Click "📁 Browse" next to "🐍 ML Script (.py):"
- Select `my_analysis.py`
- Click "▶ Run Analysis"

### 3. Check Results
- Script runs with your custom analysis
- Results appear in the console and results panel
- Dashboard shows your custom results

---

## Troubleshooting

### Problem: "Script execution failed with code 1"
**Solution**: 
- Check your script for Python errors
- Ensure PySpark is installed: `pip install pyspark`
- Look at the error message in the console

### Problem: "Results file not found"
**Solution**:
- This should NOT happen now with the fallback mechanism
- Check that your script creates `/tmp/ml_analysis_summary.json`
- Verify output directory has write permissions

### Problem: "Analysis is taking too long"
**Solution**:
- Analysis has a 10-minute timeout
- Check your data file size (large files take longer)
- Monitor memory usage in Task Manager

### Problem: Dashboard shows old results
**Solution**:
- Refresh browser (F5 or Ctrl+R)
- Clear browser cache
- Make sure new analysis actually completed

---

## File Locations

| File | Purpose | Location |
|------|---------|----------|
| Input CSV | Your data to analyze | Anywhere (you select it) |
| Output JSON | Analysis results | User-selected output dir or `/tmp/` |
| Output PNG | Charts/graphs | User-selected output dir or `/tmp/` |
| ML Script | Python analysis code | You select it or use default code7.py |
| Dashboard HTML | Interactive visualization | `d:\BaiTapSinhVien\TH BigData\GUI-Docker\run_spark_gui\ml_analytics_dashboard.html` |

---

## Key Improvements Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Execution** | Simulated (fake) | Real subprocess execution |
| **File Output** | ❌ Not created | ✅ Always created |
| **Custom Scripts** | ❌ Not supported | ✅ Full support with Browse button |
| **Error Messages** | Generic | ✅ Detailed with location hints |
| **Fallback Files** | ❌ No fallback | ✅ Checks `/tmp/` automatically |
| **Logging** | Generic messages | ✅ Real Spark output line-by-line |
| **Timeout** | None (could hang forever) | ✅ 10-minute timeout |

---

## Need Help?

### Check the Logs
All execution details are shown in the console. Look for:
- ❌ Error messages (red)
- ⚠️ Warnings (yellow)  
- ✅ Success messages (green)
- ℹ️ Info messages (blue)

### Common Patterns
- `✍️ Script created:` - Script file was created successfully
- `🚀 Executing PySpark job...` - Script execution started
- `✅ Output file:` - Results file was found
- `ℹ️ Found data in /tmp/` - Using fallback mechanism

---

**Version**: 2.0 (with bug fixes and custom script support)  
**Last Updated**: 2024  
**Status**: ✅ Ready to use
