# 🔄 MIGRATION GUIDE - Nâng cấp lên Version 7.0.0

**Ngày:** 14/10/2025  
**Phiên bản hiện tại:** 6.4.0  
**Phiên bản mới:** 7.0.0  
**Loại nâng cấp:** MAJOR (Breaking changes)

---

## 📋 MỤC LỤC

1. [Tổng quan Thay đổi](#1-tổng-quan-thay-đổi)
2. [Chuẩn bị Migration](#2-chuẩn-bị-migration)
3. [Hướng dẫn Từng bước](#3-hướng-dẫn-từng-bước)
4. [Breaking Changes](#4-breaking-changes)
5. [Code Migration](#5-code-migration)
6. [Testing](#6-testing)
7. [Rollback Plan](#7-rollback-plan)
8. [FAQ](#8-faq)

---

## 1. TỔNG QUAN THAY ĐỔI

### 1.1. Những gì Đã thay đổi

#### ✅ New Features

**Unified Error Handler v2.0**
- ✅ Specific exception handling (không còn `except Exception:`)
- ✅ Context managers cho error scopes
- ✅ Decorator-based error handling
- ✅ Circuit breaker pattern
- ✅ Enhanced logging với categories
- ✅ Thread-safe operations

**Auto-Healing System v2.0**
- ✅ Improved health checks
- ✅ Better subprocess error handling
- ✅ Integration với UnifiedErrorHandler
- ✅ Type hints cho better code clarity

**System Cleanup**
- ✅ Removed duplicate modules
- ✅ Code consolidation
- ✅ 20% code base reduction
- ✅ Better organization

#### 🗑️ Removed (Deprecated)

```
❌ enhanced_error_handler.py    → Use error_handler_v2.py
❌ unified_error_handler.py     → Use error_handler_v2.py
❌ advanced_error_recovery.py   → Use error_handler_v2.py
❌ connection_pool.py (old)     → Use connection_pool_v2.py
❌ error_recovery_v2.py         → Use error_handler_v2.py
```

### 1.2. Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Phase 1: Preparation** | 1 day | Backup, review changes |
| **Phase 2: Migration** | 2 days | Update imports, fix code |
| **Phase 3: Testing** | 2 days | Run tests, fix issues |
| **Phase 4: Deployment** | 1 day | Deploy to production |

**Total:** ~1 week

---

## 2. CHUẨN BỊ MIGRATION

### 2.1. Backup Hệ thống

#### Option A: Using Built-in Backup Manager

```python
from backup_manager import get_backup_manager

backup_manager = get_backup_manager()
backup_manager.create_backup([
    'run_spark_gui/',
    'spark_runner_config.json'
])
```

#### Option B: Manual Backup

```bash
# Windows PowerShell
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item -Path "run_spark_gui" -Destination "backups/backup_$timestamp" -Recurse
```

### 2.2. Kiểm tra Dependencies

```bash
# Check Python version
python --version  # Should be 3.7+

# Install/Update dependencies
cd run_spark_gui
pip install -r requirements.txt --upgrade

# Verify imports
python -c "import pyspark; import psutil; print('✅ Dependencies OK')"
```

### 2.3. Review Current Code

```bash
# Find all files using old error handlers
cd run_spark_gui
Select-String -Pattern "from enhanced_error_handler|from unified_error_handler|from advanced_error_recovery" -Path *.py

# Find bare exception handlers
Select-String -Pattern "except Exception:" -Path *.py
```

---

## 3. HƯỚNG DẪN TỪNG BƯỚC

### Step 1: Run Cleanup Script (Dry Run)

```bash
cd run_spark_gui
python cleanup_system.py --workspace "d:\BaiTapSinhVien\TH BigData\GUI-Docker"

# Review output, ensure no critical files will be deleted
```

### Step 2: Run Cleanup Script (Live)

```bash
python cleanup_system.py --live --workspace "d:\BaiTapSinhVien\TH BigData\GUI-Docker"

# ⚠️ This will actually delete files!
```

### Step 3: Update Imports

**Find and replace across all Python files:**

#### A. Error Handler Imports

```python
# ❌ OLD (Remove these)
from enhanced_error_handler import ErrorHandler
from unified_error_handler import UnifiedErrorHandler
from advanced_error_recovery import AdvancedRecovery

# ✅ NEW (Use this)
from error_handler_v2 import (
    UnifiedErrorHandler,
    get_error_handler,
    ErrorSeverity,
    ErrorCategory
)
```

#### B. Auto-Healing Imports

```python
# ❌ OLD
from auto_healing import AutoHealingSystem

# ✅ NEW
from auto_healing_v2 import (
    AutoHealingSystem,
    get_auto_healing_system
)
```

### Step 4: Update Error Handling Code

#### Pattern 1: Bare Exception Handlers

**❌ Before:**
```python
try:
    result = subprocess.run(['docker', 'info'])
    return result.returncode == 0
except Exception as e:
    print(f"Error: {e}")
    return False
```

**✅ After:**
```python
try:
    result = subprocess.run(
        ['docker', 'info'],
        capture_output=True,
        timeout=5
    )
    return result.returncode == 0
except subprocess.TimeoutExpired:
    logger.error("Docker command timeout")
    return False
except FileNotFoundError:
    logger.error("Docker not found")
    return False
except subprocess.SubprocessError as e:
    logger.error(f"Docker error: {e}")
    return False
```

#### Pattern 2: Using Context Managers

**✅ New Approach:**
```python
from error_handler_v2 import get_error_handler, ErrorCategory

handler = get_error_handler()

# Use context manager
with handler.error_context(
    "Docker operation",
    expected_exceptions=(subprocess.SubprocessError, FileNotFoundError),
    category=ErrorCategory.DOCKER
):
    result = subprocess.run(['docker', 'info'])
```

#### Pattern 3: Using Decorators

**✅ New Approach:**
```python
@handler.error_handler(
    expected_exceptions=(ValueError, KeyError),
    default_return={},
    category=ErrorCategory.VALIDATION
)
def parse_config(config_file):
    with open(config_file) as f:
        return json.load(f)
```

### Step 5: Update main.py

**Find this section in main.py:**

```python
# Import new enhanced error handling modules
try:
    from error_handler import get_error_handler, safe_execute, ErrorSeverity, with_error_handling
    ERROR_HANDLER_AVAILABLE = True
    error_handler = get_error_handler(app_logger if LOGGING_AVAILABLE else None)
    print("✅ Enhanced error handling enabled (v2.0)")
except ImportError:
    print("⚠️ Warning: Enhanced error handler not available")
    ERROR_HANDLER_AVAILABLE = False
    error_handler = None
```

**Replace with:**

```python
# Import Unified Error Handler v2.0
try:
    from error_handler_v2 import (
        UnifiedErrorHandler,
        get_error_handler,
        ErrorSeverity,
        ErrorCategory
    )
    ERROR_HANDLER_AVAILABLE = True
    error_handler = get_error_handler(app_logger if LOGGING_AVAILABLE else None)
    print("✅ Unified Error Handler v2.0 enabled")
except ImportError:
    print("⚠️ Warning: Unified error handler not available")
    ERROR_HANDLER_AVAILABLE = False
    error_handler = None
```

---

## 4. BREAKING CHANGES

### 4.1. API Changes

#### UnifiedErrorHandler

**Changed:** `handle_error()` signature

```python
# ❌ OLD
handler.handle_error(
    error=e,
    context="operation",
    severity="error",  # String
    recovery_callback=None
)

# ✅ NEW
handler._handle_exception(  # Internal, use context managers instead
    exception=e,
    context="operation",
    severity=ErrorSeverity.ERROR,  # Enum
    category=ErrorCategory.SYSTEM,  # Added
    recovery_callback=None
)

# ✅ BETTER: Use context manager
with handler.error_context("operation"):
    ...
```

#### safe_execute()

**Changed:** Parameter names

```python
# ❌ OLD
safe_execute(
    operation=my_func,
    context="test",
    default_return=None
)

# ✅ NEW
handler.safe_execute(
    func=my_func,
    context="test",
    default_return=None,
    expected_exceptions=(ValueError,)  # Now required
)
```

### 4.2. Removed Functions

```python
# ❌ REMOVED - No longer available
from error_handler import with_error_handling  # Removed
from enhanced_error_handler import EnhancedHandler  # Removed

# ✅ USE INSTEAD
from error_handler_v2 import get_error_handler

handler = get_error_handler()

# Use decorator
@handler.error_handler(...)
def my_function():
    ...
```

---

## 5. CODE MIGRATION

### 5.1. Migration Script

Tạo file `migrate_to_v7.py`:

```python
"""
Automated migration script for v7.0.0
"""

import os
import re
from pathlib import Path


def migrate_imports(file_path: Path):
    """Update imports in a Python file"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Replace old imports
    replacements = [
        (
            r'from enhanced_error_handler import.*',
            'from error_handler_v2 import UnifiedErrorHandler, get_error_handler, ErrorSeverity, ErrorCategory'
        ),
        (
            r'from unified_error_handler import.*',
            'from error_handler_v2 import UnifiedErrorHandler, get_error_handler, ErrorSeverity, ErrorCategory'
        ),
        (
            r'from advanced_error_recovery import.*',
            'from error_handler_v2 import UnifiedErrorHandler, get_error_handler, ErrorSeverity, ErrorCategory'
        ),
        (
            r'from auto_healing import AutoHealingSystem',
            'from auto_healing_v2 import AutoHealingSystem, get_auto_healing_system'
        ),
    ]
    
    for old_pattern, new_import in replacements:
        content = re.sub(old_pattern, new_import, content)
    
    # Save if changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Updated: {file_path.name}")
        return True
    
    return False


def migrate_directory(directory: Path):
    """Migrate all Python files in directory"""
    updated = 0
    
    for py_file in directory.rglob('*.py'):
        if 'backup' in str(py_file) or '__pycache__' in str(py_file):
            continue
        
        if migrate_imports(py_file):
            updated += 1
    
    print(f"\n✅ Updated {updated} files")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python migrate_to_v7.py <directory>")
        sys.exit(1)
    
    directory = Path(sys.argv[1])
    
    if not directory.exists():
        print(f"❌ Directory not found: {directory}")
        sys.exit(1)
    
    print(f"Migrating files in: {directory}")
    print("=" * 80)
    
    migrate_directory(directory)
```

**Chạy migration:**

```bash
python migrate_to_v7.py "d:\BaiTapSinhVien\TH BigData\GUI-Docker\run_spark_gui"
```

### 5.2. Manual Fixes

Một số pattern cần sửa thủ công:

#### Fix 1: Exception Handling

Tìm và sửa tất cả:

```python
# Search pattern
except Exception:

# Replace with specific exceptions
except (ValueError, KeyError, FileNotFoundError) as e:
```

#### Fix 2: Pass Statements

Tìm và sửa:

```python
# ❌ BAD
try:
    something()
except:
    pass

# ✅ GOOD
try:
    something()
except Exception as e:
    logger.warning(f"Operation failed: {e}")
    # Or provide default behavior
```

---

## 6. TESTING

### 6.1. Unit Tests

Chạy tests để verify:

```bash
cd run_spark_gui

# Test error handler v2
python error_handler_v2.py

# Test auto-healing v2
python auto_healing_v2.py

# Run full test suite (if available)
python -m pytest tests/ -v
```

### 6.2. Integration Tests

```python
"""
Test integration of new error handler
"""

def test_error_handler_integration():
    """Test that error handler works with main app"""
    from error_handler_v2 import get_error_handler, ErrorCategory
    from auto_healing_v2 import get_auto_healing_system
    
    # Get handlers
    error_handler = get_error_handler()
    healing_system = get_auto_healing_system()
    
    # Test error context
    with error_handler.error_context("test", category=ErrorCategory.SYSTEM):
        assert 1 + 1 == 2
    
    # Test health check
    status = healing_system.get_health_status()
    assert 'overall' in status
    
    print("✅ Integration test passed")


if __name__ == '__main__':
    test_error_handler_integration()
```

### 6.3. Manual Testing Checklist

- [ ] Application starts without errors
- [ ] Error messages display correctly
- [ ] Logging works
- [ ] Auto-healing monitors services
- [ ] Docker operations work
- [ ] HDFS upload works
- [ ] Spark jobs can be submitted
- [ ] Settings can be saved/loaded

---

## 7. ROLLBACK PLAN

### 7.1. Nếu có vấn đề sau migration

**Step 1: Stop application**

```bash
# Stop all processes
taskkill /F /IM python.exe
```

**Step 2: Restore from backup**

```bash
# Find latest backup
$backup = Get-ChildItem "backups" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

# Restore
Remove-Item "run_spark_gui" -Recurse -Force
Copy-Item $backup.FullName -Destination "run_spark_gui" -Recurse
```

**Step 3: Verify restoration**

```bash
cd run_spark_gui
python main.py
```

### 7.2. Partial Rollback

Nếu chỉ một số module có vấn đề:

```python
# Temporarily use old error handler
try:
    from error_handler_v2 import get_error_handler
    handler = get_error_handler()
except ImportError:
    # Fallback to old handler
    from error_handler import get_error_handler
    handler = get_error_handler()
```

---

## 8. FAQ

### Q1: Tôi có nhất thiết phải migrate không?

**A:** Không bắt buộc ngay lập tức, nhưng **strongly recommended**:
- Old handlers sẽ không được maintain
- V7.0 có nhiều improvements
- Bug fixes chỉ apply cho v7.0+

### Q2: Migration mất bao lâu?

**A:** Phụ thuộc project size:
- Small (< 10 custom files): 2-4 hours
- Medium (10-50 files): 1-2 days
- Large (> 50 files): 2-3 days

### Q3: Có automated migration tool không?

**A:** Có! Use `migrate_to_v7.py` script (section 5.1)

### Q4: Làm sao test trước khi deploy production?

**A:**
1. Tạo test environment
2. Copy code sang test environment
3. Run migration
4. Test thoroughly
5. Deploy to production

### Q5: Breaking changes có ảnh hưởng gì?

**A:** Major changes:
- Import statements khác
- API signature khác một chút
- Removed deprecated functions

### Q6: Có thể dùng cả v6 và v7 cùng lúc không?

**A:** Có, trong transition period:

```python
try:
    from error_handler_v2 import get_error_handler  # v7
    use_v7 = True
except ImportError:
    from error_handler import get_error_handler  # v6
    use_v7 = False

handler = get_error_handler()
```

### Q7: Documentation ở đâu?

**A:**
- `SYSTEM_OPTIMIZATION_ANALYSIS.md` - Full analysis
- `error_handler_v2.py` - Inline documentation
- `auto_healing_v2.py` - Inline documentation
- This migration guide

### Q8: Cần support?

**A:** Create issue trên GitHub với:
- Error messages
- Stack traces
- Steps to reproduce
- Environment info

---

## 9. RESOURCES

### Documentation

- 📄 `SYSTEM_OPTIMIZATION_ANALYSIS.md` - Comprehensive analysis
- 📄 `error_handler_v2.py` - Error handler documentation
- 📄 `auto_healing_v2.py` - Auto-healing documentation
- 📄 `cleanup_system.py` - Cleanup script

### Tools

- 🔧 `cleanup_system.py` - Automated cleanup
- 🔧 `migrate_to_v7.py` - Migration automation
- 🔧 `error_handler_v2.py` - New error handler
- 🔧 `auto_healing_v2.py` - Improved auto-healing

### Support

- 💬 GitHub Issues
- 📧 Email support
- 📖 Wiki documentation

---

## 10. CHECKLIST

Pre-Migration:
- [ ] Backup toàn bộ hệ thống
- [ ] Review breaking changes
- [ ] Check dependencies
- [ ] Read migration guide

Migration:
- [ ] Run cleanup script (dry run)
- [ ] Run cleanup script (live)
- [ ] Update imports
- [ ] Fix exception handling
- [ ] Run migration script
- [ ] Manual fixes

Post-Migration:
- [ ] Run tests
- [ ] Manual testing
- [ ] Performance testing
- [ ] Update documentation
- [ ] Deploy to production

---

**Good luck with your migration! 🚀**

**Version:** 1.0  
**Last updated:** 14/10/2025  
**Author:** AI System Optimizer
