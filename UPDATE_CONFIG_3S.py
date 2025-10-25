#!/usr/bin/env python3
"""
Direct file write - bypass any caching
"""
import json
import os

config_path = "d:/BaiTapSinhVien/TH BigData/GUI-Docker/spark_runner_config.json"

# Read
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# Modify
print(f"Current timeout: {config.get('spark_job_timeout')}")
config['spark_job_timeout'] = 3
config['hdfs_upload_timeout'] = 3
config['docker_command_timeout'] = 3

# Write
with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print(f"Updated timeout: {config.get('spark_job_timeout')}")

# Verify by reading back
with open(config_path, 'r', encoding='utf-8') as f:
    verify = json.load(f)
print(f"Verified timeout: {verify.get('spark_job_timeout')}")
