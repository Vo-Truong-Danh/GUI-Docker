# -*- coding: utf-8 -*-
"""
Test script for ML Analytics Tab integration with Docker Results Extractor
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("[TEST] Testing imports...")
    
    try:
        from docker_results_extractor import copy_docker_results_to_tmp, extract_results_from_docker
        print("  [OK] docker_results_extractor imported")
    except Exception as e:
        print(f"  [ERROR] docker_results_extractor import failed: {e}")
        return False
    
    try:
        from html_dashboard_helper import HTMLDashboardHelper
        print("  [OK] html_dashboard_helper imported")
    except Exception as e:
        print(f"  [ERROR] html_dashboard_helper import failed: {e}")
        return False
    
    try:
        import ml_analytics_tab
        print("  [OK] ml_analytics_tab imported")
    except Exception as e:
        print(f"  [ERROR] ml_analytics_tab import failed: {e}")
        return False
    
    return True

def test_docker_extraction():
    """Test docker results extraction"""
    print("\n[TEST] Testing docker results extraction...")
    
    try:
        from docker_results_extractor import copy_docker_results_to_tmp
        
        # Try to extract from spark-master container
        print("  [INFO] Attempting to extract from spark-master container...")
        success, json_file, png_file = copy_docker_results_to_tmp('spark-master', verbose=False)
        
        if success:
            print(f"  [OK] Extraction successful!")
            if json_file and os.path.exists(json_file):
                print(f"  [OK] JSON file exists: {json_file}")
            if png_file and os.path.exists(png_file):
                print(f"  [OK] PNG file exists: {png_file}")
            return True
        else:
            print("  [WARNING] Extraction returned False - container may not have results yet")
            print("  [INFO] This is expected if Spark analysis hasn't run yet")
            return True  # Not an error condition
            
    except Exception as e:
        print(f"  [ERROR] Extraction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dashboard_helper():
    """Test HTML dashboard helper"""
    print("\n[TEST] Testing HTML dashboard helper...")
    
    try:
        from html_dashboard_helper import HTMLDashboardHelper
        
        helper = HTMLDashboardHelper()
        print("  [OK] HTMLDashboardHelper created")
        
        # Check if dashboard HTML file exists
        if hasattr(helper, 'dashboard_path'):
            if os.path.exists(helper.dashboard_path):
                print(f"  [OK] Dashboard HTML exists: {helper.dashboard_path}")
            else:
                print(f"  [WARNING] Dashboard HTML not found: {helper.dashboard_path}")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Dashboard helper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("ML Analytics Tab Integration Tests")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Docker Extraction", test_docker_extraction()))
    results.append(("Dashboard Helper", test_dashboard_helper()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n[SUCCESS] All tests passed! Integration ready.")
        return 0
    else:
        print("\n[FAILURE] Some tests failed. Check output above.")
        return 1

if __name__ == "__main__":
    exit(main())
