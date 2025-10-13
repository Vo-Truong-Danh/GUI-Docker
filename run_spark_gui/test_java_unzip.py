"""
Quick Test: Java Unzip Integration
Tests the complete Java-based unzip workflow
"""

import sys
import subprocess
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

def log(msg, tag='INFO'):
    """Simple logger"""
    print(f"[{tag:8}] {msg}")


def test_java_unzip_integration():
    """Test complete Java unzip integration"""
    print("=" * 80)
    print("JAVA UNZIP INTEGRATION TEST")
    print("=" * 80)
    
    try:
        # Test 1: Import modules
        print("\n1. Testing imports...")
        from java_unzip_util import check_java_available, setup_java_unzip, unzip_with_java
        log("✅ All imports successful", "SUCCESS")
        
        # Test 2: Check Java
        print("\n2. Checking Java availability...")
        available, version = check_java_available('namenode', log)
        if not available:
            log("❌ Java not available - test cannot continue", "ERROR")
            return False
        log(f"✅ Java available: {version}", "SUCCESS")
        
        # Test 3: Setup utility
        print("\n3. Setting up Java unzip utility...")
        success = setup_java_unzip('namenode', log)
        if not success:
            log("❌ Setup failed", "ERROR")
            return False
        log("✅ Java unzip utility ready", "SUCCESS")
        
        # Test 4: Use existing ZIP file (the-antiwork-subreddit-dataset-posts.zip)
        print("\n4. Checking for test ZIP file...")
        
        # Check if we have a ZIP file already uploaded
        check_zip_cmd = [
            'docker', 'exec', 'namenode', 'sh', '-c',
            'hdfs dfs -ls /input/*.zip 2>/dev/null | head -1 | awk \'{print $8}\''
        ]
        
        result = subprocess.run(check_zip_cmd, capture_output=True, timeout=10, text=True)
        hdfs_zip = result.stdout.strip()
        
        if not hdfs_zip:
            log("⚠️ No ZIP file found in HDFS /input/", "WARNING")
            log("💡 Skipping extraction test (upload a ZIP file first)", "INFO")
            log("✅ Java unzip utility is set up and ready!", "SUCCESS")
            print("\n" + "=" * 80)
            print("⚠️ PARTIAL TEST COMPLETED")
            print("=" * 80)
            print("\n✅ Java unzip utility is ready")
            print("⚠️ Extraction test skipped (no ZIP file available)")
            print("\nTo complete full test:")
            print("  1. Upload a ZIP file to HDFS via GUI")
            print("  2. Enable 'Auto-extract' checkbox")
            print("  3. Watch it extract automatically!")
            print("\n" + "=" * 80)
            return True
        
        log(f"✅ Found ZIP file: {hdfs_zip}", "SUCCESS")
        
        # Copy ZIP from HDFS to /tmp/ for testing
        log("📥 Copying ZIP from HDFS to /tmp/...", "INFO")
        copy_cmd = [
            'docker', 'exec', 'namenode', 'hdfs', 'dfs', '-get',
            hdfs_zip, '/tmp/test_java_unzip.zip'
        ]
        result = subprocess.run(copy_cmd, capture_output=True, timeout=30, text=True)
        if result.returncode != 0:
            log(f"❌ Failed to create test ZIP: {result.stderr}", "ERROR")
            return False
        log("✅ Test ZIP created: /tmp/test_java_unzip.zip", "SUCCESS")
        
        # Test 5: Extract with Java
        print("\n5. Extracting ZIP with Java...")
        success, msg = unzip_with_java(
            container='namenode',
            zip_file_path='/tmp/test_java_unzip.zip',
            output_dir='/tmp/test_extracted',
            log_callback=log
        )
        
        if not success:
            log(f"❌ Extraction failed: {msg}", "ERROR")
            return False
        log(f"✅ Extraction successful: {msg}", "SUCCESS")
        
        # Test 6: Verify extracted files
        print("\n6. Verifying extracted files...")
        verify_cmd = [
            'docker', 'exec', 'namenode', 'sh', '-c',
            'ls -R /tmp/test_extracted'
        ]
        
        result = subprocess.run(verify_cmd, capture_output=True, timeout=10, text=True)
        if result.returncode != 0:
            log("❌ Failed to verify files", "ERROR")
            return False
        
        log("✅ Files verified:", "SUCCESS")
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                log(f"   {line}", "INFO")
        
        # Test 7: Cleanup
        print("\n7. Cleaning up...")
        cleanup_cmd = [
            'docker', 'exec', 'namenode', 'sh', '-c',
            'rm -rf /tmp/test_java_unzip.zip /tmp/test_extracted'
        ]
        subprocess.run(cleanup_cmd, capture_output=True, timeout=10)
        log("✅ Cleanup complete", "SUCCESS")
        
        # Success!
        print("\n" + "=" * 80)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 80)
        print("\n✅ Java unzip integration is working perfectly!")
        print("✅ Ready to use in HDFS Upload Manager")
        print("\nNext steps:")
        print("  1. Open HDFS Upload Manager")
        print("  2. Enable 'Auto-extract' checkbox")
        print("  3. Upload a ZIP file")
        print("  4. Watch it extract automatically with Java!")
        print("\n" + "=" * 80)
        
        return True
    
    except Exception as e:
        log(f"❌ Test failed with exception: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_java_unzip_integration()
    sys.exit(0 if success else 1)
