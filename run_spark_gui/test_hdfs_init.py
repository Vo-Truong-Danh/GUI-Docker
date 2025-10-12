"""
Simple test to check HDFSUploadTabV4Clean initialization
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("HDFSUploadTabV4Clean Initialization Test")
print("=" * 60)

try:
    print("\n1. Importing module...")
    from hdfs_upload_tab_v4_clean import HDFSUploadTabV4Clean
    print("   ✓ Import successful")
    
    print("\n2. Creating Tkinter root...")
    root = tk.Tk()
    root.title("Test")
    root.geometry("800x600")
    print("   ✓ Root created")
    
    print("\n3. Creating frame...")
    frame = ttk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True)
    print("   ✓ Frame created")
    
    print("\n4. Preparing config...")
    test_config = {
        'hdfs_container': 'namenode',
        'hdfs_path': '/input',
        'auto_extract': True
    }
    print("   ✓ Config ready")
    
    print("\n5. Creating HDFSUploadTabV4Clean instance...")
    tab = HDFSUploadTabV4Clean(
        parent_frame=frame,
        config=test_config,
        status_callback=lambda msg: print(f"   [STATUS] {msg}"),
        log_callback=lambda msg: print(f"   [LOG] {msg}")
    )
    print("   ✓ Instance created")
    
    print("\n6. Checking attributes...")
    attrs_to_check = ['frame', 'config', 'log_text', 'container_var', 'path_var', 
                     'status_badge', 'thread_pool', 'selected_files']
    
    for attr in attrs_to_check:
        if hasattr(tab, attr):
            value = getattr(tab, attr)
            print(f"   ✓ {attr}: {type(value).__name__}")
        else:
            print(f"   ❌ {attr}: NOT FOUND")
    
    print("\n7. Testing log method...")
    try:
        tab.log("Test message", 'info')
        print("   ✓ log() method works")
    except Exception as e:
        print(f"   ❌ log() failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n8. Testing container_var...")
    try:
        container = tab.container_var.get()
        print(f"   ✓ container_var.get() = '{container}'")
    except Exception as e:
        print(f"   ❌ container_var.get() failed: {str(e)}")
    
    print("\n9. Simulating Test button click...")
    try:
        tab.test_connection()
        print("   ✓ test_connection() called")
        print("   → Check console output above for execution details")
    except Exception as e:
        print(f"   ❌ test_connection() failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ Initialization test complete!")
    print("=" * 60)
    print("\n🔍 If test_connection() logged steps, the tab is working!")
    print("   Close window to exit...")
    
    # Keep window open
    root.mainloop()
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    print("\n" + "=" * 60)
