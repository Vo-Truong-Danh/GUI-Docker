"""
Auto-fix script: Replace subprocess.run with run_hidden to hide console windows
"""
import re
from pathlib import Path

def fix_file(filepath):
    """Fix subprocess calls in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Check if subprocess_utils already imported
        has_import = 'from subprocess_utils import' in content or 'import subprocess_utils' in content
        
        # Skip if it's subprocess_utils.py itself
        if 'subprocess_utils.py' in str(filepath):
            return False, "Skipped (subprocess_utils.py itself)"
        
        # Count replacements needed
        count_run = content.count('subprocess.run(')
        count_popen = content.count('subprocess.Popen(')
        
        if count_run == 0 and count_popen == 0:
            return False, "No subprocess calls found"
        
        # Add import if not present
        if not has_import and (count_run > 0 or count_popen > 0):
            # Find import subprocess line
            import_pattern = r'(import subprocess\n)'
            if re.search(import_pattern, content):
                # Add after import subprocess
                content = re.sub(
                    import_pattern,
                    r'\1\n# Import subprocess utilities for hidden console windows\ntry:\n    from subprocess_utils import run_hidden, popen_hidden\nexcept ImportError:\n    def run_hidden(*args, **kwargs):\n        return subprocess.run(*args, **kwargs)\n    def popen_hidden(*args, **kwargs):\n        return subprocess.Popen(*args, **kwargs)\n',
                    content,
                    count=1
                )
        
        # Replace subprocess.run( with run_hidden(
        content = content.replace('subprocess.run(', 'run_hidden(')
        
        # Replace subprocess.Popen( with popen_hidden(
        content = content.replace('subprocess.Popen(', 'popen_hidden(')
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, f"Fixed: {count_run} run() + {count_popen} Popen()"
        else:
            return False, "No changes needed"
    
    except Exception as e:
        return False, f"Error: {e}"


def main():
    """Main function"""
    print("=" * 70)
    print("Auto-fix: Hide console windows for subprocess calls")
    print("=" * 70)
    print()
    
    # Files to fix
    files_to_fix = [
        'run_spark_gui/hdfs_utils.py',
        'run_spark_gui/hdfs_upload_tab_v4_clean.py',
        'run_spark_gui/java_unzip_util.py',
        'run_spark_gui/health_check.py',
        'run_spark_gui/performance_monitor_v4_clean.py',
        'run_spark_gui/advanced_ai_tab_v8.py',
    ]
    
    fixed_count = 0
    skipped_count = 0
    
    for filepath in files_to_fix:
        path = Path(filepath)
        if not path.exists():
            print(f"❌ {filepath} - Not found")
            continue
        
        success, message = fix_file(path)
        if success:
            print(f"✅ {filepath} - {message}")
            fixed_count += 1
        else:
            print(f"⏭️  {filepath} - {message}")
            skipped_count += 1
    
    print()
    print("=" * 70)
    print(f"Summary: {fixed_count} fixed, {skipped_count} skipped")
    print("=" * 70)
    print()
    print("✅ Done! Console windows will now be hidden when running executables.")
    print()


if __name__ == '__main__':
    main()
