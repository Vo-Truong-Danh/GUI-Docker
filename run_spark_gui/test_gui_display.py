"""
Minimal test to see if GUI actually appears
"""
import tkinter as tk
from tkinter import ttk
import sys

print("=" * 60)
print("Testing Basic GUI Display")
print("=" * 60)

def test_basic_window():
    """Test if a basic window can appear"""
    print("\n[Test 1] Creating root window...")
    root = tk.Tk()
    root.title("Test Window")
    root.geometry("400x300")
    
    print("[Test 1] Adding label...")
    label = tk.Label(root, text="If you see this window, GUI works!", font=('Arial', 14))
    label.pack(pady=50)
    
    button = tk.Button(root, text="Close", command=root.destroy)
    button.pack(pady=20)
    
    print("[Test 1] ✅ Window created! Check your screen.")
    print("[Test 1] Window should auto-close in 3 seconds...")
    
    root.after(3000, root.destroy)  # Auto close after 3 seconds
    root.mainloop()
    print("[Test 1] ✅ Window closed successfully")

def test_full_app():
    """Test if main.py can run"""
    print("\n[Test 2] Running main.py...")
    try:
        import main
        print("[Test 2] ✅ main.py imported successfully")
    except Exception as e:
        print(f"[Test 2] ❌ Failed to import main.py: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("\nStarting GUI tests...")
    print("=" * 60)
    
    # Test 1: Basic window
    test_basic_window()
    
    print("\n" + "=" * 60)
    print("✅ GUI test completed!")
    print("=" * 60)
