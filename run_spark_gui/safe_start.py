"""
Safe Start Script for Spark Runner GUI
Performs pre-flight checks before launching
"""
import sys
import os
from pathlib import Path
import subprocess
import json

print("=" * 80)
print("🚀 SPARK RUNNER GUI - SAFE START")
print("=" * 80)

# Pre-flight checklist
checks_passed = 0
checks_total = 0

def check(name, test_func):
    """Run a check and report result"""
    global checks_passed, checks_total
    checks_total += 1
    
    print(f"\n{checks_total}. {name}...", end=" ")
    try:
        result = test_func()
        if result:
            print("✅")
            checks_passed += 1
            return True
        else:
            print("⚠️")
            return False
    except Exception as e:
        print(f"❌ ({e})")
        return False

# Check 1: Python version
def check_python():
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"(Python {version.major}.{version.minor}.{version.micro})", end=" ")
        return True
    return False

check("Python Version (>= 3.8)", check_python)

# Check 2: Required files exist
def check_files():
    required_files = [
        'main.py',
        'spark_backend.py',
        'docker_utils.py',
        'system_utils.py',
        'database.py',
        'spark_runner_config.json'
    ]
    
    for file in required_files:
        if not Path(file).exists():
            print(f"\n   Missing: {file}", end="")
            return False
    
    print(f"({len(required_files)} files)", end=" ")
    return True

check("Required Files", check_files)

# Check 3: Import modules
def check_imports():
    try:
        import tkinter
        import sqlite3
        return True
    except ImportError as e:
        print(f"\n   Missing module: {e}", end="")
        return False

check("Python Modules (tkinter, sqlite3)", check_imports)

# Check 4: Configuration valid
def check_config():
    try:
        with open('spark_runner_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        required_keys = ['container', 'master']
        for key in required_keys:
            if key not in config:
                print(f"\n   Missing config: {key}", end="")
                return False
        
        return True
    except Exception as e:
        print(f"\n   Error: {e}", end="")
        return False

check("Configuration File", check_config)

# Check 5: Database accessible
def check_database():
    try:
        from database import db
        # Try a simple operation
        stats = db.get_job_stats()
        return True
    except Exception as e:
        print(f"\n   Error: {e}", end="")
        return False

check("Database Connection", check_database)

# Check 6: Docker available (warning only)
def check_docker():
    try:
        from docker_utils import is_docker_running, check_docker_compose
        
        docker_ok = is_docker_running()
        compose_ok, _ = check_docker_compose()
        
        if docker_ok and compose_ok:
            print("(Docker + Compose)", end=" ")
            return True
        elif docker_ok:
            print("(Docker only)", end=" ")
            return True
        else:
            print("(Not running - will auto-start)", end=" ")
            return True  # Not critical, can auto-start
    except Exception as e:
        print(f"\n   Warning: {e}", end="")
        return True  # Not critical

check("Docker Environment", check_docker)

# Summary
print("\n" + "=" * 80)
print(f"📊 Pre-flight Check: {checks_passed}/{checks_total} passed")
print("=" * 80)

if checks_passed == checks_total:
    print("\n✅ All checks passed! Starting application...\n")
    print("=" * 80)
    
    # Launch main application
    try:
        import main
        # main.py will handle the rest
    except KeyboardInterrupt:
        print("\n\n⚠️ Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Application error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
else:
    print("\n⚠️ Some checks failed. Please fix issues before starting.")
    print("\n💡 Common fixes:")
    print("   • Install Python 3.8+")
    print("   • Run: pip install tkinter (if missing)")
    print("   • Ensure spark_runner_config.json exists")
    print("   • Check file permissions")
    
    print("\n" + "=" * 80)
    sys.exit(1)
