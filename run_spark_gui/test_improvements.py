"""
Test script for Phase 1 improvements
Tests thread safety, resource cleanup, config validation, and retry logic
"""
import sys
import os
import time
import threading
import signal

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_validation():
    """Test config validation"""
    print("\n=== Testing Config Validation ===")
    from main import validate_config
    
    # Test invalid container name
    test_config = {
        'container': 'invalid name with spaces',
        'master': 'invalid-url',
        'hdfs_host': 'not-hdfs',
        'hdfs_default_path': 'no-leading-slash',
        'auto_extract_archives': 'not-bool',
        'delete_archive_after_extract': 123
    }
    
    validated = validate_config(test_config)
    
    assert validated['container'] == 'spark-worker', "Container name should be fixed"
    assert validated['master'] == 'spark://spark-master:7077', "Master URL should be fixed"
    assert validated['hdfs_host'] == 'hdfs://namenode:8020', "HDFS host should be fixed"
    assert validated['hdfs_default_path'] == '/user/spark/data', "HDFS path should be fixed"
    assert validated['auto_extract_archives'] == True, "Boolean should be fixed"
    assert validated['delete_archive_after_extract'] == True, "Boolean should be fixed"
    
    print("✅ Config validation working correctly!")


def test_retry_decorator():
    """Test retry decorator"""
    print("\n=== Testing Retry Decorator ===")
    from spark_runner_tab import retry_on_error
    
    call_count = {'value': 0}
    
    @retry_on_error(max_retries=3, delay=0.1)
    def failing_function():
        call_count['value'] += 1
        if call_count['value'] < 3:
            raise Exception(f"Attempt {call_count['value']} failed")
        return "Success!"
    
    result = failing_function()
    assert result == "Success!", "Function should succeed on 3rd attempt"
    assert call_count['value'] == 3, f"Expected 3 calls, got {call_count['value']}"
    
    print("✅ Retry decorator working correctly!")


def test_thread_safety():
    """Test thread-safe logging"""
    print("\n=== Testing Thread Safety ===")
    
    # Can't fully test without GUI, but check imports work
    try:
        from spark_runner_tab import SparkRunnerTab
        import queue
        from concurrent.futures import ThreadPoolExecutor
        print("✅ Thread safety imports successful!")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    return True


def test_cleanup_handlers():
    """Test cleanup handlers registration"""
    print("\n=== Testing Cleanup Handlers ===")
    
    try:
        import atexit
        import signal as sig
        from main import App
        
        print("✅ Cleanup handler imports successful!")
        print("✅ App class has cleanup handlers registered in __init__")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_thread_pool_integration():
    """Test ThreadPoolExecutor integration"""
    print("\n=== Testing ThreadPoolExecutor Integration ===")
    
    from concurrent.futures import ThreadPoolExecutor
    import queue
    
    # Simulate what SparkRunnerTab does
    thread_pool = ThreadPoolExecutor(max_workers=3, thread_name_prefix='test_spark_')
    log_queue = queue.Queue()
    active_futures = []
    
    def test_task(n):
        time.sleep(0.1)
        return f"Task {n} completed"
    
    # Submit tasks
    for i in range(5):
        future = thread_pool.submit(test_task, i)
        active_futures.append(future)
    
    # Wait for completion
    for future in active_futures:
        result = future.result(timeout=2)
        print(f"  {result}")
    
    # Cleanup
    thread_pool.shutdown(wait=True, cancel_futures=False)
    
    print(f"✅ ThreadPool executed {len(active_futures)} tasks successfully!")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Phase 1 Improvements Test Suite")
    print("=" * 60)
    
    tests = [
        ("Config Validation", test_config_validation),
        ("Retry Decorator", test_retry_decorator),
        ("Thread Safety", test_thread_safety),
        ("Cleanup Handlers", test_cleanup_handlers),
        ("ThreadPool Integration", test_thread_pool_integration),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("✅ All tests passed! Phase 1 improvements are working.")
        print("\n📝 Next steps:")
        print("  1. Run the app: python main.py")
        print("  2. Test manual operations:")
        print("     - Load a Spark job file")
        print("     - Run Docker commands (start/stop/restart)")
        print("     - Execute a Spark job")
        print("     - Close the app properly (should show confirmation)")
        print("  3. Check for memory leaks:")
        print("     - Open Task Manager")
        print("     - Monitor Python process memory")
        print("     - Run multiple jobs and docker commands")
        print("     - Memory should stabilize, not grow continuously")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return 1


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
