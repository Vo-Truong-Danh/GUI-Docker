"""
Real-time System Health Monitoring Dashboard
Dashboard giám sát sức khỏe hệ thống thời gian thực
Version: 1.0.0
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import psutil
import threading
import time
from datetime import datetime
from typing import Dict, List
import json
from pathlib import Path


class RealTimeMonitoringDashboard:
    """
    Dashboard giám sát hệ thống thời gian thực
    
    Features:
    - CPU, Memory, Disk usage monitoring
    - Process monitoring
    - Error rate tracking
    - Performance metrics visualization
    - Alert system
    - Export reports
    """
    
    def __init__(self, parent=None):
        if parent:
            self.window = tk.Toplevel(parent)
        else:
            self.window = tk.Tk()
        
        self.window.title("🔍 Real-time System Monitoring Dashboard")
        self.window.geometry("1000x700")
        
        # Monitoring state
        self.monitoring = False
        self.monitor_thread = None
        self.metrics_history = []
        self.max_history = 100
        
        # Alert thresholds
        self.thresholds = {
            'cpu_percent': 80,
            'memory_percent': 85,
            'disk_percent': 90
        }
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Thiết lập UI"""
        # Main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(
            main_frame,
            text="🔍 Real-time System Health Monitoring",
            font=("Arial", 16, "bold")
        )
        title.pack(pady=(0, 10))
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_btn = ttk.Button(
            control_frame,
            text="▶️ Start Monitoring",
            command=self.start_monitoring
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(
            control_frame,
            text="⏸️ Stop Monitoring",
            command=self.stop_monitoring,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame,
            text="📊 Export Report",
            command=self.export_report
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame,
            text="🔄 Clear History",
            command=self.clear_history
        ).pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = ttk.Label(
            control_frame,
            text="⚪ Status: Not monitoring",
            font=("Arial", 10, "bold")
        )
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
        # Metrics notebook
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: System Resources
        resources_tab = ttk.Frame(notebook)
        notebook.add(resources_tab, text="💻 System Resources")
        self._setup_resources_tab(resources_tab)
        
        # Tab 2: Processes
        processes_tab = ttk.Frame(notebook)
        notebook.add(processes_tab, text="⚙️ Processes")
        self._setup_processes_tab(processes_tab)
        
        # Tab 3: Alerts & Logs
        alerts_tab = ttk.Frame(notebook)
        notebook.add(alerts_tab, text="🚨 Alerts & Logs")
        self._setup_alerts_tab(alerts_tab)
        
        # Tab 4: Statistics
        stats_tab = ttk.Frame(notebook)
        notebook.add(stats_tab, text="📊 Statistics")
        self._setup_stats_tab(stats_tab)
    
    def _setup_resources_tab(self, parent):
        """Setup resources monitoring tab"""
        frame = ttk.Frame(parent, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # CPU Section
        cpu_frame = ttk.LabelFrame(frame, text="🖥️ CPU", padding="10")
        cpu_frame.pack(fill=tk.X, pady=5)
        
        self.cpu_label = ttk.Label(cpu_frame, text="CPU Usage: ---%", font=("Arial", 12))
        self.cpu_label.pack(anchor=tk.W)
        
        self.cpu_progress = ttk.Progressbar(cpu_frame, length=400, mode='determinate')
        self.cpu_progress.pack(fill=tk.X, pady=5)
        
        self.cpu_cores_label = ttk.Label(cpu_frame, text="Cores: ---")
        self.cpu_cores_label.pack(anchor=tk.W)
        
        # Memory Section
        mem_frame = ttk.LabelFrame(frame, text="🧠 Memory", padding="10")
        mem_frame.pack(fill=tk.X, pady=5)
        
        self.mem_label = ttk.Label(mem_frame, text="Memory Usage: ---%", font=("Arial", 12))
        self.mem_label.pack(anchor=tk.W)
        
        self.mem_progress = ttk.Progressbar(mem_frame, length=400, mode='determinate')
        self.mem_progress.pack(fill=tk.X, pady=5)
        
        self.mem_details_label = ttk.Label(mem_frame, text="Available: --- / Total: ---")
        self.mem_details_label.pack(anchor=tk.W)
        
        # Disk Section
        disk_frame = ttk.LabelFrame(frame, text="💾 Disk", padding="10")
        disk_frame.pack(fill=tk.X, pady=5)
        
        self.disk_label = ttk.Label(disk_frame, text="Disk Usage: ---%", font=("Arial", 12))
        self.disk_label.pack(anchor=tk.W)
        
        self.disk_progress = ttk.Progressbar(disk_frame, length=400, mode='determinate')
        self.disk_progress.pack(fill=tk.X, pady=5)
        
        self.disk_details_label = ttk.Label(disk_frame, text="Free: --- / Total: ---")
        self.disk_details_label.pack(anchor=tk.W)
        
        # Network Section
        net_frame = ttk.LabelFrame(frame, text="🌐 Network", padding="10")
        net_frame.pack(fill=tk.X, pady=5)
        
        self.net_label = ttk.Label(net_frame, text="Sent: --- | Received: ---")
        self.net_label.pack(anchor=tk.W)
    
    def _setup_processes_tab(self, parent):
        """Setup processes monitoring tab"""
        frame = ttk.Frame(parent, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Controls
        controls = ttk.Frame(frame)
        controls.pack(fill=tk.X, pady=5)
        
        ttk.Label(controls, text="🔍 Filter:").pack(side=tk.LEFT, padx=5)
        self.process_filter = ttk.Entry(controls, width=30)
        self.process_filter.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            controls,
            text="Refresh",
            command=self.refresh_processes
        ).pack(side=tk.LEFT, padx=5)
        
        # Process tree
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.process_tree = ttk.Treeview(
            tree_frame,
            columns=("PID", "Name", "CPU%", "Memory%", "Status"),
            show="headings",
            yscrollcommand=scrollbar.set
        )
        
        self.process_tree.heading("PID", text="PID")
        self.process_tree.heading("Name", text="Name")
        self.process_tree.heading("CPU%", text="CPU %")
        self.process_tree.heading("Memory%", text="Memory %")
        self.process_tree.heading("Status", text="Status")
        
        self.process_tree.column("PID", width=80)
        self.process_tree.column("Name", width=200)
        self.process_tree.column("CPU%", width=100)
        self.process_tree.column("Memory%", width=100)
        self.process_tree.column("Status", width=100)
        
        self.process_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.process_tree.yview)
    
    def _setup_alerts_tab(self, parent):
        """Setup alerts tab"""
        frame = ttk.Frame(parent, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Threshold settings
        threshold_frame = ttk.LabelFrame(frame, text="⚙️ Alert Thresholds", padding="10")
        threshold_frame.pack(fill=tk.X, pady=5)
        
        # CPU threshold
        ttk.Label(threshold_frame, text="CPU %:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.cpu_threshold = ttk.Spinbox(threshold_frame, from_=0, to=100, width=10)
        self.cpu_threshold.set(self.thresholds['cpu_percent'])
        self.cpu_threshold.grid(row=0, column=1, padx=5)
        
        # Memory threshold
        ttk.Label(threshold_frame, text="Memory %:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.mem_threshold = ttk.Spinbox(threshold_frame, from_=0, to=100, width=10)
        self.mem_threshold.set(self.thresholds['memory_percent'])
        self.mem_threshold.grid(row=0, column=3, padx=5)
        
        # Disk threshold
        ttk.Label(threshold_frame, text="Disk %:").grid(row=0, column=4, sticky=tk.W, padx=5)
        self.disk_threshold = ttk.Spinbox(threshold_frame, from_=0, to=100, width=10)
        self.disk_threshold.set(self.thresholds['disk_percent'])
        self.disk_threshold.grid(row=0, column=5, padx=5)
        
        ttk.Button(
            threshold_frame,
            text="Apply",
            command=self.update_thresholds
        ).grid(row=0, column=6, padx=10)
        
        # Alerts log
        log_frame = ttk.LabelFrame(frame, text="🚨 Alerts Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.alerts_text = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            font=("Consolas", 9)
        )
        self.alerts_text.pack(fill=tk.BOTH, expand=True)
    
    def _setup_stats_tab(self, parent):
        """Setup statistics tab"""
        frame = ttk.Frame(parent, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Statistics display
        self.stats_text = scrolledtext.ScrolledText(
            frame,
            height=25,
            font=("Consolas", 9)
        )
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Update button
        ttk.Button(
            frame,
            text="🔄 Update Statistics",
            command=self.update_statistics
        ).pack(pady=5)
    
    def start_monitoring(self):
        """Bắt đầu monitoring"""
        if not self.monitoring:
            self.monitoring = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_label.config(text="🟢 Status: Monitoring...")
            
            # Start monitoring thread
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            
            self.log_alert("✅ Monitoring started")
    
    def stop_monitoring(self):
        """Dừng monitoring"""
        if self.monitoring:
            self.monitoring = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.status_label.config(text="⚪ Status: Not monitoring")
            
            self.log_alert("⏸️ Monitoring stopped")
    
    def _monitor_loop(self):
        """Monitoring loop"""
        while self.monitoring:
            try:
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)
                
                # Limit history
                if len(self.metrics_history) > self.max_history:
                    self.metrics_history.pop(0)
                
                # Update UI
                self.window.after(0, self._update_ui, metrics)
                
                # Check alerts
                self._check_alerts(metrics)
                
                time.sleep(2)  # Update every 2 seconds
            
            except Exception as e:
                self.log_alert(f"❌ Monitor error: {e}")
                time.sleep(5)
    
    def _collect_metrics(self) -> Dict:
        """Thu thập metrics"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'percent': psutil.cpu_percent(interval=1),
                'cores': psutil.cpu_count(),
                'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {}
            },
            'memory': {
                'percent': psutil.virtual_memory().percent,
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'used': psutil.virtual_memory().used
            },
            'disk': {
                'percent': psutil.disk_usage('/').percent,
                'total': psutil.disk_usage('/').total,
                'free': psutil.disk_usage('/').free,
                'used': psutil.disk_usage('/').used
            },
            'network': psutil.net_io_counters()._asdict()
        }
        
        return metrics
    
    def _update_ui(self, metrics: Dict):
        """Cập nhật UI với metrics mới"""
        # CPU
        cpu_percent = metrics['cpu']['percent']
        self.cpu_label.config(text=f"CPU Usage: {cpu_percent:.1f}%")
        self.cpu_progress['value'] = cpu_percent
        self.cpu_cores_label.config(text=f"Cores: {metrics['cpu']['cores']}")
        
        # Memory
        mem_percent = metrics['memory']['percent']
        self.mem_label.config(text=f"Memory Usage: {mem_percent:.1f}%")
        self.mem_progress['value'] = mem_percent
        
        mem_avail = metrics['memory']['available'] / (1024**3)  # GB
        mem_total = metrics['memory']['total'] / (1024**3)
        self.mem_details_label.config(
            text=f"Available: {mem_avail:.1f} GB / Total: {mem_total:.1f} GB"
        )
        
        # Disk
        disk_percent = metrics['disk']['percent']
        self.disk_label.config(text=f"Disk Usage: {disk_percent:.1f}%")
        self.disk_progress['value'] = disk_percent
        
        disk_free = metrics['disk']['free'] / (1024**3)
        disk_total = metrics['disk']['total'] / (1024**3)
        self.disk_details_label.config(
            text=f"Free: {disk_free:.1f} GB / Total: {disk_total:.1f} GB"
        )
        
        # Network
        sent_mb = metrics['network']['bytes_sent'] / (1024**2)
        recv_mb = metrics['network']['bytes_recv'] / (1024**2)
        self.net_label.config(
            text=f"Sent: {sent_mb:.1f} MB | Received: {recv_mb:.1f} MB"
        )
    
    def _check_alerts(self, metrics: Dict):
        """Kiểm tra và tạo alerts"""
        # CPU alert
        if metrics['cpu']['percent'] > self.thresholds['cpu_percent']:
            self.log_alert(
                f"⚠️ HIGH CPU: {metrics['cpu']['percent']:.1f}% "
                f"(threshold: {self.thresholds['cpu_percent']}%)"
            )
        
        # Memory alert
        if metrics['memory']['percent'] > self.thresholds['memory_percent']:
            self.log_alert(
                f"⚠️ HIGH MEMORY: {metrics['memory']['percent']:.1f}% "
                f"(threshold: {self.thresholds['memory_percent']}%)"
            )
        
        # Disk alert
        if metrics['disk']['percent'] > self.thresholds['disk_percent']:
            self.log_alert(
                f"⚠️ HIGH DISK: {metrics['disk']['percent']:.1f}% "
                f"(threshold: {self.thresholds['disk_percent']}%)"
            )
    
    def log_alert(self, message: str):
        """Log alert message"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        full_message = f"[{timestamp}] {message}\n"
        
        self.window.after(0, self._append_to_alerts, full_message)
    
    def _append_to_alerts(self, message: str):
        """Append message to alerts text"""
        self.alerts_text.insert(tk.END, message)
        self.alerts_text.see(tk.END)
    
    def refresh_processes(self):
        """Refresh process list"""
        # Clear current items
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)
        
        # Get filter
        filter_text = self.process_filter.get().lower()
        
        # Add processes
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                info = proc.info
                name = info['name']
                
                # Apply filter
                if filter_text and filter_text not in name.lower():
                    continue
                
                self.process_tree.insert('', tk.END, values=(
                    info['pid'],
                    name,
                    f"{info['cpu_percent']:.1f}",
                    f"{info['memory_percent']:.1f}",
                    info['status']
                ))
            except:
                pass
    
    def update_thresholds(self):
        """Update alert thresholds"""
        try:
            self.thresholds['cpu_percent'] = float(self.cpu_threshold.get())
            self.thresholds['memory_percent'] = float(self.mem_threshold.get())
            self.thresholds['disk_percent'] = float(self.disk_threshold.get())
            
            self.log_alert("✅ Alert thresholds updated")
        except ValueError:
            self.log_alert("❌ Invalid threshold values")
    
    def update_statistics(self):
        """Update statistics display"""
        if not self.metrics_history:
            self.stats_text.delete('1.0', tk.END)
            self.stats_text.insert('1.0', "No data available. Start monitoring first.")
            return
        
        # Calculate statistics
        stats = {
            'cpu': [m['cpu']['percent'] for m in self.metrics_history],
            'memory': [m['memory']['percent'] for m in self.metrics_history],
            'disk': [m['disk']['percent'] for m in self.metrics_history]
        }
        
        output = []
        output.append("=" * 80)
        output.append("SYSTEM STATISTICS")
        output.append("=" * 80)
        output.append(f"Sample count: {len(self.metrics_history)}")
        output.append("")
        
        for metric_name, values in stats.items():
            output.append(f"{metric_name.upper()}:")
            output.append(f"  Average: {sum(values)/len(values):.2f}%")
            output.append(f"  Min: {min(values):.2f}%")
            output.append(f"  Max: {max(values):.2f}%")
            output.append("")
        
        output.append("=" * 80)
        
        self.stats_text.delete('1.0', tk.END)
        self.stats_text.insert('1.0', '\n'.join(output))
    
    def clear_history(self):
        """Clear metrics history"""
        self.metrics_history.clear()
        self.log_alert("🗑️ History cleared")
    
    def export_report(self):
        """Export monitoring report"""
        if not self.metrics_history:
            self.log_alert("❌ No data to export")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = Path(__file__).parent / f'monitoring_report_{timestamp}.json'
        
        report = {
            'generated': datetime.now().isoformat(),
            'thresholds': self.thresholds,
            'metrics_count': len(self.metrics_history),
            'metrics': self.metrics_history
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log_alert(f"✅ Report exported: {report_path}")
    
    def run(self):
        """Run dashboard"""
        self.window.mainloop()


def main():
    """Main function"""
    dashboard = RealTimeMonitoringDashboard()
    dashboard.run()


if __name__ == '__main__':
    main()
