"""
Test script to diagnose slow tab loading
"""
import sys
import time

print("=" * 60)
print("Testing V4 Clean Tabs Import Speed")
print("=" * 60)

# Test 1: Spark Runner Tab
print("\n[1/4] Testing Spark Runner Tab V4...")
start = time.time()
try:
    from spark_runner_tab_v4_clean import SparkRunnerTabV4
    elapsed = time.time() - start
    print(f"✅ Spark Runner Tab loaded in {elapsed:.2f}s")
except Exception as e:
    elapsed = time.time() - start
    print(f"❌ Spark Runner Tab failed after {elapsed:.2f}s: {e}")
    import traceback
    traceback.print_exc()

# Test 2: HDFS Upload Tab
print("\n[2/4] Testing HDFS Upload Tab V4...")
start = time.time()
try:
    from hdfs_upload_tab_v4_clean import HDFSUploadTabV4Clean
    elapsed = time.time() - start
    print(f"✅ HDFS Upload Tab loaded in {elapsed:.2f}s")
except Exception as e:
    elapsed = time.time() - start
    print(f"❌ HDFS Upload Tab failed after {elapsed:.2f}s: {e}")
    import traceback
    traceback.print_exc()

# Test 3: AI Code Generator Tab
print("\n[3/4] Testing AI Code Generator Tab V4...")
start = time.time()
try:
    from ai_code_generator_tab_v4_clean import AICodeGeneratorTabV4Clean
    elapsed = time.time() - start
    print(f"✅ AI Code Generator Tab loaded in {elapsed:.2f}s")
except Exception as e:
    elapsed = time.time() - start
    print(f"❌ AI Code Generator Tab failed after {elapsed:.2f}s: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Performance Monitor Tab
print("\n[4/4] Testing Performance Monitor Tab V4...")
start = time.time()
try:
    from performance_monitor_v4_clean import PerformanceMonitorV4Clean
    elapsed = time.time() - start
    print(f"✅ Performance Monitor Tab loaded in {elapsed:.2f}s")
except Exception as e:
    elapsed = time.time() - start
    print(f"❌ Performance Monitor Tab failed after {elapsed:.2f}s: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Import test completed!")
print("=" * 60)
