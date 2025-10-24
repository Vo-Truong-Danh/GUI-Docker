"""
Dashboard Tab - Trực quan hóa kết quả phân tích Big Data
Tích hợp vào GUI chính bằng tkinter.simpledialog và webbrowser
"""

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import os
import sys
import threading
import time
import http.server
import socketserver
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

class DashboardTab:
    def __init__(self, parent_frame, config=None, status_callback=None, log_callback=None):
        """
        Initialize Dashboard Tab
        
        Args:
            parent_frame: Parent tkinter frame
            config: Application config dictionary
            status_callback: Callback to update status
            log_callback: Callback to append logs
        """
        self.parent = parent_frame
        self.config = config or {}
        self.status_callback = status_callback or (lambda x: None)
        self.log_callback = log_callback or (lambda x: None)
        
        self.server_thread = None
        self.server_running = False
        self.httpd = None
        self.port = 8000
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dashboard UI"""
        # Main frame
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="📊 Dashboard - Big Data Analytics",
            font=('Segoe UI', 16, 'bold'),
            fg='#0969DA'
        )
        title_label.pack(pady=10)
        
        # Info box
        info_frame = tk.Frame(main_frame, bg='#E6F2FF', relief=tk.SOLID, bd=1)
        info_frame.pack(fill=tk.X, pady=10)
        
        info_text = tk.Label(
            info_frame,
            text="✅ Tự động khởi động server khi cần\n"
                 "📍 Truy cập: http://localhost:8000/unified_dashboard.html\n"
                 "💾 File dữ liệu: tmp/ml_analysis_summary.json",
            font=('Segoe UI', 10),
            bg='#E6F2FF',
            fg='#004085',
            justify=tk.LEFT
        )
        info_text.pack(pady=10, padx=10)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        # Start Server button
        self.start_btn = tk.Button(
            button_frame,
            text="🚀 Khởi Động Server",
            command=self.start_server,
            font=('Segoe UI', 11, 'bold'),
            bg='#28a745',
            fg='white',
            padx=20,
            pady=10,
            relief=tk.SOLID,
            bd=1
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        # Open Dashboard button
        self.open_btn = tk.Button(
            button_frame,
            text="🌐 Mở Dashboard",
            command=self.open_dashboard,
            font=('Segoe UI', 11, 'bold'),
            bg='#0969DA',
            fg='white',
            padx=20,
            pady=10,
            relief=tk.SOLID,
            bd=1,
            state=tk.DISABLED
        )
        self.open_btn.pack(side=tk.LEFT, padx=5)
        
        # Stop Server button
        self.stop_btn = tk.Button(
            button_frame,
            text="⏹️  Dừng Server",
            command=self.stop_server,
            font=('Segoe UI', 11, 'bold'),
            bg='#dc3545',
            fg='white',
            padx=20,
            pady=10,
            relief=tk.SOLID,
            bd=1,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Copy Images button
        self.copy_btn = tk.Button(
            button_frame,
            text="📥 Copy Ảnh từ Container",
            command=self.copy_images_from_container,
            font=('Segoe UI', 11, 'bold'),
            bg='#6C63FF',
            fg='white',
            padx=20,
            pady=10,
            relief=tk.SOLID,
            bd=1
        )
        self.copy_btn.pack(side=tk.LEFT, padx=5)
        
        # Refresh Dashboard button
        self.refresh_btn = tk.Button(
            button_frame,
            text="🔄 Làm mới Dashboard",
            command=self.refresh_dashboard,
            font=('Segoe UI', 11, 'bold'),
            bg='#17A2B8',
            fg='white',
            padx=20,
            pady=10,
            relief=tk.SOLID,
            bd=1
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Status frame
        status_frame = tk.Frame(main_frame, bg='#F8F9FA', relief=tk.SOLID, bd=1)
        status_frame.pack(fill=tk.X, pady=10)
        
        self.status_label = tk.Label(
            status_frame,
            text="⚪ Server: Chưa khởi động",
            font=('Segoe UI', 10),
            bg='#F8F9FA',
            fg='#666',
            justify=tk.LEFT
        )
        self.status_label.pack(pady=10, padx=10, anchor=tk.W)
        
        # Log frame
        log_label = tk.Label(main_frame, text="📋 Logs:", font=('Segoe UI', 10, 'bold'))
        log_label.pack(anchor=tk.W, pady=(20, 5))
        
        # Log text widget with scrollbar
        log_frame = tk.Frame(main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = tk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(
            log_frame,
            height=10,
            font=('Courier New', 9),
            bg='#1E1E1E',
            fg='#00FF00',
            yscrollcommand=scrollbar.set
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)
        
        self.append_log("✅ Dashboard Tab Initialized", "success")
    
    def append_log(self, message, level="info"):
        """Append message to log widget"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color codes
        color_map = {
            "info": "#0F0",      # Green
            "success": "#0F0",   # Green
            "warning": "#FF0",   # Yellow
            "error": "#F00",     # Red
            "debug": "#0FF"      # Cyan
        }
        
        color_tag = f"color_{level}"
        self.log_text.tag_configure(color_tag, foreground=color_map.get(level, "#0F0"))
        
        log_line = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_line, color_tag)
        self.log_text.see(tk.END)
        self.log_text.update()
    
    def update_status(self, message):
        """Update status label"""
        self.status_label.config(text=message)
        self.status_label.update()
    
    def start_server(self):
        """Start HTTP server in background thread"""
        if self.server_running:
            messagebox.showinfo("Info", "Server đã chạy!")
            return
        
        self.append_log("🚀 Đang khởi động server...", "info")
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        # Start server in background thread
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
    
    def _run_server(self):
        """Run HTTP server (in background thread)"""
        try:
            # Get directory path - serve from parent directory (GUI-Docker folder)
            directory = str(Path(__file__).parent.parent)
            
            # Create handler
            class MyHandler(http.server.SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, directory=directory, **kwargs)
                
                def log_message(self, format, *args):
                    # Custom logging
                    msg = f"[HTTP] {format % args}"
                    self.server.dashboard_tab.append_log(msg, "debug")
            
            # Create server
            self.httpd = socketserver.TCPServer(("", self.port), MyHandler)
            self.httpd.dashboard_tab = self
            self.server_running = True
            
            self.update_status(f"🟢 Server: Chạy tại http://localhost:{self.port}")
            self.append_log(f"✅ Server khởi động thành công!", "success")
            self.append_log(f"📍 Dashboard URL: http://localhost:{self.port}/unified_dashboard.html", "success")
            self.append_log(f"📁 Thư mục phục vụ: {directory}", "info")
            self.append_log(f"📊 Dữ liệu từ: {directory}/tmp/", "info")
            self.open_btn.config(state=tk.NORMAL)
            
            # Serve requests (blocking)
            self.httpd.serve_forever()
            
        except Exception as e:
            self.server_running = False
            self.update_status(f"🔴 Server: Lỗi - {str(e)}")
            self.append_log(f"❌ Lỗi khởi động server: {str(e)}", "error")
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.open_btn.config(state=tk.DISABLED)
    
    def open_dashboard(self):
        """Open dashboard in browser"""
        url = f"http://localhost:{self.port}/unified_dashboard.html"
        try:
            self.append_log(f"🌐 Mở dashboard tại {url}...", "info")
            webbrowser.open(url)
            self.append_log("✅ Unified Dashboard mở trong trình duyệt", "success")
        except Exception as e:
            self.append_log(f"❌ Lỗi mở dashboard: {str(e)}", "error")
            messagebox.showerror("Error", f"Không thể mở dashboard:\n{str(e)}")
    
    def stop_server(self):
        """Stop HTTP server"""
        if not self.server_running:
            messagebox.showinfo("Info", "Server chưa chạy!")
            return
        
        self.append_log("⏹️  Đang dừng server...", "warning")
        self.stop_btn.config(state=tk.DISABLED)
        
        try:
            if self.httpd:
                self.httpd.shutdown()
                self.httpd.server_close()
                self.server_running = False
            
            self.update_status("⚪ Server: Dừng")
            self.append_log("✅ Server dừng thành công", "success")
            self.start_btn.config(state=tk.NORMAL)
            self.open_btn.config(state=tk.DISABLED)
        except Exception as e:
            self.append_log(f"❌ Lỗi dừng server: {str(e)}", "error")
    
    def cleanup(self):
        """Cleanup when tab closes"""
        if self.server_running:
            self.stop_server()
    
    def refresh_dashboard(self):
        """Refresh dashboard in browser (clear cache)"""
        if not self.server_running:
            messagebox.showinfo("Info", "Server chưa chạy! Hãy khởi động trước")
            return
        
        url = f"http://localhost:{self.port}/unified_dashboard.html?nocache={int(time.time())}"
        try:
            self.append_log("🔄 Làm mới dashboard trong browser...", "info")
            webbrowser.open(url)
            self.append_log("✅ Dashboard đã được làm mới", "success")
        except Exception as e:
            self.append_log(f"❌ Lỗi: {str(e)}", "error")
    
    def copy_images_from_container(self):
        """Copy ML result images from Docker container to host machine"""
        self.append_log("📥 Bắt đầu copy ảnh từ container...", "info")
        self.copy_btn.config(state=tk.DISABLED)
        
        # Run in thread to avoid blocking UI
        thread = threading.Thread(target=self._copy_images_thread, daemon=True)
        thread.start()
    
    def _copy_images_thread(self):
        """Background thread to copy images"""
        try:
            # Get project root directory
            project_root = str(Path(__file__).parent.parent)
            tmp_dir = os.path.join(project_root, "tmp")
            
            # Create tmp directory if not exists
            os.makedirs(tmp_dir, exist_ok=True)
            self.append_log(f"📂 Thư mục đích: {tmp_dir}", "info")
            
            # Get list of running containers
            result = subprocess.run(
                ["docker", "ps", "--quiet"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                self.append_log("❌ Docker không khả dụng hoặc không có container chạy", "error")
                self.copy_btn.config(state=tk.NORMAL)
                return
            
            containers = result.stdout.strip().split('\n')
            
            if not containers or not containers[0]:
                self.append_log("❌ Không có container nào đang chạy", "error")
                self.copy_btn.config(state=tk.NORMAL)
                return
            
            # Try to copy from each container
            copied_count = 0
            container_found = False
            
            for container_id in containers:
                if not container_id.strip():
                    continue
                
                try:
                    # Get container name
                    name_result = subprocess.run(
                        ["docker", "ps", "--filter", f"id={container_id}", "--format", "{{.Names}}"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    container_name = name_result.stdout.strip()
                    
                    # Check if images exist in container using find command (more reliable)
                    check_cmd = 'find /tmp -name "ml_result_*.png" -type f'
                    result = subprocess.run(
                        ["docker", "exec", container_id, "sh", "-c", check_cmd],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    found_files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
                    
                    if found_files:
                        container_found = True
                        self.append_log(f"🐳 Tìm thấy {len(found_files)} ảnh trong container: {container_name}", "success")
                        
                        # Copy each file individually
                        for src_path in found_files:
                            try:
                                filename = os.path.basename(src_path)
                                dst_path = os.path.join(tmp_dir, filename)
                                
                                # Copy using docker cp
                                copy_result = subprocess.run(
                                    ["docker", "cp", f"{container_id}:{src_path}", dst_path],
                                    capture_output=True,
                                    text=True,
                                    timeout=15
                                )
                                
                                if copy_result.returncode == 0 and os.path.exists(dst_path):
                                    file_size = os.path.getsize(dst_path)
                                    self.append_log(f"   ✓ {filename} ({file_size/1024:.1f} KB)", "success")
                                    copied_count += 1
                                else:
                                    self.append_log(f"   ⚠ {filename}: {copy_result.stderr}", "warning")
                            except Exception as e:
                                self.append_log(f"   ⚠ {filename}: {str(e)}", "warning")
                        
                        break
                
                except Exception as e:
                    self.append_log(f"⚠ Lỗi kiểm tra container {container_name}: {str(e)}", "warning")
                    continue
            
            if not container_found:
                self.append_log("⚠ Không tìm thấy ảnh trong bất kỳ container nào", "warning")
                self.append_log("💡 Hãy chạy code phân tích trong container trước", "info")
            elif copied_count > 0:
                self.append_log(f"✅ Đã copy {copied_count} ảnh thành công!", "success")
                self.append_log(f"📍 Vị trí: {tmp_dir}", "success")
                self.append_log(f"🔄 Reload browser để xem ảnh (hoặc nhấn F5)", "info")
            else:
                self.append_log(f"❌ Không copy được ảnh nào. Kiểm tra quyền Docker", "error")
            
        except Exception as e:
            self.append_log(f"❌ Lỗi copy ảnh: {str(e)}", "error")
        
        finally:
            self.copy_btn.config(state=tk.NORMAL)
