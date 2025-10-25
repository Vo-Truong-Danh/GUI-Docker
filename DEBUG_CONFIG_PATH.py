#!/usr/bin/env python3
"""
Debug: Check if config file path is correct
"""
import os
import json

print("=" * 70)
print("🔍 DEBUG: Config file path check")
print("=" * 70)

# Check current directory
print(f"\n📍 Current working directory: {os.getcwd()}")

# Check where spark_backend.py is
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'run_spark_gui'))

module_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(module_dir)

print(f"📁 Module dir: {module_dir}")
print(f"📁 Project root: {project_root}")

# Try to construct config path like spark_backend.py does
config_path_computed = os.path.join(project_root, 'spark_runner_config.json')
print(f"📄 Computed config path: {config_path_computed}")
print(f"   Exists: {os.path.exists(config_path_computed)}")

# Also check relative path
relative_path = 'spark_runner_config.json'
print(f"\n📄 Relative config path: {relative_path}")
print(f"   Exists: {os.path.exists(relative_path)}")
print(f"   Full path: {os.path.abspath(relative_path)}")

# Read config
if os.path.exists(config_path_computed):
    print(f"\n✅ Reading config from: {config_path_computed}")
    with open(config_path_computed, 'r') as f:
        config = json.load(f)
    print(f"   spark_job_timeout: {config.get('spark_job_timeout', 'NOT FOUND')}")
    print(f"   hdfs_upload_timeout: {config.get('hdfs_upload_timeout', 'NOT FOUND')}")
else:
    print(f"\n❌ Config file not found at: {config_path_computed}")

print("\n" + "=" * 70)
