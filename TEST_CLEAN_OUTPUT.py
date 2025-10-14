#!/usr/bin/env python3
"""
Test: Remove stats footer from generated code
"""

print("=" * 70)
print("TEST: Clean Code Output (No Stats)")
print("=" * 70)

# Simulate generated output with stats
sample_output = """from pyspark.sql import SparkSession

# Initialize SparkSession
spark = SparkSession.builder \\
    .appName("CountSnape") \\
    .getOrCreate()

# HDFS file path
hdfs_file_path = "hdfs://namenode:8020/input/harrypotter.txt"

# Read the HDFS file into an RDD of lines
lines_rdd = spark.read.text(hdfs_file_path).rdd.map(lambda r: r[0])

# FlatMap lines to words, filter for 'Snape', and count
snape_count = lines_rdd.flatMap(lambda line: line.replace('.', ' ').replace(',', ' ').split()) \\
                       .filter(lambda word: word == "Snape") \\
                       .count()

# Print the result
print(f"Số lượng từ 'Snape': {snape_count}")

# Stop SparkSession
spark.stop()

======================================================================
⏱️  Time: 9.08s | 🎯 Quality: 54% | 💰 Cost: $0.0000
🤖 Provider: google_gemini_25_flash
======================================================================"""

print("\n📋 BEFORE (with stats):")
print("-" * 70)
print(sample_output)
print(f"\nLength: {len(sample_output)} chars")
print(f"Has stats: {'⏱️' in sample_output}")

# Method to remove stats
def remove_stats(text):
    """Remove stats footer"""
    if '=' * 70 in text:
        return text.split('=' * 70)[0].strip()
    return text.strip()

clean_code = remove_stats(sample_output)

print("\n📋 AFTER (stats removed):")
print("-" * 70)
print(clean_code)
print(f"\nLength: {len(clean_code)} chars")
print(f"Has stats: {'⏱️' in clean_code}")

print("\n✅ TEST RESULT:")
if '⏱️' not in clean_code and 'spark.stop()' in clean_code:
    print("  ✅ PASSED: Stats removed, code intact")
else:
    print("  ❌ FAILED")

print("\n" + "=" * 70)
print("🎯 Expected Behavior:")
print("=" * 70)
print("""
1. GUI displays code + stats (for info)
2. Copy button → Clipboard gets ONLY code (no stats)
3. Save button → File contains ONLY code (no stats)
4. Run button → Executes ONLY code (no stats)

Result: User sees stats but they don't copy/save them!
""")

print("=" * 70)
