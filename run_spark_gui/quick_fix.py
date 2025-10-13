"""
Quick Fix Script - Automatically fix common issues
"""
import sys
import json
import sqlite3
from pathlib import Path
import shutil

print("=" * 80)
print("🔧 QUICK FIX TOOL - Spark Runner GUI")
print("=" * 80)

fixes_applied = []
issues_found = []

# Fix 1: Missing configuration file
def fix_config():
    config_file = Path('spark_runner_config.json')
    
    if not config_file.exists():
        print("\n❌ Missing: spark_runner_config.json")
        print("   Creating default configuration...")
        
        default_config = {
            "container": "spark-worker",
            "master": "spark://spark-master:7077",
            "ports": {
                "spark_master_ui": 8080,
                "spark_worker_ui": 8081,
                "namenode_ui": 9870,
                "datanode_ui": 9864,
                "jupyter": 8888,
                "history_server": 18080
            },
            "resource_limits": {
                "memory": "2g",
                "cores": 2,
                "executor_memory": "1g",
                "driver_memory": "1g"
            },
            "docker_network": "spark-network",
            "hdfs": {
                "default_replication": 1,
                "block_size": "128M"
            },
            "logging": {
                "level": "INFO",
                "max_size": "10MB",
                "backup_count": 5
            }
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        fixes_applied.append("Created default configuration file")
        print("   ✅ Configuration file created")
        return True
    
    # Validate existing config
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Check required keys
        required_keys = ['container', 'master']
        missing_keys = [key for key in required_keys if key not in config]
        
        if missing_keys:
            print(f"\n⚠️ Configuration missing keys: {missing_keys}")
            
            # Add missing keys with defaults
            if 'container' not in config:
                config['container'] = 'spark-worker'
            if 'master' not in config:
                config['master'] = 'spark://spark-master:7077'
            
            # Save fixed config
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            fixes_applied.append(f"Added missing config keys: {missing_keys}")
            print("   ✅ Configuration fixed")
            return True
        
        print("✅ Configuration file OK")
        return False
    
    except json.JSONDecodeError as e:
        print(f"\n❌ Configuration file corrupted: {e}")
        
        # Backup corrupted file
        backup_path = config_file.with_suffix('.json.backup')
        shutil.copy(config_file, backup_path)
        print(f"   📦 Backed up to: {backup_path}")
        
        # Create new config
        return fix_config()

# Fix 2: Database issues
def fix_database():
    db_file = Path('spark_runner.db')
    
    if not db_file.exists():
        print("\n⚠️ Database file not found")
        print("   It will be created on first run")
        return False
    
    # Try to connect and validate
    try:
        conn = sqlite3.connect(str(db_file))
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['job_history', 'upload_history', 'performance_metrics',
                          'user_preferences', 'ai_code_history']
        
        missing_tables = [t for t in expected_tables if t not in tables]
        
        if missing_tables:
            print(f"\n⚠️ Database missing tables: {missing_tables}")
            print("   Recreating database...")
            
            conn.close()
            
            # Backup old database
            backup_path = db_file.with_suffix('.db.backup')
            shutil.copy(db_file, backup_path)
            print(f"   📦 Backed up to: {backup_path}")
            
            # Remove and let it recreate
            db_file.unlink()
            
            fixes_applied.append("Database recreated")
            print("   ✅ Database will be recreated on startup")
            return True
        
        conn.close()
        print("✅ Database OK")
        return False
    
    except sqlite3.DatabaseError as e:
        print(f"\n❌ Database error: {e}")
        
        # Backup corrupted database
        backup_path = db_file.with_suffix('.db.backup')
        shutil.copy(db_file, backup_path)
        print(f"   📦 Backed up to: {backup_path}")
        
        # Remove corrupted database
        db_file.unlink()
        
        fixes_applied.append("Removed corrupted database")
        print("   ✅ Database will be recreated on startup")
        return True

# Fix 3: Cache cleanup
def fix_cache():
    # Clear any stale cache files
    cache_files = list(Path('.').glob('*.cache'))
    temp_files = list(Path('.').glob('*.tmp'))
    
    if cache_files or temp_files:
        print(f"\n⚠️ Found {len(cache_files) + len(temp_files)} temporary files")
        
        for f in cache_files + temp_files:
            try:
                f.unlink()
                print(f"   🗑️ Removed: {f.name}")
            except:
                pass
        
        fixes_applied.append(f"Cleaned {len(cache_files) + len(temp_files)} temp files")
        return True
    
    return False

# Fix 4: Python cache cleanup
def fix_pycache():
    pycache_dirs = list(Path('.').glob('**/__pycache__'))
    pyc_files = list(Path('.').glob('**/*.pyc'))
    
    if pycache_dirs or pyc_files:
        print(f"\n⚠️ Found {len(pycache_dirs)} __pycache__ directories")
        
        for d in pycache_dirs:
            try:
                shutil.rmtree(d)
                print(f"   🗑️ Removed: {d}")
            except:
                pass
        
        for f in pyc_files:
            try:
                f.unlink()
            except:
                pass
        
        fixes_applied.append(f"Cleaned Python cache")
        return True
    
    return False

# Run all fixes
print("\n" + "=" * 80)
print("Running automated fixes...")
print("=" * 80)

fix_config()
fix_database()
fix_cache()
fix_pycache()

# Summary
print("\n" + "=" * 80)
print("📊 SUMMARY")
print("=" * 80)

if fixes_applied:
    print(f"\n✅ Applied {len(fixes_applied)} fix(es):")
    for fix in fixes_applied:
        print(f"   • {fix}")
else:
    print("\n✅ No issues found - system is healthy!")

if issues_found:
    print(f"\n⚠️ Found {len(issues_found)} issue(s) that need manual attention:")
    for issue in issues_found:
        print(f"   • {issue}")

print("\n" + "=" * 80)
print("💡 You can now run: python safe_start.py")
print("=" * 80)
