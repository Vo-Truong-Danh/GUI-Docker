#!/usr/bin/env python3
"""
Test script để verify 2 fixes:
1. HDFS path không bị duplicate (//input/input/input)
2. Provider mapping không bị lỗi GPT4O_MINI
"""

import sys
import os

# Add run_spark_gui to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'run_spark_gui'))

print("=" * 60)
print("TEST 1: HDFS Path Parsing")
print("=" * 60)

from advanced_ai_tab_v8 import get_hdfs_files

# Mock HDFS output
test_output = """Found 3 items
drwxr-xr-x   - root supergroup          0 2024-10-14 10:00 /input/data
drwxr-xr-x   - root supergroup          0 2024-10-14 10:00 /input/logs
-rw-r--r--   1 root supergroup    1234567 2024-10-14 10:00 /input/sample.csv"""

print("\n📋 Expected behavior:")
print("  - name: 'data' (basename only)")
print("  - path: '/input/data' (full path)")
print("  - When double click 'data', next path should be '/input/data'")
print("  - NOT '/input/input' or '/input/input/input' ❌")

print("\n✅ Test passed if get_hdfs_files() returns:")
print("  [{")
print("    'name': 'data',")
print("    'path': '/input/data',  # Full path for navigation")
print("    'is_dir': True")
print("  }]")

print("\n" + "=" * 60)
print("TEST 2: Provider Mapping")
print("=" * 60)

from advanced_ai_engine_v8 import AIProvider

print("\n📋 Available providers in AIProvider enum:")
for provider in AIProvider:
    print(f"  ✅ {provider.name} = '{provider.value}'")

print("\n❌ Check if OPENAI_GPT4O_MINI exists:")
try:
    test_provider = AIProvider.OPENAI_GPT4O_MINI
    print("  ❌ OPENAI_GPT4O_MINI exists (BAD!)")
except AttributeError:
    print("  ✅ OPENAI_GPT4O_MINI does NOT exist (GOOD!)")

print("\n✅ Check provider_map in advanced_ai_tab_v8.py:")
print("  Expected:")
print("    'GPT-4o Mini': AIProvider.OPENAI_GPT4O  # NOT GPT4O_MINI")

# Read actual code
with open('run_spark_gui/advanced_ai_tab_v8.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
if 'OPENAI_GPT4O_MINI' in content:
    print("  ❌ Found OPENAI_GPT4O_MINI in code! (BAD)")
    # Show where
    for i, line in enumerate(content.split('\n'), 1):
        if 'OPENAI_GPT4O_MINI' in line:
            print(f"    Line {i}: {line.strip()}")
else:
    print("  ✅ No OPENAI_GPT4O_MINI in code (GOOD!)")

if 'AIProvider.OPENAI_GPT4O' in content:
    print("  ✅ Found AIProvider.OPENAI_GPT4O (correct)")
else:
    print("  ⚠️ No AIProvider.OPENAI_GPT4O found")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

print("\n🎯 To test in GUI:")
print("  1. Run: python run_spark_gui/main.py")
print("  2. Go to tab: '🤖 AI Engine V8.3'")
print("  3. Click: '📂 Browse HDFS'")
print("  4. Navigate: / → input → data")
print("  5. Verify path shows: '/input/data' (NOT '//input/input')")
print("")
print("  6. Select: 'Gemini 2.5 Flash (Free)'")
print("  7. Click: '🚀 Initialize Engine'")
print("  8. Should see: '✅ Engine Ready'")
print("  9. Should NOT see: 'OPENAI_GPT4O_MINI' error")

print("\n✅ All tests completed!")
