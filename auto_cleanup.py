"""
Auto Cleanup - No confirmation needed
"""

import os
from pathlib import Path

workspace = Path(r"d:\BaiTapSinhVien\TH BigData\GUI-Docker")

# OLD files to REMOVE
old_files = [
    'COMPLETION_FINAL.md', 'COMPLETION_REPORT.md', 'COMPLETION_SUMMARY.md',
    'COMPLETION_SUMMARY_V6.3.md', 'DOCUMENTATION_INDEX.md',
    'DOCUMENTATION_INDEX_V6.1.md', 'DOCUMENTATION_INDEX_V6.3.md',
    'DOCUMENTATION_INDEX_V6.4.0.md', 'FEATURE_GUIDE_V6.md',
    'HDFS_UPLOAD_IMPROVEMENTS.md', 'IMPLEMENTATION_GUIDE_V6.1.md',
    'IMPLEMENTATION_SUMMARY_V6.3.1.md', 'IMPROVEMENTS_SUMMARY_V6.1.md',
    'IMPROVEMENTS_SUMMARY_V6.md', 'INDEX.md', 'MIGRATION_GUIDE_V6.md',
    'NEW_FEATURES_GUIDE_V6.1.md', 'NEW_FEATURES_GUIDE_V6.4.0.md',
    'NEW_FEATURES_V6.3.0.md', 'OPTIMIZATION_COMPLETE_V6.4.0.md',
    'OPTIMIZATION_COMPLETION_REPORT.md', 'OPTIMIZATION_COMPLETION_V6.2.md',
    'OPTIMIZATION_SUMMARY_V6.4.0.md', 'QUICKSTART.md',
    'QUICK_START_NEW_FEATURES.md', 'QUICK_UPDATE_V6.1.md',
    'README_OPTIMIZATION_V6.3.md', 'SUMMARY_NEW_FEATURES_V6.3.0.md',
    'SUMMARY_V6.2.md', 'SYSTEM_ANALYSIS_REPORT.md',
    'SYSTEM_IMPROVEMENTS_V6.2.md', 'TROUBLESHOOTING.md',
    'UPGRADE_GUIDE.md', 'USER_GUIDE.md', 'validate_system.py'
]

print("🗑️  AUTO CLEANUP STARTING...")
print("=" * 70)

removed = 0
total_size = 0

for filename in old_files:
    filepath = workspace / filename
    if filepath.exists():
        size = filepath.stat().st_size
        filepath.unlink()
        removed += 1
        total_size += size
        print(f"✅ {filename}")

print("=" * 70)
print(f"✅ Removed {removed} files ({total_size/1024:.1f} KB)")
print("\n📁 Remaining docs:")
for f in sorted(workspace.glob('*.md')):
    print(f"   ✅ {f.name}")
