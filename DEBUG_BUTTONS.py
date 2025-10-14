#!/usr/bin/env python3
"""
Debug: Check if buttons exist in UI
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'run_spark_gui'))

print("=" * 70)
print("DEBUG: Button Check")
print("=" * 70)

# Check if advanced_ai_tab_v8.py has button code
filepath = "run_spark_gui/advanced_ai_tab_v8.py"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

print("\n🔍 Searching for button definitions...")

buttons = {
    "Copy Code": '📋 Copy Code',
    "Save to File": '💾 Save to File',
    "Run Code": '▶️ Run Code',
    "Clear": '🗑️ Clear'
}

found = {}
for name, text in buttons.items():
    if text in content:
        # Find line number
        for i, line in enumerate(content.split('\n'), 1):
            if text in line and 'text=' in line:
                found[name] = i
                break

print(f"\n✅ Found {len(found)}/{len(buttons)} buttons:")
for name, line in found.items():
    print(f"  ✅ {name:15} at line {line}")

if len(found) < len(buttons):
    print(f"\n❌ Missing buttons:")
    for name in buttons:
        if name not in found:
            print(f"  ❌ {name}")

# Check methods
print("\n🔍 Searching for button methods...")

methods = {
    "_copy_code": "Copy button handler",
    "_save_code": "Save button handler", 
    "_run_code": "Run button handler"
}

for method, desc in methods.items():
    if f"def {method}(" in content:
        print(f"  ✅ {method:20} - {desc}")
    else:
        print(f"  ❌ {method:20} - {desc} MISSING!")

# Check UI structure
print("\n🔍 Checking UI layout...")

if "btn_frame = tk.Frame(output_frame" in content:
    print("  ✅ Button frame created")
    
    if ".pack(side=tk.LEFT" in content:
        print("  ✅ Buttons packed horizontally")
    else:
        print("  ⚠️ Button packing not found")
else:
    print("  ❌ Button frame NOT created")

print("\n" + "=" * 70)
print("📊 RESULT")
print("=" * 70)

if len(found) == 4 and all(m in content for m in [f"def {m}(" for m in methods]):
    print("\n✅ All buttons and methods present in code!")
    print("\n🔧 If buttons not visible in GUI:")
    print("  1. Close GUI completely")
    print("  2. Run: RESTART_GUI_WITH_BUTTONS.bat")
    print("  3. Generate code first")
    print("  4. Check bottom of output area")
    print("  5. Resize window if needed")
else:
    print("\n❌ Missing components in code!")
    print("  Need to re-apply fixes")

print("\n" + "=" * 70)
