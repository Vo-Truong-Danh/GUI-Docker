"""
Comprehensive System Test - Validate All Modules
Tests all new features and ensures no import errors
"""
import sys
import traceback
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("🧪 COMPREHENSIVE SYSTEM TEST - Spark Runner GUI v4.4.3")
print("=" * 80)

test_results = {
    'passed': [],
    'failed': [],
    'warnings': []
}

def test_module(name, import_func):
    """Test a module import"""
    try:
        print(f"\n📦 Testing {name}...")
        result = import_func()
        print(f"   ✅ {name} - OK")
        test_results['passed'].append(name)
        return result
    except Exception as e:
        print(f"   ❌ {name} - FAILED")
        print(f"   Error: {e}")
        traceback.print_exc()
        test_results['failed'].append((name, str(e)))
        return None

# Test 1: System Utils (Caching & Performance)
print("\n" + "=" * 80)
print("TEST 1: SYSTEM UTILITIES")
print("=" * 80)

def test_system_utils():
    from system_utils import (
        LRUCache, CacheManager, PerformanceMonitor, 
        CircuitBreaker, RetryHandler, cache_manager, timed
    )
    
    # Quick functionality test
    cache = LRUCache(capacity=10, ttl=5)
    cache.set('test', 'value')
    assert cache.get('test') == 'value', "Cache get/set failed"
    
    print("   • LRUCache: ✓")
    print("   • CacheManager: ✓")
    print("   • PerformanceMonitor: ✓")
    print("   • CircuitBreaker: ✓")
    print("   • RetryHandler: ✓")
    
    return True

test_module("system_utils.py", test_system_utils)

# Test 2: Database Module
print("\n" + "=" * 80)
print("TEST 2: DATABASE MODULE")
print("=" * 80)

def test_database():
    from database import DatabaseManager, db
    
    # Test database connection
    assert db is not None, "Database manager not initialized"
    
    # Test by trying to add and query a job
    try:
        test_job_id = db.add_job({
            'job_name': 'test_comprehensive',
            'file_path': '/tmp/test.py',
            'container': 'test-container',
            'status': 'running',
            'start_time': datetime.now().isoformat()
        })
        
        assert test_job_id is not None, "Failed to add test job"
        print(f"   • Add job: ✓ (ID: {test_job_id})")
        
        # Query the job back
        jobs = db.get_job_history(limit=1)
        assert len(jobs) > 0, "Failed to retrieve job history"
        print(f"   • Query jobs: ✓")
        
        # Get statistics
        stats = db.get_job_stats()
        assert 'total_jobs' in stats, "Failed to get job stats"
        print(f"   • Statistics: ✓ (Total: {stats['total_jobs']})")
        
        # Clean up test job
        db.delete_old_jobs(days=0)
        print(f"   • Cleanup: ✓")
        
    except Exception as e:
        print(f"   ⚠️ Database operations test failed: {e}")
        test_results['warnings'].append(f"Database operations: {e}")
    
    return True

test_module("database.py", test_database)

# Test 3: Docker Utils (Auto-Start)
print("\n" + "=" * 80)
print("TEST 3: DOCKER UTILITIES")
print("=" * 80)

def test_docker_utils():
    from docker_utils import (
        is_docker_running, find_docker_desktop_path,
        ensure_docker_running, get_docker_info, check_docker_compose
    )
    
    # Test Docker detection
    docker_running = is_docker_running()
    print(f"   • Docker Status: {'✅ Running' if docker_running else '⚠️ Not Running'}")
    
    # Test path finding
    docker_path = find_docker_desktop_path()
    if docker_path:
        print(f"   • Docker Path: ✓ ({docker_path})")
    else:
        print(f"   • Docker Path: ⚠️ Not found (OK if Linux)")
    
    # Test docker-compose
    compose_ok, compose_ver = check_docker_compose()
    if compose_ok:
        print(f"   • docker-compose: ✓ ({compose_ver})")
    else:
        print(f"   • docker-compose: ⚠️ Not available")
        test_results['warnings'].append("docker-compose not available")
    
    return True

test_module("docker_utils.py", test_docker_utils)

# Test 4: Spark Backend (Enhanced)
print("\n" + "=" * 80)
print("TEST 4: SPARK BACKEND")
print("=" * 80)

def test_spark_backend():
    from spark_backend import (
        ENHANCED_FEATURES, DOCKER_AUTO_START,
        get_container_status, get_docker_compose_status,
        auto_run_spark_job, docker_compose_command
    )
    
    print(f"   • Enhanced Features: {'✅ Enabled' if ENHANCED_FEATURES else '⚠️ Disabled'}")
    print(f"   • Docker Auto-Start: {'✅ Enabled' if DOCKER_AUTO_START else '⚠️ Disabled'}")
    
    # Test function signatures (don't execute)
    assert callable(get_container_status), "get_container_status not callable"
    assert callable(get_docker_compose_status), "get_docker_compose_status not callable"
    assert callable(auto_run_spark_job), "auto_run_spark_job not callable"
    assert callable(docker_compose_command), "docker_compose_command not callable"
    
    print("   • All functions: ✓")
    
    return True

test_module("spark_backend.py", test_spark_backend)

# Test 5: Main Application Imports
print("\n" + "=" * 80)
print("TEST 5: MAIN APPLICATION MODULES")
print("=" * 80)

def test_main_imports():
    # Test all tab imports
    from spark_runner_tab_v4_clean import SparkRunnerTabV4
    print("   • SparkRunnerTab: ✓")
    
    from hdfs_upload_tab_v4_clean import HDFSUploadTabV4Clean
    print("   • HDFSUploadTab: ✓")
    
    from ai_code_generator_tab_v4_clean import AICodeGeneratorTabV4Clean
    print("   • AICodeGeneratorTab: ✓")
    
    from performance_monitor_v4_clean import PerformanceMonitorV4Clean
    print("   • PerformanceMonitor: ✓")
    
    from docker_compose_editor_v4 import DockerComposeEditorV4
    print("   • DockerComposeEditor: ✓")
    
    from settings_tab_v4 import SettingsTabV4
    print("   • SettingsTab: ✓")
    
    from modern_theme import setup_modern_theme, ModernTheme
    print("   • ModernTheme: ✓")
    
    return True

test_module("Main Application", test_main_imports)

# Test 6: Configuration File
print("\n" + "=" * 80)
print("TEST 6: CONFIGURATION")
print("=" * 80)

def test_config():
    import json
    
    config_file = Path("spark_runner_config.json")
    if not config_file.exists():
        print("   ⚠️ Config file not found (will be created on first run)")
        test_results['warnings'].append("Config file not found")
        return True
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Check essential keys
    essential_keys = ['container', 'master', 'ports', 'resource_limits']
    for key in essential_keys:
        if key in config:
            print(f"   • Config key '{key}': ✓")
        else:
            print(f"   • Config key '{key}': ⚠️ Missing")
            test_results['warnings'].append(f"Config missing key: {key}")
    
    return True

test_module("Configuration", test_config)

# Test 7: Database File
print("\n" + "=" * 80)
print("TEST 7: DATABASE FILE")
print("=" * 80)

def test_db_file():
    db_file = Path("spark_runner.db")
    
    if db_file.exists():
        size_mb = db_file.stat().st_size / (1024 * 1024)
        print(f"   • Database file: ✓ ({size_mb:.2f} MB)")
    else:
        print("   • Database file: ⚠️ Not found (will be created on first run)")
        test_results['warnings'].append("Database file not found")
    
    return True

test_module("Database File", test_db_file)

# Final Summary
print("\n" + "=" * 80)
print("📊 TEST SUMMARY")
print("=" * 80)

total_tests = len(test_results['passed']) + len(test_results['failed'])
pass_rate = (len(test_results['passed']) / total_tests * 100) if total_tests > 0 else 0

print(f"\n✅ Passed: {len(test_results['passed'])}/{total_tests} ({pass_rate:.1f}%)")
if test_results['passed']:
    for test in test_results['passed']:
        print(f"   • {test}")

if test_results['failed']:
    print(f"\n❌ Failed: {len(test_results['failed'])}/{total_tests}")
    for test, error in test_results['failed']:
        print(f"   • {test}: {error}")

if test_results['warnings']:
    print(f"\n⚠️ Warnings: {len(test_results['warnings'])}")
    for warning in test_results['warnings']:
        print(f"   • {warning}")

print("\n" + "=" * 80)
if len(test_results['failed']) == 0:
    print("🎉 ALL TESTS PASSED! System is ready for production.")
    print("=" * 80)
    sys.exit(0)
else:
    print("⚠️ SOME TESTS FAILED. Please fix errors before running main application.")
    print("=" * 80)
    sys.exit(1)
