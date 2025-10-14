"""
Comprehensive System Analysis and Optimization Tool
Performs full system audit, security scan, and optimization
Version: 1.0.0
"""
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from logging_config import get_logger
    logger = get_logger('system_analysis', log_to_file=True)
except ImportError:
    logger = None
    print("⚠️ Logging module not available")

try:
    from system_optimizer import get_system_optimizer
    OPTIMIZER_AVAILABLE = True
except ImportError:
    OPTIMIZER_AVAILABLE = False
    print("⚠️ System optimizer not available")

try:
    from security_auditor import get_security_auditor
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False
    print("⚠️ Security auditor not available")

try:
    from backup_manager import get_backup_manager
    BACKUP_AVAILABLE = True
except ImportError:
    BACKUP_AVAILABLE = False
    print("⚠️ Backup manager not available")


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_section(title: str):
    """Print formatted section"""
    print("\n" + "-" * 80)
    print(f"  {title}")
    print("-" * 80)


def analyze_system():
    """Comprehensive system analysis"""
    print_header("COMPREHENSIVE SYSTEM ANALYSIS & OPTIMIZATION")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'phases': {}
    }
    
    # Phase 1: System Metrics
    if OPTIMIZER_AVAILABLE:
        print_section("Phase 1: System Metrics Analysis")
        optimizer = get_system_optimizer(logger)
        
        print("📊 Collecting system metrics...")
        metrics = optimizer.get_system_metrics()
        
        if metrics:
            print(f"✓ CPU Usage: {metrics.get('cpu', {}).get('percent', 0):.1f}%")
            print(f"✓ Memory Usage: {metrics.get('memory', {}).get('percent', 0):.1f}%")
            print(f"✓ Disk Usage: {metrics.get('disk', {}).get('percent', 0):.1f}%")
            print(f"✓ Process Memory: {metrics.get('process', {}).get('memory_rss', 0) / (1024*1024):.1f} MB")
            print(f"✓ Process Threads: {metrics.get('process', {}).get('num_threads', 0)}")
            
            results['phases']['system_metrics'] = metrics
        
        # Check for resource leaks
        print("\n🔍 Checking for resource leaks...")
        leak_check = optimizer.check_resource_leaks()
        
        if leak_check.get('warnings'):
            print("⚠️ Resource leak warnings:")
            for warning in leak_check['warnings']:
                print(f"   - {warning}")
        else:
            print("✓ No resource leaks detected")
        
        results['phases']['resource_leaks'] = leak_check
    
    # Phase 2: Security Audit
    if SECURITY_AVAILABLE:
        print_section("Phase 2: Security Audit")
        auditor = get_security_auditor(logger)
        
        print("🔒 Scanning for security vulnerabilities...")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        security_report = auditor.generate_security_report(current_dir)
        
        print(f"✓ Files scanned: {security_report.get('code_vulnerabilities', {}).get('files_scanned', 0)}")
        print(f"✓ Security Score: {security_report.get('overall_score', 0)}/100")
        
        vulns = security_report.get('code_vulnerabilities', {}).get('by_severity', {})
        if vulns:
            print(f"\nVulnerabilities by severity:")
            print(f"  🔴 Critical: {vulns.get('CRITICAL', 0)}")
            print(f"  🟠 High: {vulns.get('HIGH', 0)}")
            print(f"  🟡 Medium: {vulns.get('MEDIUM', 0)}")
            print(f"  🟢 Low: {vulns.get('LOW', 0)}")
        
        perm_issues = security_report.get('permission_issues', {}).get('count', 0)
        if perm_issues > 0:
            print(f"\n⚠️ Permission issues found: {perm_issues}")
        
        recommendations = security_report.get('recommendations', [])
        if recommendations:
            print(f"\n📋 Security Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        
        results['phases']['security_audit'] = security_report
    
    # Phase 3: Memory Optimization
    if OPTIMIZER_AVAILABLE:
        print_section("Phase 3: Memory Optimization")
        optimizer = get_system_optimizer(logger)
        
        print("🧹 Optimizing memory...")
        mem_result = optimizer.optimize_memory()
        
        if mem_result.get('success'):
            print(f"✓ Objects collected: {mem_result.get('objects_collected', 0)}")
            print(f"✓ Memory improvement: {mem_result.get('improvement', 0):.2f}%")
        else:
            print(f"❌ Memory optimization failed: {mem_result.get('error', 'Unknown error')}")
        
        results['phases']['memory_optimization'] = mem_result
    
    # Phase 4: Temp File Cleanup
    if OPTIMIZER_AVAILABLE:
        print_section("Phase 4: Temporary File Cleanup")
        
        print("🗑️ Cleaning temporary files...")
        cleanup_result = optimizer.clear_temp_files()
        
        if cleanup_result.get('success'):
            print(f"✓ Files cleared: {cleanup_result.get('files_cleared', 0)}")
            print(f"✓ Space freed: {cleanup_result.get('space_freed_mb', 0):.2f} MB")
            
            if cleanup_result.get('errors'):
                print(f"⚠️ Errors encountered: {len(cleanup_result['errors'])}")
        else:
            print(f"❌ Cleanup failed: {cleanup_result.get('error', 'Unknown error')}")
        
        results['phases']['temp_cleanup'] = cleanup_result
    
    # Phase 5: Backup Configuration
    if BACKUP_AVAILABLE:
        print_section("Phase 5: Configuration Backup")
        backup_mgr = get_backup_manager()
        
        print("💾 Creating configuration backup...")
        config_file = os.path.join(os.path.dirname(__file__), 'spark_runner_config.json')
        
        if os.path.exists(config_file):
            backup_path = backup_mgr.create_backup(config_file, 'config')
            if backup_path:
                print(f"✓ Backup created: {backup_path}")
                results['phases']['backup'] = {'success': True, 'path': backup_path}
            else:
                print("❌ Backup failed")
                results['phases']['backup'] = {'success': False}
        else:
            print("⚠️ Configuration file not found")
            results['phases']['backup'] = {'success': False, 'reason': 'File not found'}
        
        # List existing backups
        backups = backup_mgr.list_backups()
        if backups:
            print(f"\n📦 Total backups: {len(backups)}")
            print("Recent backups:")
            for backup in backups[:5]:
                print(f"   - {backup['name']} ({backup['timestamp']})")
    
    # Phase 6: Generate Report
    print_section("Phase 6: Generating Report")
    
    report_file = f"system_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path = os.path.join(os.path.dirname(__file__), 'logs', report_file)
    
    # Ensure logs directory exists
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"✓ Report saved: {report_path}")
    except Exception as e:
        print(f"❌ Failed to save report: {e}")
    
    # Final Summary
    print_header("ANALYSIS COMPLETE")
    
    print("\n📊 Summary:")
    print(f"   Phases completed: {len(results['phases'])}")
    
    if OPTIMIZER_AVAILABLE:
        print(f"   Memory optimized: ✓")
        print(f"   Temp files cleaned: ✓")
    
    if SECURITY_AVAILABLE:
        score = results.get('phases', {}).get('security_audit', {}).get('overall_score', 0)
        print(f"   Security score: {score}/100")
    
    if BACKUP_AVAILABLE:
        backup_success = results.get('phases', {}).get('backup', {}).get('success', False)
        print(f"   Configuration backed up: {'✓' if backup_success else '✗'}")
    
    print(f"\n   Report: {report_path}")
    print("\n✅ System analysis and optimization completed!")
    print("=" * 80)
    
    return results


def main():
    """Main function"""
    try:
        analyze_system()
    except KeyboardInterrupt:
        print("\n\n⚠️ Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        if logger:
            logger.error(f"Analysis failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
