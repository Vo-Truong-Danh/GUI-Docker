"""
Advanced Monitoring Dashboard Tab - Giám sát hệ thống nâng cao
Version: 1.0.0
Date: 2025-10-13

Features:
- Real-time system metrics
- Docker container monitoring
- Spark job tracking
- Resource usage graphs
- Alert management
- Historical data
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import subprocess


class MonitoringDashboard(ttk.Frame):
    """
    Tab giám sát hệ thống nâng cao với real-time updates
    """
    
    def __init__(self, parent, theme=None):
        super().__init__(parent)
        self.theme = theme
        
        # Monitoring state
        self.monitoring_active = False
        self.monitor_thread = None
        self.update_interval = 2000  # ms
        
        # Data storage
        self.metrics_history: List[Dict] = []
        self.max_history = 100
        
        # Create UI
        self._create_ui()
        
    def _create_ui(self):
        """Tạo giao diện"""
        
        # Main container with padding
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_frame = ttk.Frame(container)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title = ttk.Label(
            title_frame,
            text="📊 Advanced Monitoring Dashboard",
            font=('Segoe UI', 16, 'bold')
        )
        title.pack(side=tk.LEFT)
        
        # Control buttons
        btn_frame = ttk.Frame(title_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        self.start_btn = ttk.Button(
            btn_frame,
            text="▶️ Start Monitoring",
            command=self._start_monitoring,
            width=18
        )
        self.start_btn.pack(side=tk.LEFT, padx=2)
        
        self.stop_btn = ttk.Button(
            btn_frame,
            text="⏹️ Stop Monitoring",
            command=self._stop_monitoring,
            state=tk.DISABLED,
            width=18
        )
        self.stop_btn.pack(side=tk.LEFT, padx=2)
        
        refresh_btn = ttk.Button(
            btn_frame,
            text="🔄 Refresh",
            command=self._refresh_data,
            width=12
        )
        refresh_btn.pack(side=tk.LEFT, padx=2)
        
        # Create notebook for different monitoring sections
        notebook = ttk.Notebook(container)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # System Resources Tab
        self.system_tab = ttk.Frame(notebook)
        notebook.add(self.system_tab, text="💻 System Resources")
        self._create_system_tab()
        
        # Docker Containers Tab
        self.docker_tab = ttk.Frame(notebook)
        notebook.add(self.docker_tab, text="🐳 Docker Containers")
        self._create_docker_tab()
        
        # Spark Jobs Tab
        self.spark_tab = ttk.Frame(notebook)
        notebook.add(self.spark_tab, text="⚡ Spark Jobs")
        self._create_spark_tab()
        
        # Alerts Tab
        self.alerts_tab = ttk.Frame(notebook)
        notebook.add(self.alerts_tab, text="🔔 Alerts")
        self._create_alerts_tab()
        
        # Status bar
        self._create_status_bar(container)
    
    def _create_system_tab(self):
        """Tab giám sát tài nguyên hệ thống"""
        
        # CPU Section
        cpu_frame = ttk.LabelFrame(self.system_tab, text="CPU Usage", padding=10)
        cpu_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.cpu_label = ttk.Label(cpu_frame, text="CPU: N/A", font=('Segoe UI', 10))
        self.cpu_label.pack(anchor=tk.W)
        
        self.cpu_progress = ttk.Progressbar(
            cpu_frame,
            mode='determinate',
            length=400
        )
        self.cpu_progress.pack(fill=tk.X, pady=5)
        
        # Memory Section
        mem_frame = ttk.LabelFrame(self.system_tab, text="Memory Usage", padding=10)
        mem_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.mem_label = ttk.Label(mem_frame, text="Memory: N/A", font=('Segoe UI', 10))
        self.mem_label.pack(anchor=tk.W)
        
        self.mem_progress = ttk.Progressbar(
            mem_frame,
            mode='determinate',
            length=400
        )
        self.mem_progress.pack(fill=tk.X, pady=5)
        
        # Disk Section
        disk_frame = ttk.LabelFrame(self.system_tab, text="Disk Usage", padding=10)
        disk_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.disk_label = ttk.Label(disk_frame, text="Disk: N/A", font=('Segoe UI', 10))
        self.disk_label.pack(anchor=tk.W)
        
        self.disk_progress = ttk.Progressbar(
            disk_frame,
            mode='determinate',
            length=400
        )
        self.disk_progress.pack(fill=tk.X, pady=5)
        
        # Network Section
        net_frame = ttk.LabelFrame(self.system_tab, text="Network Activity", padding=10)
        net_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.net_text = tk.Text(net_frame, height=4, width=60, wrap=tk.WORD)
        self.net_text.pack(fill=tk.BOTH, expand=True)
        
    def _create_docker_tab(self):
        """Tab giám sát Docker containers"""
        
        # Toolbar
        toolbar = ttk.Frame(self.docker_tab)
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(
            toolbar,
            text="🔄 Refresh Containers",
            command=self._refresh_containers
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            toolbar,
            text="▶️ Start Selected",
            command=self._start_container
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            toolbar,
            text="⏹️ Stop Selected",
            command=self._stop_container
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            toolbar,
            text="📋 View Logs",
            command=self._view_container_logs
        ).pack(side=tk.LEFT, padx=2)
        
        # Container list
        list_frame = ttk.Frame(self.docker_tab)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Treeview
        columns = ('Container', 'Image', 'Status', 'CPU', 'Memory', 'Ports')
        self.container_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            height=12
        )
        
        for col in columns:
            self.container_tree.heading(col, text=col)
            if col == 'Container':
                self.container_tree.column(col, width=200)
            elif col == 'Image':
                self.container_tree.column(col, width=180)
            elif col == 'Status':
                self.container_tree.column(col, width=100)
            else:
                self.container_tree.column(col, width=80)
        
        # Scrollbars
        vsb = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                           command=self.container_tree.yview)
        hsb = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL,
                           command=self.container_tree.xview)
        self.container_tree.configure(yscrollcommand=vsb.set, 
                                     xscrollcommand=hsb.set)
        
        self.container_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
    
    def _create_spark_tab(self):
        """Tab giám sát Spark jobs"""
        
        # Summary
        summary_frame = ttk.LabelFrame(self.spark_tab, text="Job Summary", padding=10)
        summary_frame.pack(fill=tk.X, padx=10, pady=5)
        
        summary_text = ttk.Label(
            summary_frame,
            text="Total Jobs: 0 | Running: 0 | Completed: 0 | Failed: 0",
            font=('Segoe UI', 10)
        )
        summary_text.pack()
        self.spark_summary = summary_text
        
        # Job list
        list_frame = ttk.Frame(self.spark_tab)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ('Job ID', 'Name', 'Status', 'Started', 'Duration', 'Stages')
        self.spark_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            height=15
        )
        
        for col in columns:
            self.spark_tree.heading(col, text=col)
            if col == 'Job ID':
                self.spark_tree.column(col, width=80)
            elif col == 'Name':
                self.spark_tree.column(col, width=250)
            elif col == 'Status':
                self.spark_tree.column(col, width=100)
            else:
                self.spark_tree.column(col, width=120)
        
        vsb = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
                           command=self.spark_tree.yview)
        self.spark_tree.configure(yscrollcommand=vsb.set)
        
        self.spark_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_alerts_tab(self):
        """Tab quản lý alerts"""
        
        # Alert settings
        settings_frame = ttk.LabelFrame(self.alerts_tab, 
                                       text="Alert Thresholds", padding=10)
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # CPU threshold
        cpu_row = ttk.Frame(settings_frame)
        cpu_row.pack(fill=tk.X, pady=2)
        ttk.Label(cpu_row, text="CPU Alert (%):").pack(side=tk.LEFT)
        self.cpu_threshold = ttk.Spinbox(cpu_row, from_=50, to=100, width=10)
        self.cpu_threshold.set(80)
        self.cpu_threshold.pack(side=tk.LEFT, padx=5)
        
        # Memory threshold
        mem_row = ttk.Frame(settings_frame)
        mem_row.pack(fill=tk.X, pady=2)
        ttk.Label(mem_row, text="Memory Alert (%):").pack(side=tk.LEFT)
        self.mem_threshold = ttk.Spinbox(mem_row, from_=50, to=100, width=10)
        self.mem_threshold.set(85)
        self.mem_threshold.pack(side=tk.LEFT, padx=5)
        
        # Disk threshold
        disk_row = ttk.Frame(settings_frame)
        disk_row.pack(fill=tk.X, pady=2)
        ttk.Label(disk_row, text="Disk Alert (%):").pack(side=tk.LEFT)
        self.disk_threshold = ttk.Spinbox(disk_row, from_=50, to=100, width=10)
        self.disk_threshold.set(90)
        self.disk_threshold.pack(side=tk.LEFT, padx=5)
        
        # Alert history
        history_frame = ttk.LabelFrame(self.alerts_tab, text="Alert History", 
                                      padding=10)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.alert_text = tk.Text(history_frame, height=15, wrap=tk.WORD)
        alert_scroll = ttk.Scrollbar(history_frame, command=self.alert_text.yview)
        self.alert_text.configure(yscrollcommand=alert_scroll.set)
        
        self.alert_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        alert_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Clear button
        ttk.Button(
            history_frame,
            text="🗑️ Clear Alerts",
            command=lambda: self.alert_text.delete(1.0, tk.END)
        ).pack(pady=5)
    
    def _create_status_bar(self, parent):
        """Tạo status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
        
        self.status_label = ttk.Label(
            status_frame,
            text="⏸️ Monitoring: Stopped | Last Update: Never",
            font=('Segoe UI', 9)
        )
        self.status_label.pack(side=tk.LEFT)
        
        self.time_label = ttk.Label(
            status_frame,
            text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            font=('Segoe UI', 9)
        )
        self.time_label.pack(side=tk.RIGHT)
    
    # Control methods
    
    def _start_monitoring(self):
        """Bắt đầu monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitor_thread.start()
        
        self._log_alert("✅ Monitoring started")
        self._update_status("▶️ Monitoring: Active")
    
    def _stop_monitoring(self):
        """Dừng monitoring"""
        self.monitoring_active = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        self._log_alert("⏹️ Monitoring stopped")
        self._update_status("⏸️ Monitoring: Stopped")
    
    def _monitoring_loop(self):
        """Loop giám sát liên tục"""
        while self.monitoring_active:
            try:
                # Update all metrics
                self.after(0, self._update_system_metrics)
                self.after(0, self._refresh_containers)
                
                # Update status
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.after(0, lambda: self._update_status(
                    f"▶️ Monitoring: Active | Last Update: {timestamp}"
                ))
                self.after(0, lambda: self.time_label.config(text=timestamp))
                
                time.sleep(self.update_interval / 1000.0)
                
            except Exception as e:
                print(f"⚠️ Monitoring error: {e}")
                time.sleep(5)
    
    def _update_system_metrics(self):
        """Cập nhật system metrics"""
        try:
            # Get CPU usage
            try:
                import psutil
                cpu_percent = psutil.cpu_percent(interval=1)
                self.cpu_label.config(text=f"CPU: {cpu_percent:.1f}%")
                self.cpu_progress['value'] = cpu_percent
                
                # Check threshold
                if cpu_percent > float(self.cpu_threshold.get()):
                    self._log_alert(f"⚠️ HIGH CPU: {cpu_percent:.1f}%", 'warning')
                
                # Memory
                mem = psutil.virtual_memory()
                self.mem_label.config(
                    text=f"Memory: {mem.percent:.1f}% "
                         f"({mem.used / (1024**3):.1f} / {mem.total / (1024**3):.1f} GB)"
                )
                self.mem_progress['value'] = mem.percent
                
                if mem.percent > float(self.mem_threshold.get()):
                    self._log_alert(f"⚠️ HIGH MEMORY: {mem.percent:.1f}%", 'warning')
                
                # Disk
                disk = psutil.disk_usage('/')
                self.disk_label.config(
                    text=f"Disk: {disk.percent:.1f}% "
                         f"({disk.used / (1024**3):.1f} / {disk.total / (1024**3):.1f} GB)"
                )
                self.disk_progress['value'] = disk.percent
                
                if disk.percent > float(self.disk_threshold.get()):
                    self._log_alert(f"⚠️ HIGH DISK: {disk.percent:.1f}%", 'warning')
                
                # Network
                net_io = psutil.net_io_counters()
                net_info = (
                    f"Sent: {net_io.bytes_sent / (1024**2):.1f} MB | "
                    f"Received: {net_io.bytes_recv / (1024**2):.1f} MB\n"
                    f"Packets Sent: {net_io.packets_sent:,} | "
                    f"Packets Received: {net_io.packets_recv:,}"
                )
                self.net_text.delete(1.0, tk.END)
                self.net_text.insert(1.0, net_info)
                
            except ImportError:
                self.cpu_label.config(text="CPU: psutil not installed")
                self.mem_label.config(text="Memory: psutil not installed")
                self.disk_label.config(text="Disk: psutil not installed")
                
        except Exception as e:
            print(f"⚠️ Error updating metrics: {e}")
    
    def _refresh_containers(self):
        """Cập nhật danh sách containers"""
        try:
            result = subprocess.run(
                ['docker', 'ps', '-a', '--format', 
                 '{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            if result.returncode == 0:
                # Clear tree
                for item in self.container_tree.get_children():
                    self.container_tree.delete(item)
                
                # Add containers
                for line in result.stdout.strip().split('\n'):
                    if not line:
                        continue
                    
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        name = parts[0]
                        image = parts[1]
                        status = parts[2]
                        ports = parts[3] if len(parts) > 3 else ''
                        
                        # Get stats if running
                        cpu = mem = 'N/A'
                        if 'Up' in status:
                            # Try to get stats (simplified)
                            cpu = '~%'
                            mem = '~MB'
                        
                        self.container_tree.insert(
                            '',
                            tk.END,
                            values=(name, image, status, cpu, mem, ports)
                        )
        except Exception as e:
            print(f"⚠️ Error refreshing containers: {e}")
    
    def _refresh_data(self):
        """Manual refresh"""
        self._update_system_metrics()
        self._refresh_containers()
        self._log_alert("🔄 Data refreshed manually")
    
    def _start_container(self):
        """Start selected container"""
        selection = self.container_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a container")
            return
        
        item = self.container_tree.item(selection[0])
        container_name = item['values'][0]
        
        try:
            subprocess.run(
                ['docker', 'start', container_name],
                check=True,
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            self._log_alert(f"✅ Started container: {container_name}")
            self._refresh_containers()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start container:\n{e}")
    
    def _stop_container(self):
        """Stop selected container"""
        selection = self.container_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a container")
            return
        
        item = self.container_tree.item(selection[0])
        container_name = item['values'][0]
        
        try:
            subprocess.run(
                ['docker', 'stop', container_name],
                check=True,
                capture_output=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            self._log_alert(f"⏹️ Stopped container: {container_name}")
            self._refresh_containers()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop container:\n{e}")
    
    def _view_container_logs(self):
        """View logs của container được chọn"""
        selection = self.container_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a container")
            return
        
        item = self.container_tree.item(selection[0])
        container_name = item['values'][0]
        
        # Show logs in new window
        log_window = tk.Toplevel(self)
        log_window.title(f"Container Logs: {container_name}")
        log_window.geometry("800x600")
        
        text_widget = tk.Text(log_window, wrap=tk.WORD)
        scroll = ttk.Scrollbar(log_window, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scroll.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        try:
            result = subprocess.run(
                ['docker', 'logs', '--tail', '200', container_name],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            text_widget.insert(1.0, result.stdout)
            if result.stderr:
                text_widget.insert(tk.END, "\n=== STDERR ===\n" + result.stderr)
        except Exception as e:
            text_widget.insert(1.0, f"Error getting logs:\n{e}")
    
    def _log_alert(self, message: str, level: str = 'info'):
        """Ghi alert vào history"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}\n"
        
        self.alert_text.insert(tk.END, log_msg)
        self.alert_text.see(tk.END)
        
        # Keep only last 100 lines
        lines = int(self.alert_text.index('end-1c').split('.')[0])
        if lines > 100:
            self.alert_text.delete(1.0, f"{lines-100}.0")
    
    def _update_status(self, message: str):
        """Cập nhật status bar"""
        self.status_label.config(text=message)


# Test standalone
if __name__ == '__main__':
    root = tk.Tk()
    root.title("Monitoring Dashboard Test")
    root.geometry("1000x700")
    
    dashboard = MonitoringDashboard(root)
    dashboard.pack(fill=tk.BOTH, expand=True)
    
    root.mainloop()
