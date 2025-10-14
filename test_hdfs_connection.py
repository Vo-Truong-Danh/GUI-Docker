#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test HDFS Connection and List Files
"""

import subprocess
import sys

def test_hdfs_connection():
    """Test HDFS connection"""
    print("="*70)
    print("  Testing HDFS Connection")
    print("="*70)
    print()
    
    # Test 1: Check namenode container
    print("1️⃣  Checking namenode container...")
    try:
        result = subprocess.run(
            "docker ps --filter name=namenode --format '{{.Names}}: {{.Status}}'",
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and result.stdout.strip():
            print(f"   ✅ {result.stdout.strip()}")
        else:
            print("   ❌ Namenode container not found!")
            print("   💡 Start Docker: docker-compose up -d")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print()
    
    # Test 2: List HDFS root
    print("2️⃣  Listing HDFS root directory...")
    try:
        result = subprocess.run(
            "docker exec namenode hdfs dfs -ls /",
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("   ✅ HDFS is accessible!")
            print()
            print("   📁 Files in HDFS root:")
            print("   " + "-"*66)
            
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                for line in lines[1:]:  # Skip header
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 8:
                            permissions = parts[0]
                            size = parts[4]
                            name = parts[7]
                            is_dir = permissions.startswith('d')
                            icon = "📁" if is_dir else "📄"
                            print(f"   {icon} {name} ({size if not is_dir else 'DIR'})")
            else:
                print("   ⚠️  No files found in HDFS root")
            
            print("   " + "-"*66)
        else:
            print(f"   ❌ HDFS error: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print()
    
    # Test 3: List /input directory (common for PySpark examples)
    print("3️⃣  Listing /input directory...")
    try:
        result = subprocess.run(
            "docker exec namenode hdfs dfs -ls /input",
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("   ✅ /input directory exists!")
            print()
            print("   📁 Files in /input:")
            print("   " + "-"*66)
            
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                for line in lines[1:]:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 8:
                            permissions = parts[0]
                            size = parts[4]
                            name = os.path.basename(parts[7])
                            is_dir = permissions.startswith('d')
                            icon = "📁" if is_dir else "📄"
                            print(f"   {icon} {name} ({size if not is_dir else 'DIR'})")
            else:
                print("   ⚠️  No files in /input")
            
            print("   " + "-"*66)
        else:
            print("   ⚠️  /input directory not found")
            print("   💡 Create it: docker exec namenode hdfs dfs -mkdir /input")
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
    
    print()
    print("="*70)
    print("✅ HDFS Connection Test Complete!")
    print("="*70)
    
    return True

if __name__ == "__main__":
    import os
    
    success = test_hdfs_connection()
    
    if success:
        print()
        print("🎉 HDFS is working! You can now use the HDFS Browser in GUI.")
        print()
        print("Next steps:")
        print("1. Open GUI: python main.py")
        print("2. Go to 'AI Engine V8.3' tab")
        print("3. Click 'Browse' to select HDFS files")
        print("4. Generate PySpark code!")
    else:
        print()
        print("❌ HDFS connection failed!")
        print()
        print("Troubleshooting:")
        print("1. Check Docker: docker ps")
        print("2. Start containers: docker-compose up -d")
        print("3. Wait 30 seconds for HDFS to initialize")
        print("4. Run this test again")
    
    sys.exit(0 if success else 1)
