#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script tự động xóa các file thừa không cần thiết trong run_spark_gui/
"""

import os
import shutil
from pathlib import Path

# Các file cần XÓA (đã có phiên bản mới hơn hoặc trùng lặp)
FILES_TO_REMOVE = [
    # File cũ - đã có v2
    "run_spark_gui/auto_healing.py",  # Có auto_healing_v2.py
    "run_spark_gui/error_handler.py",  # Có error_handler_v2.py
    "run_spark_gui/connection_pool.py",  # File cũ
    
    # File trùng lặp
    "run_spark_gui/auto_recovery.py",  # Trùng với auto_healing
    "run_spark_gui/docker_utils_enhanced.py",  # Trùng với docker_utils.py
    "run_spark_gui/performance_optimizer_advanced.py",  # Trùng với performance_optimizer.py
    
    # File test không cần thiết
    "run_spark_gui/test_improvements.py",
    "run_spark_gui/test_suite.py",
    "run_spark_gui/test_v6.3.1_comprehensive.py",
    
    # File backup/cleanup tools
    "run_spark_gui/cleanup_system.py",
    "run_spark_gui/backup_manager.py",
    
    # File quality checker
    "run_spark_gui/code_quality_checker.py",
    "run_spark_gui/code_quality_report.json",
    "run_spark_gui/dependency_optimizer.py",
    "run_spark_gui/dependency_report.json",
    
    # File requirements cũ
    "run_spark_gui/requirements_optimized.txt",
    
    # File log và db test
    "run_spark_gui/security_audit.log",
    "run_spark_gui/spark_runner.db",
    
    # File config cũ
    "run_spark_gui/spark_runner_config.json",
    
    # Utility trùng lặp
    "run_spark_gui/utility_manager.py",  # Trùng với system_utils.py
    "run_spark_gui/resource_cleanup.py",  # Trùng với resource_manager.py
    "run_spark_gui/resource_optimizer.py",  # Trùng với resource_manager.py
]

# Thư mục cần XÓA
DIRS_TO_REMOVE = [
    "run_spark_gui/.cache",
    "run_spark_gui/backups",
    "run_spark_gui/logs",
    "run_spark_gui/__pycache__",
]

def cleanup():
    """Xóa các file và thư mục thừa"""
    removed_files = []
    removed_dirs = []
    total_size = 0
    
    # Xóa files
    for file_path in FILES_TO_REMOVE:
        full_path = Path(file_path)
        if full_path.exists():
            size = full_path.stat().st_size
            full_path.unlink()
            removed_files.append(file_path)
            total_size += size
            print(f"✅ Đã xóa: {file_path}")
    
    # Xóa directories
    for dir_path in DIRS_TO_REMOVE:
        full_path = Path(dir_path)
        if full_path.exists():
            size = sum(f.stat().st_size for f in full_path.rglob('*') if f.is_file())
            shutil.rmtree(full_path)
            removed_dirs.append(dir_path)
            total_size += size
            print(f"✅ Đã xóa thư mục: {dir_path}")
    
    # Báo cáo
    print("\n" + "="*70)
    print("📊 BÁO CÁO XÓA FILE THỪA")
    print("="*70)
    print(f"✅ Đã xóa {len(removed_files)} files")
    print(f"✅ Đã xóa {len(removed_dirs)} thư mục")
    print(f"💾 Giải phóng: {total_size / 1024:.2f} KB")
    print("\n📋 Files đã xóa:")
    for f in removed_files:
        print(f"  - {f}")
    print("\n📁 Thư mục đã xóa:")
    for d in removed_dirs:
        print(f"  - {d}")
    print("\n✅ HOÀN TẤT!")

if __name__ == "__main__":
    cleanup()
