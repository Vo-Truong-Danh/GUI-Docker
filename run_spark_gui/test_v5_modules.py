"""
Comprehensive Test Suite for Version 5.0.0 Modules
Tests: logging_config.py, validation.py, health_check.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("🧪 VERSION 5.0.0 - MODULE TEST SUITE")
print("=" * 80)

# Test counters
tests_passed = 0
tests_failed = 0
tests_total = 0

def test_module(name, test_func):
    """Run a test and track results"""
    global tests_passed, tests_failed, tests_total
    tests_total += 1
    
    print(f"\n📦 Testing {name}...")
    try:
        test_func()
        print(f"   ✅ {name} - PASSED")
        tests_passed += 1
        return True
    except Exception as e:
        print(f"   ❌ {name} - FAILED: {e}")
        tests_failed += 1
        return False


# ============================================================================
# TEST 1: Logging Module
# ============================================================================

def test_logging_module():
    """Test logging_config.py"""
    from logging_config import get_logger, logger_manager
    import logging
    
    # Test logger creation
    logger = get_logger('test_module', level=logging.DEBUG)
    assert logger is not None, "Logger should not be None"
    
    # Test logging messages
    logger.debug("Test debug message")
    logger.info("Test info message")
    logger.warning("Test warning message")
    logger.error("Test error message")
    
    # Test log directory exists
    log_dir = logger_manager.log_dir
    assert log_dir.exists(), f"Log directory should exist: {log_dir}"
    
    # Test log file created
    log_files = list(log_dir.glob("test_module.log*"))
    assert len(log_files) > 0, "Log file should be created"
    
    print(f"      ✓ Log directory: {log_dir}")
    print(f"      ✓ Log files created: {len(log_files)}")


# ============================================================================
# TEST 2: Validation Module
# ============================================================================

def test_validation_module():
    """Test validation.py"""
    from validation import Validator, ConfigValidator
    
    # Test container name validation
    valid, error = Validator.is_valid_container_name('spark-worker')
    assert valid, "Valid container name should pass"
    
    valid, error = Validator.is_valid_container_name('-invalid')
    assert not valid, "Invalid container name should fail"
    
    # Test Spark master URL validation
    valid, error = Validator.is_valid_spark_master('spark://master:7077')
    assert valid, "Valid Spark URL should pass"
    
    valid, error = Validator.is_valid_spark_master('local[*]')
    assert valid, "local[*] should be valid"
    
    valid, error = Validator.is_valid_spark_master('invalid')
    assert not valid, "Invalid Spark URL should fail"
    
    # Test HDFS path validation
    valid, error = Validator.is_valid_hdfs_path('/user/spark/data')
    assert valid, "Valid HDFS path should pass"
    
    valid, error = Validator.is_valid_hdfs_path('hdfs://namenode:8020/data')
    assert valid, "Valid HDFS URL should pass"
    
    # Test port validation
    valid, error = Validator.is_valid_port(8080)
    assert valid, "Valid port should pass"
    
    valid, error = Validator.is_valid_port(99999)
    assert not valid, "Invalid port should fail"
    
    # Test config validation
    valid_config = {
        'container': 'spark-worker',
        'master': 'spark://master:7077',
        'hdfs_host': 'hdfs://namenode:8020',
        'hdfs_default_path': '/user/spark/data'
    }
    
    is_valid, errors = ConfigValidator.validate_config(valid_config)
    assert is_valid, "Valid config should pass"
    
    invalid_config = {
        'container': '-invalid',
        'master': 'bad-url',
        'hdfs_host': 'not-hdfs',
        'hdfs_default_path': 'no-slash'
    }
    
    is_valid, errors = ConfigValidator.validate_config(invalid_config)
    assert not is_valid, "Invalid config should fail"
    assert len(errors) > 0, "Should have validation errors"
    
    # Test auto-fix
    fixed = ConfigValidator.fix_config(invalid_config)
    assert fixed['hdfs_default_path'].startswith('/'), "Path should be auto-fixed"
    
    print(f"      ✓ Container validation working")
    print(f"      ✓ Spark master validation working")
    print(f"      ✓ HDFS path validation working")
    print(f"      ✓ Config validation working")
    print(f"      ✓ Auto-fix working")


# ============================================================================
# TEST 3: Health Check Module
# ============================================================================

def test_health_check_module():
    """Test health_check.py"""
    from health_check import health_checker, HealthStatus
    
    # Test Docker daemon check
    result = health_checker.check_docker_daemon()
    assert result is not None, "Should return result"
    assert result.component == 'Docker Daemon', "Component name should match"
    print(f"      ✓ Docker daemon check: {result.status}")
    
    # Test container check (may not exist, that's OK)
    result = health_checker.check_container('test-container')
    assert result is not None, "Should return result"
    print(f"      ✓ Container check: {result.status}")
    
    # Test network check
    result = health_checker.check_network_connectivity('localhost', 80)
    assert result is not None, "Should return result"
    print(f"      ✓ Network check: {result.status}")
    
    # Test docker-compose file check
    compose_file = Path(__file__).parent / 'docker-compose.yml'
    if compose_file.exists():
        result = health_checker.check_docker_compose_file(str(compose_file))
        assert result is not None, "Should return result"
        print(f"      ✓ Compose file check: {result.status}")
    else:
        print(f"      ⚠ Compose file not found, skipping test")
    
    # Test overall health
    status, message = health_checker.get_overall_health()
    assert status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED, 
                      HealthStatus.UNHEALTHY, HealthStatus.UNKNOWN]
    print(f"      ✓ Overall health: {status}")


# ============================================================================
# TEST 4: Integration Test
# ============================================================================

def test_integration():
    """Test modules working together"""
    from logging_config import get_logger
    from validation import ConfigValidator
    from health_check import health_checker
    import logging
    
    # Setup logger
    logger = get_logger('integration_test', level=logging.INFO)
    
    # Validate a config
    config = {
        'container': 'spark-worker',
        'master': 'spark://master:7077',
        'hdfs_host': 'hdfs://namenode:8020',
        'hdfs_default_path': '/user/spark/data',
        'hdfs_container': 'namenode'
    }
    
    logger.info("Testing config validation...")
    is_valid, errors = ConfigValidator.validate_config(config)
    assert is_valid, "Config should be valid"
    logger.info("Config is valid")
    
    # Run health checks
    logger.info("Running health checks...")
    results = health_checker.run_all_checks(config)
    assert len(results) > 0, "Should have health check results"
    logger.info(f"Health checks completed: {len(results)} components")
    
    # Get overall status
    status, message = health_checker.get_overall_health()
    logger.info(f"Overall health: {status} - {message}")
    
    print(f"      ✓ Logging working")
    print(f"      ✓ Validation working")
    print(f"      ✓ Health checks working")
    print(f"      ✓ All modules integrated successfully")


# ============================================================================
# TEST 5: Error Handling Test
# ============================================================================

def test_error_handling():
    """Test error handling in modules"""
    from logging_config import get_logger, log_exception
    from validation import ValidationError
    import logging
    
    logger = get_logger('error_test', level=logging.DEBUG)
    
    # Test exception logging
    try:
        raise ValueError("Test exception")
    except Exception as e:
        log_exception(logger, e, extra_context={'test': 'error_handling'})
    
    # Test validation error
    try:
        from validation import validate_and_sanitize_input, Validator
        validate_and_sanitize_input('-invalid', Validator.is_valid_container_name, 'container')
        assert False, "Should have raised ValidationError"
    except ValidationError as e:
        assert 'container' in str(e), "Error should mention field name"
    
    print(f"      ✓ Exception logging working")
    print(f"      ✓ Validation errors working")
    print(f"      ✓ Error handling robust")


# ============================================================================
# RUN ALL TESTS
# ============================================================================

print("\n" + "=" * 80)
print("🚀 RUNNING TESTS")
print("=" * 80)

# Run tests
test_module("Logging Module", test_logging_module)
test_module("Validation Module", test_validation_module)
test_module("Health Check Module", test_health_check_module)
test_module("Integration Test", test_integration)
test_module("Error Handling Test", test_error_handling)

# Summary
print("\n" + "=" * 80)
print("📊 TEST SUMMARY")
print("=" * 80)
print(f"Total Tests:  {tests_total}")
print(f"Passed:       {tests_passed} ✅")
print(f"Failed:       {tests_failed} ❌")
print(f"Success Rate: {(tests_passed/tests_total)*100:.1f}%")

if tests_failed == 0:
    print("\n🎉 ALL TESTS PASSED! 🎉")
    print("Version 5.0.0 modules are working correctly!")
    sys.exit(0)
else:
    print(f"\n⚠️ {tests_failed} TEST(S) FAILED")
    print("Please review the errors above.")
    sys.exit(1)
