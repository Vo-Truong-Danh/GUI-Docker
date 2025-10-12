"""
HDFS Upload Tab - Quick Test Script
Tests the enhanced logging and config management features
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hdfs_upload_tab_v4_clean import HDFSUploadTabV4Clean

def main():
    """Run quick test of HDFS Upload tab"""
    
    # Create root window
    root = tk.Tk()
    root.title("HDFS Upload - Quick Test")
    root.geometry("1200x800")
    
    # Create main frame
    main_frame = ttk.Frame(root, padding=10)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Status bar
    status_var = tk.StringVar(value="Ready")
    status_bar = ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    # Log area (for testing log callback)
    log_frame = ttk.LabelFrame(root, text="Main Log", padding=5)
    log_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
    
    log_text = tk.Text(log_frame, height=8, wrap=tk.WORD, font=('Consolas', 8))
    log_text.pack(fill=tk.BOTH, expand=True)
    
    def log_callback(message):
        """Callback for main log"""
        log_text.insert(tk.END, message)
        log_text.see(tk.END)
    
    def status_callback(message):
        """Callback for status bar"""
        status_var.set(message)
    
    # Test config
    test_config = {
        'hdfs_container': 'namenode',
        'hdfs_path': '/user/spark/data',
        'auto_extract': True
    }
    
    # Create HDFS Upload tab
    print("Creating HDFS Upload tab...")
    hdfs_tab = HDFSUploadTabV4Clean(
        parent_frame=main_frame,
        config=test_config,
        status_callback=status_callback,
        log_callback=log_callback
    )
    
    print("✓ Tab created successfully!")
    print("\n" + "="*60)
    print("HDFS UPLOAD TAB - QUICK TEST")
    print("="*60)
    print("\n📋 Test Checklist:")
    print("  1. ✅ Check log shows config file path on startup")
    print("  2. ✅ Click 'Test' button - see detailed logging")
    print("  3. ✅ Click 'Add Files' - see files added with names")
    print("  4. ✅ Click 'Save Config' - see absolute path in dialog")
    print("  5. ✅ Check timestamp on all log messages")
    print("\n💡 Expected Log Format:")
    print("  [HH:MM:SS] 📤 HDFS Upload Manager ready")
    print("  [HH:MM:SS] 📁 Config file: D:\\...\\spark_runner_config.json")
    print("\n🔍 Features to Test:")
    print("  • Timestamp on every log entry")
    print("  • Config file path display")
    print("  • Detailed button click logging")
    print("  • Step-by-step upload progress")
    print("  • Error messages with context")
    print("\n" + "="*60 + "\n")
    
    # Run
    root.mainloop()

if __name__ == '__main__':
    main()
