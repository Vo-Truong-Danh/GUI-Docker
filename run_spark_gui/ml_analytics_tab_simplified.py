"""
ML Analytics Tab - Simplified Version
Chỉ load data từ /tmp và mở HTML dashboard
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os

class MLAnalyticsTab:
    """Simplified ML Analytics Tab - Load results and show dashboard"""
    
    def __init__(self, parent_frame, config, status_callback=None, log_callback=None):
        self.parent = parent_frame
        self.config = config
        self.update_status = status_callback or (lambda x: None)
        self.append_log = log_callback or (lambda x: None)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Create simplified UI"""
        main_container = ttk.Frame(self.parent)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title = ttk.Label(main_container, text="📊 ML Analytics Dashboard", 
                         font=('Segoe UI', 14, 'bold'))
        title.pack(pady=10)
        
        # Info section
        info_frame = ttk.LabelFrame(main_container, text="ℹ️ Thông Tin", padding=10)
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(info_frame, text="Chạy phân tích từ Spark Runner Tab trước", 
                 font=('Segoe UI', 9)).pack(anchor=tk.W)
        ttk.Label(info_frame, text="• File kết quả: /tmp/ml_analysis_summary.json", 
                 font=('Segoe UI', 9)).pack(anchor=tk.W)
        ttk.Label(info_frame, text="• File biểu đồ: /tmp/ml_analysis_results.png", 
                 font=('Segoe UI', 9)).pack(anchor=tk.W)
        ttk.Label(info_frame, text="• Dashboard sẽ auto-load kết quả khi có sẵn", 
                 font=('Segoe UI', 9)).pack(anchor=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="🌐 Mở Dashboard", 
                  command=self.open_dashboard).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Làm mới", 
                  command=self.refresh_dashboard).pack(side=tk.LEFT, padx=5)
        
        # Console
        console_frame = ttk.LabelFrame(main_container, text="📝 Console Output", padding=5)
        console_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.console = scrolledtext.ScrolledText(console_frame, height=15, 
                                                 font=('Courier', 9), bg='#1e1e1e', 
                                                 fg='#00ff00', wrap=tk.WORD)
        self.console.pack(fill=tk.BOTH, expand=True)
        self.console.config(state=tk.DISABLED)
        
        self.log_message("info", "✅ ML Analytics Tab Initialized")
        self.log_message("info", "📌 Hướng dẫn:")
        self.log_message("info", "  1. Chạy analysis từ Spark Runner tab")
        self.log_message("info", "  2. Dữ liệu sẽ lưu vào /tmp/ml_analysis_summary.json")
        self.log_message("info", "  3. Click 'Mở Dashboard' để view biểu đồ")
    
    def log_message(self, level, message):
        """Log message to console"""
        colors = {
            'info': 'info',
            'success': 'success', 
            'error': 'error',
            'warning': 'warning'
        }
        
        # Format message with color tags
        self.console.config(state=tk.NORMAL)
        
        if level == 'error':
            self.console.insert(tk.END, f"❌ {message}\n", 'error')
        elif level == 'success':
            self.console.insert(tk.END, f"✅ {message}\n", 'success')
        elif level == 'warning':
            self.console.insert(tk.END, f"⚠️ {message}\n", 'warning')
        else:
            self.console.insert(tk.END, f"ℹ️ {message}\n", 'info')
        
        self.console.see(tk.END)
        self.console.config(state=tk.DISABLED)
    
    def open_dashboard(self):
        """Open ML Analytics Dashboard in browser"""
        try:
            from html_dashboard_helper import HTMLDashboardHelper
            helper = HTMLDashboardHelper()
            helper.open_dashboard()
            self.log_message("success", "Dashboard mở thành công!")
        except Exception as e:
            self.log_message("error", f"Lỗi: {e}")
            messagebox.showerror("Lỗi", f"Không thể mở dashboard:\n{str(e)}")
    
    def refresh_dashboard(self):
        """Refresh dashboard in browser"""
        self.log_message("info", "🔄 Làm mới dashboard...")
        self.open_dashboard()


# Export
__all__ = ['MLAnalyticsTab']
