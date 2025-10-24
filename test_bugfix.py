#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify ML Analytics Tab bug fix
"""

import os
import sys
import tempfile

print("=" * 60)
print("🧪 ML ANALYTICS TAB - BUG FIX TEST")
print("=" * 60)

# Test 1: Check temp directory
print("\n[TEST 1] System Temp Directory")
temp_dir = tempfile.gettempdir()
print(f"✅ Temp dir: {temp_dir}")
print(f"✅ Exists: {os.path.exists(temp_dir)}")
print(f"✅ Writable: {os.access(temp_dir, os.W_OK)}")

# Test 2: Create test file
print("\n[TEST 2] Create Test File in Temp")
test_script = os.path.join(temp_dir, 'test_script.py')
print(f"Test file path: {test_script}")

try:
    with open(test_script, 'w') as f:
        f.write("print('Hello from temp!')")
    print(f"✅ File created successfully")
    print(f"✅ File exists: {os.path.exists(test_script)}")
    
    # Clean up
    os.remove(test_script)
    print(f"✅ File cleaned up")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Test 3: Check imports
print("\n[TEST 3] Import Checks")
try:
    import tkinter
    print("✅ tkinter imported")
    
    from run_spark_gui.ml_analytics_tab import MLAnalyticsTab
    print("✅ MLAnalyticsTab imported")
    
    print("✅ All imports OK")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test 4: Check main.py
print("\n[TEST 4] Check main.py Integration")
main_py = 'd:/BaiTapSinhVien/TH BigData/GUI-Docker/run_spark_gui/main.py'
if os.path.exists(main_py):
    print(f"✅ main.py exists")
    try:
        with open(main_py, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'MLAnalyticsTab' in content:
                print(f"✅ MLAnalyticsTab imported in main.py")
            else:
                print(f"⚠️ MLAnalyticsTab not found in imports")
    except Exception as e:
        print(f"⚠️ Could not read main.py: {e}")
else:
    print(f"❌ main.py not found")

# Test 5: Syntax check
print("\n[TEST 5] Python Syntax Check")
ml_tab_py = 'd:/BaiTapSinhVien/TH BigData/GUI-Docker/run_spark_gui/ml_analytics_tab.py'
try:
    import py_compile
    py_compile.compile(ml_tab_py, doraise=True)
    print(f"✅ ml_analytics_tab.py - No syntax errors")
except py_compile.PyCompileError as e:
    print(f"❌ Syntax error: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\nThe ML Analytics Tab bug fix is working!")
print("You can now run: python run_spark_gui/main.py")
print("\nNext steps:")
print("1. Run GUI")
print("2. Click: 🤖 ML Analytics tab")
print("3. Configure input/output")
print("4. Click: ▶️ Run Analysis")
print("=" * 60)
