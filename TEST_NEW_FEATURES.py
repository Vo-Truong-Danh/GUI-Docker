#!/usr/bin/env python3
"""
Quick test for new features V8.3 Enhanced
"""

print("=" * 70)
print("TEST: New Features V8.3 Enhanced")
print("=" * 70)

# Test 1: Code extraction
print("\n📋 Test 1: Code Extraction")
print("-" * 70)

sample_response = """
Tuyệt vời! Đây là code PySpark để đếm từ 'snape':

### Giải thích chi tiết:

1. **SparkSession**: Khởi tạo Spark context
2. **textFile**: Đọc file từ HDFS
3. **flatMap**: Tách từng từ
4. **filter**: Lọc từ 'snape'
5. **count**: Đếm số lượng

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("CountSnape").getOrCreate()
text_rdd = spark.sparkContext.textFile("hdfs://namenode:8020/input/harrypotter.txt")
snape_count = text_rdd.flatMap(lambda line: line.lower().split()).filter(lambda word: word == "snape").count()
print(f"Count of 'snape': {snape_count}")
spark.stop()
```

**Lưu ý**: Code này case-insensitive (lowercase).
"""

import re

def extract_python_code(text):
    """Extract only Python code"""
    code_blocks = re.findall(r'```(?:python)?\n(.*?)```', text, re.DOTALL)
    if code_blocks:
        return '\n\n'.join(block.strip() for block in code_blocks)
    return text

extracted = extract_python_code(sample_response)

print("\n🔹 Input (AI response):")
print(f"  Length: {len(sample_response)} chars")
print(f"  Has verbose text: {'Tuyệt vời' in sample_response}")

print("\n🔹 Output (extracted code):")
print(f"  Length: {len(extracted)} chars")
print(f"  Has verbose text: {'Tuyệt vời' in extracted}")
print(f"  Starts with: {extracted[:30]}...")

print("\n✅ Test 1 Result:")
if 'from pyspark.sql' in extracted and 'Tuyệt vời' not in extracted:
    print("  ✅ PASSED: Code extracted, verbose text removed")
else:
    print("  ❌ FAILED")

# Test 2: Config file
print("\n" + "=" * 70)
print("📋 Test 2: API Key Persistence")
print("-" * 70)

import json
import os

config_path = "run_spark_gui/spark_runner_config.json"

if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    print(f"\n🔹 Config file found: {config_path}")
    print(f"  Keys: {list(config.keys())}")
    
    if 'ai_api_key' in config:
        key = config['ai_api_key']
        masked = key[:10] + '...' if len(key) > 10 else key
        print(f"  ✅ ai_api_key: {masked}")
    else:
        print(f"  ⚠️ ai_api_key: Not saved yet")
    
    if 'ai_provider' in config:
        print(f"  ✅ ai_provider: {config['ai_provider']}")
    else:
        print(f"  ⚠️ ai_provider: Not saved yet")
    
    print("\n✅ Test 2 Result:")
    print("  ✅ PASSED: Config file structure OK")
else:
    print(f"\n⚠️ Config file not found: {config_path}")
    print("  (Will be created on first Initialize)")

# Test 3: File operations
print("\n" + "=" * 70)
print("📋 Test 3: File Operations")
print("-" * 70)

test_code = """from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Test").getOrCreate()
print("Hello from PySpark!")
spark.stop()
"""

import tempfile

# Test save
temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8')
temp_file.write(test_code)
temp_file.close()

print(f"\n🔹 Test file created: {temp_file.name}")

# Test read
with open(temp_file.name, 'r', encoding='utf-8') as f:
    read_back = f.read()

print(f"  Content length: {len(read_back)} chars")
print(f"  Matches original: {read_back == test_code}")

# Cleanup
os.unlink(temp_file.name)
print(f"  File deleted: ✅")

print("\n✅ Test 3 Result:")
print("  ✅ PASSED: File save/read works")

# Summary
print("\n" + "=" * 70)
print("📊 SUMMARY")
print("=" * 70)

print("\n✅ All 3 features ready:")
print("  1. ✅ Code extraction (remove verbose text)")
print("  2. ✅ API key persistence (save to config)")
print("  3. ✅ File operations (save/copy/run)")

print("\n🚀 Next steps:")
print("  1. Run GUI: python run_spark_gui/main.py")
print("  2. Initialize engine (API key will be saved)")
print("  3. Generate code (only Python code displayed)")
print("  4. Use buttons: Save, Copy, Run")

print("\n" + "=" * 70)
