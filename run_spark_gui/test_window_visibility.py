"""
Force window to appear on top
"""
import tkinter as tk
from tkinter import ttk
import sys
import os

# Add run_spark_gui to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_simple_app():
    """Create minimal app to test display"""
    root = tk.Tk()
    root.title("Test - Spark Runner")
    root.geometry("600x400")
    
    # Force window to top
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    
    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Content
    frame = tk.Frame(root, bg='white')
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    title = tk.Label(frame, text="🎉 Cửa sổ test hiển thị OK!", 
                     font=('Segoe UI', 16, 'bold'), bg='white', fg='#0969DA')
    title.pack(pady=20)
    
    msg = tk.Label(frame, text="Nếu bạn thấy cửa sổ này, nghĩa là Tkinter hoạt động tốt.\n\n"
                               "Vấn đề có thể là ứng dụng chính khởi tạo quá lâu.\n\n"
                               "Hãy chờ thêm 10-15 giây khi chạy main.py",
                   font=('Segoe UI', 11), bg='white', justify=tk.LEFT)
    msg.pack(pady=20)
    
    btn = tk.Button(frame, text="Đóng", command=root.destroy,
                    font=('Segoe UI', 10), bg='#0969DA', fg='white',
                    padx=20, pady=10)
    btn.pack(pady=20)
    
    print("✅ Test window created and should be visible on top")
    root.mainloop()

if __name__ == '__main__':
    create_simple_app()
