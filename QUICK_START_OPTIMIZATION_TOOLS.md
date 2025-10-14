# 🚀 Quick Start Guide - System Optimization Tools

## 📋 Tổng Quan

Bộ công cụ tối ưu hóa và cải tiến hệ thống bao gồm 6 tools chính:

1. **comprehensive_system_analysis.py** - Phân tích toàn diện
2. **auto_code_fixer.py** - Tự động sửa lỗi
3. **enhanced_error_handler_v3.py** - Error handling nâng cao
4. **dependency_optimizer_v2.py** - Tối ưu dependencies
5. **realtime_monitoring_dashboard.py** - Dashboard giám sát
6. **master_optimization.py** - Menu tổng hợp

---

## ⚡ Quick Start

### Option 1: Sử dụng Master Menu (Khuyến nghị)

```bash
cd run_spark_gui
python master_optimization.py
```

Menu sẽ hiển thị:
```
1. 🚀 Run Full Optimization (All steps)
2. 🔍 System Analysis Only
3. 🔧 Auto Code Fixer Only
4. 📦 Dependency Optimizer Only
5. 📊 Launch Monitoring Dashboard
6. 📋 View Previous Reports
7. ❌ Exit
```

### Option 2: Chạy từng tool riêng lẻ

#### 1. Phân tích hệ thống
```bash
python comprehensive_system_analysis.py
```
**Output**: 
- `system_analysis_report_*.json`
- `system_analysis_report_*_summary.txt`

#### 2. Tự động sửa lỗi (có backup)
```bash
python auto_code_fixer.py
```
**Output**:
- `auto_fix_report_*.json`
- `backups/auto_fix_*/` (backup files)

#### 3. Tối ưu dependencies
```bash
python dependency_optimizer_v2.py
```
**Output**:
- `dependency_analysis_report.json`
- `dependency_analysis_summary.txt`
- `requirements_optimized.txt` (nếu chọn optimize)

#### 4. Launch monitoring dashboard
```bash
python realtime_monitoring_dashboard.py
```
GUI dashboard sẽ mở với real-time monitoring.

---

## 🔧 Sử Dụng Nâng Cao

### Integrate Error Handler vào Code

#### Basic Usage:
```python
from enhanced_error_handler_v3 import get_error_handler, ErrorSeverity, ErrorCategory

handler = get_error_handler()

# Decorator
@handler.decorator(severity=ErrorSeverity.HIGH, category=ErrorCategory.DATABASE)
def database_operation():
    # Your code
    pass

# Safe execute
result = handler.safe_execute(
    risky_function,
    default="fallback",
    severity=ErrorSeverity.MEDIUM
)
```

#### With Context:
```python
from enhanced_error_handler_v3 import ErrorContext

context = ErrorContext(
    operation="Loading config",
    details={'file': 'config.yaml', 'user': 'admin'}
)

try:
    # Your code
    config = load_config()
except Exception as e:
    handler.handle_error(
        e,
        context=context,
        severity=ErrorSeverity.HIGH,
        attempt_recovery=True
    )
```

#### Custom Recovery:
```python
def custom_recovery(error, context):
    # Recovery logic
    if isinstance(error, FileNotFoundError):
        # Try alternative location
        return alternative_file_path
    return None

handler.register_recovery_strategy(FileNotFoundError, custom_recovery)
```

### Monitoring Dashboard trong Code

```python
from realtime_monitoring_dashboard import RealTimeMonitoringDashboard

# Standalone
dashboard = RealTimeMonitoringDashboard()
dashboard.run()

# Or as child window
import tkinter as tk
root = tk.Tk()
dashboard = RealTimeMonitoringDashboard(parent=root)
# dashboard.window sẽ là Toplevel
```

---

## 📊 Understanding Reports

### System Analysis Report

**File**: `system_analysis_report_*.json`

Structure:
```json
{
  "timestamp": "2025-10-14T13:16:02",
  "workspace": "...",
  "summary": {
    "total_issues": 809,
    "by_severity": {
      "critical": 2,
      "high": 16,
      "medium": 15,
      "low": 776
    }
  },
  "detailed_issues": {
    "logic_errors": {...},
    "security_issues": {...},
    "error_handling": {...}
  },
  "recommendations": [...]
}
```

### Auto-Fix Report

**File**: `auto_fix_report_*.json`

Structure:
```json
{
  "timestamp": "...",
  "fixes_applied": [
    {
      "file": "path/to/file.py",
      "line": 42,
      "type": "bare_except_fixed",
      "old": "except:",
      "new": "except Exception as e:"
    }
  ],
  "files_modified": [...],
  "summary": {
    "total_fixes": 50,
    "files_modified": 10
  }
}
```

---

## 🎯 Recommended Workflow

### First Time Setup:

```bash
# 1. Run analysis
python master_optimization.py
# Choose option 2 (System Analysis Only)

# 2. Review reports
# Read: system_analysis_report_*_summary.txt

# 3. Run auto-fixer (creates backup)
python master_optimization.py
# Choose option 3 (Auto Code Fixer)

# 4. Review changes
# Check: backups/auto_fix_*/

# 5. Optimize dependencies
python master_optimization.py
# Choose option 4 (Dependency Optimizer)
```

### Daily Use:

```bash
# Monitor system
python master_optimization.py
# Choose option 5 (Launch Dashboard)

# Set thresholds:
# - CPU: 80%
# - Memory: 85%
# - Disk: 90%

# Start monitoring and watch for alerts
```

---

## ⚙️ Configuration

### Error Handler Thresholds

Edit trong code hoặc tạo config file:

```python
# In your initialization code
from enhanced_error_handler_v3 import get_error_handler

handler = get_error_handler()
handler.max_errors_stored = 500  # Default: 200
```

### Monitoring Dashboard Thresholds

GUI-based configuration trong Alerts tab:
- CPU %: 0-100
- Memory %: 0-100
- Disk %: 0-100

### Dependency Optimizer

Edit package mappings nếu cần:

```python
# In dependency_optimizer_v2.py
package_import_map = {
    'pyyaml': 'yaml',
    'pillow': 'PIL',
    # Add your custom mappings
}
```

---

## 🐛 Troubleshooting

### Issue: "Module not found"
**Solution**: Ensure you're in the correct directory:
```bash
cd run_spark_gui
python master_optimization.py
```

### Issue: "Permission denied" khi auto-fix
**Solution**: Run với appropriate permissions hoặc check file permissions

### Issue: Dashboard không mở
**Solution**: 
1. Check tkinter installation: `python -c "import tkinter"`
2. Install nếu missing: `pip install tk`

### Issue: Too many false positives trong analysis
**Solution**: Review và adjust thresholds trong analyzer code

---

## 📁 File Structure

```
run_spark_gui/
├── comprehensive_system_analysis.py    # Analyzer
├── auto_code_fixer.py                  # Auto-fixer
├── enhanced_error_handler_v3.py        # Error handler
├── dependency_optimizer_v2.py          # Dep optimizer
├── realtime_monitoring_dashboard.py    # Dashboard
├── master_optimization.py              # Master menu
├── backups/                            # Auto-generated
│   └── auto_fix_*/                     # Backup files
├── logs/                               # Log files
│   └── errors_*.log
└── Reports (auto-generated):
    ├── system_analysis_report_*.json
    ├── system_analysis_report_*_summary.txt
    ├── auto_fix_report_*.json
    ├── dependency_analysis_report.json
    └── monitoring_report_*.json
```

---

## 🔍 Understanding Issues

### Critical Issues (🔴):
- **Syntax errors**: Fix immediately
- **Security vulnerabilities**: Hardcoded credentials, eval/exec
- **Action**: Fix trước khi deploy

### High Issues (🟠):
- **Bare except clauses**: `except:` without specific exception
- **Command injection risks**: subprocess shell=True
- **Action**: Fix trong sprint hiện tại

### Medium Issues (🟡):
- **Silent exceptions**: `except: pass` without logging
- **Long functions**: > 50 lines
- **Action**: Refactor khi có thời gian

### Low Issues (🟢):
- **Print statements**: Should use logging
- **TODO comments**: Track và address
- **Action**: Cleanup định kỳ

---

## 🎓 Best Practices

### 1. Always Backup
```bash
# Auto-fixer creates backups automatically
# But you can also manual backup:
cp -r run_spark_gui run_spark_gui.backup
```

### 2. Review Before Apply
```bash
# After running auto-fixer:
diff backups/auto_fix_*/file.py file.py
```

### 3. Incremental Fixes
- Fix critical issues first
- Then high priority
- Then medium/low

### 4. Monitor After Changes
```bash
# After applying fixes:
python realtime_monitoring_dashboard.py
# Monitor for regressions
```

### 5. Regular Analysis
```bash
# Weekly or bi-weekly:
python comprehensive_system_analysis.py
# Track improvement over time
```

---

## 📈 Metrics to Track

### Code Quality:
- Total issues count (should decrease)
- Critical/High issues (should be 0)
- Quality score (should increase)

### System Health:
- CPU usage (should be stable)
- Memory usage (no leaks)
- Error rate (should decrease)

### Dependencies:
- Unused packages (should be removed)
- Missing packages (should be added)
- Version pinning (should be complete)

---

## 💡 Tips & Tricks

### Tip 1: Export Reports Regularly
```bash
# In monitoring dashboard:
Click "📊 Export Report"
# Creates JSON file với all metrics
```

### Tip 2: Use Filtering in Process Monitor
```
# In dashboard Process tab:
Filter: "python"
# Shows only Python processes
```

### Tip 3: Custom Error Categories
```python
from enhanced_error_handler_v3 import ErrorCategory
from enum import Enum

class CustomCategory(Enum):
    CUSTOM_1 = "custom_1"
    CUSTOM_2 = "custom_2"

# Extend ErrorCategory if needed
```

### Tip 4: Automated Reports
```bash
# Add to cron/scheduled task:
0 0 * * 0 cd /path/to/project && python comprehensive_system_analysis.py
# Runs weekly analysis
```

---

## 🚀 Next Steps

1. **Immediate**:
   - [ ] Run system analysis
   - [ ] Review critical issues
   - [ ] Apply auto-fixes

2. **This Week**:
   - [ ] Integrate error handler
   - [ ] Optimize dependencies
   - [ ] Set up monitoring

3. **This Month**:
   - [ ] Address all TODO comments
   - [ ] Refactor long functions
   - [ ] Improve test coverage

---

## 📞 Support & Resources

### Documentation:
- Full report: `OPTIMIZATION_REPORT.md`
- This guide: `QUICK_START_OPTIMIZATION_TOOLS.md`

### Generated Reports:
- Analysis: `system_analysis_report_*_summary.txt`
- Fixes: `auto_fix_report_*_summary.txt`
- Dependencies: `dependency_analysis_summary.txt`

### Logs:
- Error logs: `logs/errors_*.log`
- System logs: `logs/system_*.log`

---

## ✅ Checklist

- [ ] Đã chạy system analysis
- [ ] Đã review critical issues
- [ ] Đã backup code trước khi auto-fix
- [ ] Đã apply auto-fixes và test
- [ ] Đã optimize dependencies
- [ ] Đã set up monitoring dashboard
- [ ] Đã integrate error handler vào code
- [ ] Đã set alert thresholds
- [ ] Đã export baseline metrics

---

**🎉 Happy Optimizing! 🎉**

Generated by GitHub Copilot | Version 1.0.0 | October 14, 2025
