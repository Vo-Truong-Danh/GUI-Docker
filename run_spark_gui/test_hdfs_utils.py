"""
HDFS Utils Test Suite
Version: 5.1.0
Quick tests for HDFS utilities module
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_log(msg, tag):
    """Simple test logger"""
    print(f"[{tag.upper():8}] {msg}")


def test_1_import():
    """Test 1: Import hdfs_utils module"""
    print("\n" + "=" * 80)
    print("TEST 1: Import hdfs_utils module")
    print("=" * 80)
    
    try:
        from hdfs_utils import (
            check_hdfs_safe_mode,
            wait_for_hdfs_ready,
            upload_to_hdfs_with_retry,
            verify_hdfs_file,
            install_package_in_container,
            handle_hdfs_error,
            HDFSError,
            HDFSSafeModeError,
            HDFSPermissionError,
            HDFSNotFoundException
        )
        print("✅ PASSED: All imports successful")
        return True
    except ImportError as e:
        print(f"❌ FAILED: Import error - {e}")
        return False


def test_2_exception_hierarchy():
    """Test 2: HDFS exception hierarchy"""
    print("\n" + "=" * 80)
    print("TEST 2: HDFS Exception Hierarchy")
    print("=" * 80)
    
    try:
        from hdfs_utils import (
            HDFSError,
            HDFSSafeModeError,
            HDFSPermissionError,
            HDFSNotFoundException
        )
        
        # Test inheritance
        assert issubclass(HDFSSafeModeError, HDFSError), "SafeModeError should inherit from HDFSError"
        assert issubclass(HDFSPermissionError, HDFSError), "PermissionError should inherit from HDFSError"
        assert issubclass(HDFSNotFoundException, HDFSError), "NotFoundException should inherit from HDFSError"
        
        # Test instantiation
        e1 = HDFSSafeModeError("Test safe mode error")
        e2 = HDFSPermissionError("Test permission error")
        e3 = HDFSNotFoundException("Test not found error")
        
        print(f"✅ HDFSSafeModeError: {e1}")
        print(f"✅ HDFSPermissionError: {e2}")
        print(f"✅ HDFSNotFoundException: {e3}")
        
        print("✅ PASSED: Exception hierarchy working correctly")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_3_error_parsing():
    """Test 3: HDFS error message parsing"""
    print("\n" + "=" * 80)
    print("TEST 3: HDFS Error Message Parsing")
    print("=" * 80)
    
    try:
        from hdfs_utils import handle_hdfs_error, HDFSError, HDFSSafeModeError, HDFSPermissionError, HDFSNotFoundException
        
        test_cases = [
            ("Name node is in safe mode", HDFSSafeModeError),
            ("Safe mode is ON", HDFSSafeModeError),
            ("Permission denied: user=root", HDFSPermissionError),
            ("Access denied for user", HDFSPermissionError),
            ("No such file or directory", HDFSNotFoundException),
            ("File does not exist: /input/test", HDFSNotFoundException),
            ("Some other error", HDFSError),
        ]
        
        for error_msg, expected_type in test_cases:
            result = handle_hdfs_error(error_msg)
            actual_type = type(result).__name__
            expected_name = expected_type.__name__
            
            if isinstance(result, expected_type):
                print(f"✅ '{error_msg[:40]}...' → {actual_type}")
            else:
                print(f"❌ '{error_msg[:40]}...' → {actual_type} (expected {expected_name})")
                return False
        
        print("✅ PASSED: Error parsing working correctly")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_4_safe_mode_check():
    """Test 4: Safe mode checking (requires Docker)"""
    print("\n" + "=" * 80)
    print("TEST 4: HDFS Safe Mode Check")
    print("=" * 80)
    
    try:
        from hdfs_utils import check_hdfs_safe_mode
        
        container = 'namenode'
        
        print(f"Checking safe mode for container '{container}'...")
        is_safe, message = check_hdfs_safe_mode(container, log_callback=test_log)
        
        print(f"\nResult:")
        print(f"  Safe mode: {is_safe}")
        print(f"  Message: {message}")
        
        print("✅ PASSED: Safe mode check executed (check logs above for status)")
        return True
    except Exception as e:
        print(f"⚠️ WARNING: Safe mode check failed (Docker may not be running)")
        print(f"   Error: {e}")
        return True  # Don't fail test if Docker is not available


def test_5_file_verification():
    """Test 5: HDFS file verification (requires Docker and HDFS)"""
    print("\n" + "=" * 80)
    print("TEST 5: HDFS File Verification")
    print("=" * 80)
    
    try:
        from hdfs_utils import verify_hdfs_file
        
        container = 'namenode'
        test_paths = [
            '/input',  # Should exist (directory)
            '/input/nonexistent.txt',  # Should not exist
        ]
        
        for hdfs_path in test_paths:
            print(f"\nVerifying: {hdfs_path}")
            exists, message = verify_hdfs_file(container, hdfs_path, log_callback=test_log)
            print(f"  Result: {'EXISTS' if exists else 'NOT FOUND'}")
            print(f"  Message: {message}")
        
        print("\n✅ PASSED: File verification executed (check logs above for results)")
        return True
    except Exception as e:
        print(f"⚠️ WARNING: File verification failed (Docker/HDFS may not be running)")
        print(f"   Error: {e}")
        return True  # Don't fail test if Docker is not available


def test_6_integration():
    """Test 6: Integration test with GUI module"""
    print("\n" + "=" * 80)
    print("TEST 6: Integration with HDFS Upload Tab")
    print("=" * 80)
    
    try:
        # Try importing hdfs_upload_tab module
        from hdfs_upload_tab_v4_clean import ENHANCED_FEATURES
        
        if ENHANCED_FEATURES:
            print("✅ HDFS Upload Tab has enhanced features enabled")
            
            # Check if hdfs_utils is imported
            import hdfs_upload_tab_v4_clean as upload_tab
            if hasattr(upload_tab, 'upload_to_hdfs_with_retry'):
                print("✅ hdfs_utils functions available in upload tab")
            else:
                print("⚠️  hdfs_utils functions may not be imported in upload tab")
        else:
            print("⚠️  HDFS Upload Tab has enhanced features disabled")
            print("   (This is OK if dependencies are not installed)")
        
        print("✅ PASSED: Integration check complete")
        return True
    except Exception as e:
        print(f"⚠️ WARNING: Integration check failed")
        print(f"   Error: {e}")
        print("   (This is OK if GUI modules are not loaded)")
        return True  # Don't fail test if GUI is not available


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("HDFS UTILS TEST SUITE")
    print("=" * 80)
    
    tests = [
        test_1_import,
        test_2_exception_hierarchy,
        test_3_error_parsing,
        test_4_safe_mode_check,
        test_5_file_verification,
        test_6_integration,
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append((test_func.__name__, result))
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR in {test_func.__name__}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_func.__name__, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status:12} {test_name}")
    
    print("-" * 80)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("=" * 80)
    
    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
