"""
Quick test for logging functionality
"""
import tkinter as tk
from tkinter import ttk
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from spark_runner_tab import SparkRunnerTab
from theme import COLORS

def test_logging():
    """Test logging with simple UI"""
    root = tk.Tk()
    root.title("Test Logging")
    root.geometry("800x600")
    
    # Create a frame
    frame = ttk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True)
    
    # Mock config and callbacks
    config = {
        'container': 'spark-worker',
        'master': 'spark://spark-master:7077',
        'history': []
    }
    
    def mock_update_status(msg):
        print(f"Status: {msg}")
    
    def mock_append_log(msg, tag='info', widget=None):
        print(f"Log [{tag}]: {msg}")
    
    callbacks = {
        'update_status': mock_update_status,
        'append_log': mock_append_log,
        'add_to_history': lambda c, f: None,
        'save_config': lambda c: None,
        'load_config': lambda: config,
        'get_version': lambda: "2.5.0"
    }
    
    # Create SparkRunnerTab
    spark_runner = SparkRunnerTab(frame, config, COLORS, callbacks)
    spark_runner.root = root
    
    # Start log processor
    print("Starting log processor...")
    spark_runner._start_log_processor()
    
    # Test logging after 1 second
    def test_logs():
        print("\n=== Testing logs ===")
        spark_runner.append_log("Test message 1", "info")
        spark_runner.append_log("Test message 2 - Success", "success")
        spark_runner.append_log("Test message 3 - Warning", "warning")
        spark_runner.append_log("Test message 4 - Error", "error")
        print("=== Logs sent to queue ===")
        
        # Schedule another test
        root.after(2000, lambda: spark_runner.append_log("Delayed message after 2s", "info"))
        
        # Close after 5 seconds
        root.after(5000, lambda: (print("\n✅ Logging test complete!"), root.quit()))
    
    # Start testing after UI is ready
    root.after(1000, test_logs)
    
    print("Starting UI...")
    root.mainloop()

if __name__ == '__main__':
    try:
        test_logging()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
