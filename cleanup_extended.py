"""
Extended Cleanup Script - Remove ALL redundant files
Version: 2.0.0
Date: 2025-10-14
"""

import os
import shutil
from pathlib import Path

def cleanup_extended():
    """Extended cleanup - remove all old version files"""
    
    workspace = Path(r"d:\BaiTapSinhVien\TH BigData\GUI-Docker")
    
    # Files to KEEP (new optimization docs)
    keep_files = {
        'OPTIMIZATION_SUMMARY.md',
        'OPTIMIZATION_INDEX.md',
        'OPTIMIZATION_FINAL_REPORT.md',
        'OPTIMIZATION_QUICKSTART.md',
        'SYSTEM_OPTIMIZATION_ANALYSIS.md',
        'MIGRATION_GUIDE_V7.md',
        'README.md',
        'CHANGELOG.md',
        '.gitignore',
        'spark_runner_config.json',
        'cleanup_report.json'
    }
    
    # OLD files to REMOVE
    old_files_to_remove = [
        # Completion reports (old)
        'COMPLETION_FINAL.md',
        'COMPLETION_REPORT.md',
        'COMPLETION_SUMMARY.md',
        'COMPLETION_SUMMARY_V6.3.md',
        
        # Documentation indices (old versions)
        'DOCUMENTATION_INDEX.md',
        'DOCUMENTATION_INDEX_V6.1.md',
        'DOCUMENTATION_INDEX_V6.3.md',
        'DOCUMENTATION_INDEX_V6.4.0.md',
        
        # Feature guides (old)
        'FEATURE_GUIDE_V6.md',
        'HDFS_UPLOAD_IMPROVEMENTS.md',
        
        # Implementation guides (old)
        'IMPLEMENTATION_GUIDE_V6.1.md',
        'IMPLEMENTATION_SUMMARY_V6.3.1.md',
        
        # Improvement summaries (old)
        'IMPROVEMENTS_SUMMARY_V6.1.md',
        'IMPROVEMENTS_SUMMARY_V6.md',
        
        # Index (old)
        'INDEX.md',
        
        # Migration guides (old)
        'MIGRATION_GUIDE_V6.md',
        
        # New features guides (old)
        'NEW_FEATURES_GUIDE_V6.1.md',
        'NEW_FEATURES_GUIDE_V6.4.0.md',
        'NEW_FEATURES_V6.3.0.md',
        
        # Optimization reports (old versions)
        'OPTIMIZATION_COMPLETE_V6.4.0.md',
        'OPTIMIZATION_COMPLETION_REPORT.md',
        'OPTIMIZATION_COMPLETION_V6.2.md',
        'OPTIMIZATION_SUMMARY_V6.4.0.md',
        
        # Quick start guides (old)
        'QUICKSTART.md',
        'QUICK_START_NEW_FEATURES.md',
        'QUICK_UPDATE_V6.1.md',
        
        # README (old versions)
        'README_OPTIMIZATION_V6.3.md',
        
        # Summary reports (old)
        'SUMMARY_NEW_FEATURES_V6.3.0.md',
        'SUMMARY_V6.2.md',
        
        # System reports (old)
        'SYSTEM_ANALYSIS_REPORT.md',
        'SYSTEM_IMPROVEMENTS_V6.2.md',
        
        # Guides (old)
        'TROUBLESHOOTING.md',
        'UPGRADE_GUIDE.md',
        'USER_GUIDE.md',
        
        # Validation script (old)
        'validate_system.py'
    ]
    
    print("=" * 80)
    print("EXTENDED CLEANUP - REMOVING ALL OLD VERSION FILES")
    print("=" * 80)
    print()
    
    removed_count = 0
    removed_size = 0
    
    for filename in old_files_to_remove:
        filepath = workspace / filename
        if filepath.exists():
            size = filepath.stat().st_size
            try:
                filepath.unlink()
                removed_count += 1
                removed_size += size
                print(f"✅ Removed: {filename} ({size:,} bytes)")
            except Exception as e:
                print(f"❌ Error removing {filename}: {e}")
        else:
            print(f"⏭️  Already removed: {filename}")
    
    print()
    print("=" * 80)
    print(f"✅ CLEANUP COMPLETED")
    print("=" * 80)
    print(f"Files removed: {removed_count}")
    print(f"Space freed: {removed_size / 1024:.2f} KB")
    print()
    
    # Show files that remain
    print("📁 REMAINING DOCUMENTATION FILES:")
    print("-" * 80)
    for file in sorted(workspace.glob('*.md')):
        print(f"   ✅ {file.name}")
    
    print()
    print("🎉 Cleanup complete! System is now clean and optimized!")

if __name__ == '__main__':
    import sys
    
    response = input("⚠️  This will delete 40+ old documentation files. Continue? (yes/no): ")
    if response.lower() == 'yes':
        cleanup_extended()
    else:
        print("❌ Cancelled")
