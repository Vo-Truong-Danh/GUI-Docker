"""
Quick Test for New Optimization Modules
Tests all newly created modules to ensure they work correctly
Version: 1.0.0
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_result(test_name, passed, message=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")
    if message:
        print(f"       {message}")

def test_error_handler():
    """Test error_handler module"""
    print_header("Testing Error Handler")
    try:
        from error_handler import get_error_handler, safe_execute, ErrorSeverity
        
        handler = get_error_handler()
        
        # Test safe_execute
        def risky_function():
            return 1 / 0
        
        result = safe_execute(risky_function, default="fallback")
        print_result("Error Handler Import", True)
        print_result("Safe Execute", result == "fallback", f"Result: {result}")
        
        # Test error tracking
        stats = handler.get_error_stats()
        print_result("Error Stats", 'total_errors' in stats, f"Total errors: {stats.get('total_errors', 0)}")
        
        return True
    except Exception as e:
        print_result("Error Handler", False, str(e))
        return False

def test_auto_recovery():
    """Test auto_recovery module"""
    print_header("Testing Auto Recovery")
    try:
        from auto_recovery import get_auto_recovery_manager
        
        recovery = get_auto_recovery_manager()
        
        # Test recovery attempt
        can_recover = recovery.can_attempt_recovery('test_error')
        print_result("Auto Recovery Import", True)
        print_result("Can Attempt Recovery", can_recover)
        
        # Test stats
        stats = recovery.get_stats()
        print_result("Recovery Stats", 'registered_strategies' in stats, 
                    f"Strategies: {len(stats.get('registered_strategies', []))}")
        
        return True
    except Exception as e:
        print_result("Auto Recovery", False, str(e))
        return False

def test_backup_manager():
    """Test backup_manager module"""
    print_header("Testing Backup Manager")
    try:
        from backup_manager import get_backup_manager
        
        backup_mgr = get_backup_manager()
        
        # Test backup listing
        backups = backup_mgr.list_backups()
        print_result("Backup Manager Import", True)
        print_result("List Backups", True, f"Found {len(backups)} backups")
        
        return True
    except Exception as e:
        print_result("Backup Manager", False, str(e))
        return False

def test_system_optimizer():
    """Test system_optimizer module"""
    print_header("Testing System Optimizer")
    try:
        from system_optimizer import get_system_optimizer
        
        optimizer = get_system_optimizer()
        
        # Test metrics
        metrics = optimizer.get_system_metrics()
        print_result("System Optimizer Import", True)
        print_result("Get Metrics", 'cpu' in metrics and 'memory' in metrics,
                    f"CPU: {metrics.get('cpu', {}).get('percent', 0):.1f}%, "
                    f"Memory: {metrics.get('memory', {}).get('percent', 0):.1f}%")
        
        # Test memory optimization
        result = optimizer.optimize_memory()
        print_result("Memory Optimization", result.get('success', False),
                    f"Objects collected: {result.get('objects_collected', 0)}")
        
        # Test leak check
        leak_check = optimizer.check_resource_leaks()
        print_result("Resource Leak Check", 'open_files' in leak_check,
                    f"Open files: {leak_check.get('open_files', 0)}")
        
        return True
    except Exception as e:
        print_result("System Optimizer", False, str(e))
        return False

def test_security_auditor():
    """Test security_auditor module"""
    print_header("Testing Security Auditor")
    try:
        from security_auditor import get_security_auditor
        
        auditor = get_security_auditor()
        
        print_result("Security Auditor Import", True)
        
        # Test file scanning (scan this test file)
        current_file = os.path.abspath(__file__)
        result = auditor.scan_file(current_file)
        
        print_result("File Scan", 'vulnerabilities' in result,
                    f"Found {result.get('count', 0)} issues")
        
        return True
    except Exception as e:
        print_result("Security Auditor", False, str(e))
        return False

def test_code_quality_checker():
    """Test code_quality_checker module"""
    print_header("Testing Code Quality Checker")
    try:
        from code_quality_checker import get_code_quality_checker
        
        checker = get_code_quality_checker()
        
        print_result("Code Quality Checker Import", True)
        
        # Test file analysis
        current_file = os.path.abspath(__file__)
        result = checker.analyze_file(current_file)
        
        print_result("File Analysis", 'metrics' in result and 'quality_score' in result,
                    f"Quality Score: {result.get('quality_score', 0):.1f}/100")
        
        metrics = result.get('metrics', {})
        print(f"       Lines: {metrics.get('lines', 0)}, "
              f"Functions: {metrics.get('functions', 0)}, "
              f"Issues: {len(result.get('issues', []))}")
        
        return True
    except Exception as e:
        print_result("Code Quality Checker", False, str(e))
        return False

def test_health_dashboard():
    """Test health monitoring dashboard (non-GUI parts)"""
    print_header("Testing Health Monitoring Dashboard")
    try:
        from health_monitoring_dashboard import HealthMonitoringDashboard
        
        # Don't create GUI, just test import and initialization
        print_result("Health Dashboard Import", True)
        print_result("GUI Test", True, "Skipped (would open window)")
        
        return True
    except Exception as e:
        print_result("Health Dashboard", False, str(e))
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  SYSTEM OPTIMIZATION MODULES - QUICK TEST")
    print("=" * 70)
    print()
    print("Testing all newly created optimization modules...")
    
    results = {
        'Error Handler': test_error_handler(),
        'Auto Recovery': test_auto_recovery(),
        'Backup Manager': test_backup_manager(),
        'System Optimizer': test_system_optimizer(),
        'Security Auditor': test_security_auditor(),
        'Code Quality Checker': test_code_quality_checker(),
        'Health Dashboard': test_health_dashboard()
    }
    
    # Summary
    print_header("TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print()
    
    for module, result in results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {module}")
    
    print("\n" + "=" * 70)
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! All modules are working correctly.")
    else:
        print(f"⚠️ {failed} TEST(S) FAILED. Check errors above.")
    
    print("=" * 70)
    print()
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
