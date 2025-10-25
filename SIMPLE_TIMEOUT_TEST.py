#!/usr/bin/env python3
"""Simple timeout test"""
import json
import os
import time
import subprocess
from datetime import datetime

# Read config directly
config_file = "d:/BaiTapSinhVien/TH BigData/GUI-Docker/spark_runner_config.json"
with open(config_file) as f:
    config = json.load(f)
timeout = config['spark_job_timeout']

print(f"Timeout: {timeout}s")
print(f"Testing subprocess timeout...")

start = datetime.now()
try:
    subprocess.run(['python', '-c', 'import time; time.sleep(10)'], timeout=timeout)
    print(f"ERROR: Process completed!")
except subprocess.TimeoutExpired:
    elapsed = (datetime.now() - start).total_seconds()
    print(f"✅ Timed out after {elapsed:.1f}s (expected ~{timeout}s)")
