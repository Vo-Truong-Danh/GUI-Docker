"""
Real-time Health Monitoring Dashboard
Provides comprehensive system health monitoring with GUI
Version: 1.0.0
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
from datetime import datetime
from typing import Dict, Optional

try:
    from system_optimizer import get_system_optimizer
    OPTIMIZER_AVAILABLE = True
except:
    OPTIMIZER_AVAILABLE = False

try:
    from logging_config import get_logger
    logger = get_logger('health_dashboard')
except:
    logger = None


class HealthMonitoringDashboard:
    """Real-time health monitoring dashboard"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.window = None
        self.monitoring = False
        self.monitor_thread = None
        self.update_interval = 5  # seconds
        
        if OPTIMIZER_AVAILABLE:
            self.optimizer = get_system_optimizer(logger)
        else:
            self.optimizer = None
        
        # Widgets
        self.widgets = {}
        
    def create_dashboard(self):
        """Create dashboard window"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("System Health Monitoring Dashboard")
        self.window.geometry("900x700")
        
        # Main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="🏥 System Health Monitoring Dashboard",
            font=('Segoe UI', 16, 'bold')
        )
        title_label.grid(row=0, column=0, pady=(0, 15), sticky=tk.W)
        
        # Status indicators frame
        status_frame = ttk.LabelFrame(main_frame, text="System Status", padding="10")
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        # CPU
        ttk.Label(status_frame, text="CPU Usage:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.widgets['cpu_label'] = ttk.Label(status_frame, text="-- %", font=('Segoe UI', 10))
        self.widgets['cpu_label'].grid(row=0, column=1, sticky=tk.W, padx=10)
        
        self.widgets['cpu_progress'] = ttk.Progressbar(status_frame, mode='determinate', length=300)
        self.widgets['cpu_progress'].grid(row=0, column=2, sticky=tk.E, padx=10)
        
        # Memory
        ttk.Label(status_frame, text="Memory Usage:", font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.widgets['mem_label'] = ttk.Label(status_frame, text="-- %", font=('Segoe UI', 10))
        self.widgets['mem_label'].grid(row=1, column=1, sticky=tk.W, padx=10)
        
        self.widgets['mem_progress'] = ttk.Progressbar(status_frame, mode='determinate', length=300)
        self.widgets['mem_progress'].grid(row=1, column=2, sticky=tk.E, padx=10)
        
        # Disk
        ttk.Label(status_frame, text="Disk Usage:", font=('Segoe UI', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.widgets['disk_label'] = ttk.Label(status_frame, text="-- %", font=('Segoe UI', 10))
        self.widgets['disk_label'].grid(row=2, column=1, sticky=tk.W, padx=10)
        
        self.widgets['disk_progress'] = ttk.Progressbar(status_frame, mode='determinate', length=300)
        self.widgets['disk_progress'].grid(row=2, column=2, sticky=tk.E, padx=10)
        
        # Process info
        ttk.Label(status_frame, text="Process Memory:", font=('Segoe UI', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.widgets['proc_mem_label'] = ttk.Label(status_frame, text="-- MB", font=('Segoe UI', 10))
        self.widgets['proc_mem_label'].grid(row=3, column=1, sticky=tk.W, padx=10)
        
        ttk.Label(status_frame, text="Threads:", font=('Segoe UI', 10, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=5)
        self.widgets['threads_label'] = ttk.Label(status_frame, text="--", font=('Segoe UI', 10))
        self.widgets['threads_label'].grid(row=4, column=1, sticky=tk.W, padx=10)
        
        # Health status
        ttk.Label(status_frame, text="Overall Health:", font=('Segoe UI', 10, 'bold')).grid(row=5, column=0, sticky=tk.W, pady=5)
        self.widgets['health_label'] = ttk.Label(status_frame, text="🟢 Healthy", font=('Segoe UI', 12, 'bold'), foreground='green')
        self.widgets['health_label'].grid(row=5, column=1, sticky=tk.W, padx=10)
        
        # Alerts frame
        alerts_frame = ttk.LabelFrame(main_frame, text="Alerts & Recommendations", padding="10")
        alerts_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        alerts_frame.columnconfigure(0, weight=1)
        alerts_frame.rowconfigure(0, weight=1)
        
        self.widgets['alerts_text'] = scrolledtext.ScrolledText(
            alerts_frame, 
            height=8, 
            font=('Consolas', 9),
            wrap=tk.WORD
        )
        self.widgets['alerts_text'].grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.widgets['log_text'] = scrolledtext.ScrolledText(
            log_frame, 
            height=10, 
            font=('Consolas', 8),
            wrap=tk.WORD
        )
        self.widgets['log_text'].grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=4, column=0, pady=(10, 0))
        
        self.widgets['start_btn'] = ttk.Button(
            control_frame, 
            text="▶ Start Monitoring",
            command=self.start_monitoring
        )
        self.widgets['start_btn'].grid(row=0, column=0, padx=5)
        
        self.widgets['stop_btn'] = ttk.Button(
            control_frame, 
            text="⏸ Stop Monitoring",
            command=self.stop_monitoring,
            state=tk.DISABLED
        )
        self.widgets['stop_btn'].grid(row=0, column=1, padx=5)
        
        ttk.Button(
            control_frame, 
            text="🔄 Optimize Now",
            command=self.optimize_now
        ).grid(row=0, column=2, padx=5)
        
        ttk.Button(
            control_frame, 
            text="📊 Full Report",
            command=self.show_full_report
        ).grid(row=0, column=3, padx=5)
        
        ttk.Button(
            control_frame, 
            text="❌ Close",
            command=self.window.destroy
        ).grid(row=0, column=4, padx=5)
        
        # Start with initial update
        self.update_metrics()
        
        # Log startup
        self.log_message("Dashboard initialized")
    
    def update_metrics(self):
        """Update all metrics"""
        if not self.optimizer or not OPTIMIZER_AVAILABLE:
            self.log_message("⚠️ System optimizer not available")
            return
        
        try:
            metrics = self.optimizer.get_system_metrics()
            
            if not metrics:
                return
            
            # Update CPU
            cpu_percent = metrics.get('cpu', {}).get('percent', 0)
            self.widgets['cpu_label'].config(text=f"{cpu_percent:.1f}%")
            self.widgets['cpu_progress']['value'] = cpu_percent
            
            # Update Memory
            mem_percent = metrics.get('memory', {}).get('percent', 0)
            self.widgets['mem_label'].config(text=f"{mem_percent:.1f}%")
            self.widgets['mem_progress']['value'] = mem_percent
            
            # Update Disk
            disk_percent = metrics.get('disk', {}).get('percent', 0)
            self.widgets['disk_label'].config(text=f"{disk_percent:.1f}%")
            self.widgets['disk_progress']['value'] = disk_percent
            
            # Update Process Info
            proc_mem = metrics.get('process', {}).get('memory_rss', 0) / (1024 * 1024)
            self.widgets['proc_mem_label'].config(text=f"{proc_mem:.1f} MB")
            
            threads = metrics.get('process', {}).get('num_threads', 0)
            self.widgets['threads_label'].config(text=str(threads))
            
            # Update health status
            self.update_health_status(metrics)
            
            # Update alerts
            self.update_alerts(metrics)
            
        except Exception as e:
            self.log_message(f"❌ Error updating metrics: {e}")
    
    def update_health_status(self, metrics: Dict):
        """Update overall health status"""
        cpu = metrics.get('cpu', {}).get('percent', 0)
        mem = metrics.get('memory', {}).get('percent', 0)
        disk = metrics.get('disk', {}).get('percent', 0)
        
        # Determine health
        if cpu > 90 or mem > 90 or disk > 90:
            status = "🔴 Critical"
            color = "red"
        elif cpu > 70 or mem > 70 or disk > 85:
            status = "🟡 Warning"
            color = "orange"
        else:
            status = "🟢 Healthy"
            color = "green"
        
        self.widgets['health_label'].config(text=status, foreground=color)
    
    def update_alerts(self, metrics: Dict):
        """Update alerts and recommendations"""
        alerts = []
        
        cpu = metrics.get('cpu', {}).get('percent', 0)
        mem = metrics.get('memory', {}).get('percent', 0)
        disk = metrics.get('disk', {}).get('percent', 0)
        
        if cpu > 80:
            alerts.append(f"⚠️ HIGH CPU USAGE: {cpu:.1f}% - Check for intensive processes")
        
        if mem > 80:
            alerts.append(f"⚠️ HIGH MEMORY USAGE: {mem:.1f}% - Consider optimization or restart")
        
        if disk > 85:
            alerts.append(f"⚠️ HIGH DISK USAGE: {disk:.1f}% - Clean up old files")
        
        if not alerts:
            alerts.append("✅ All systems operating normally")
        
        # Update alerts text
        alerts_text = self.widgets['alerts_text']
        alerts_text.delete(1.0, tk.END)
        alerts_text.insert(tk.END, "\n".join(alerts))
    
    def log_message(self, message: str):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_text = self.widgets.get('log_text')
        
        if log_text:
            log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            log_text.see(tk.END)
            
            # Limit log size
            lines = int(log_text.index('end-1c').split('.')[0])
            if lines > 200:
                log_text.delete(1.0, "50.0")
    
    def start_monitoring(self):
        """Start continuous monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.widgets['start_btn'].config(state=tk.DISABLED)
        self.widgets['stop_btn'].config(state=tk.NORMAL)
        
        self.log_message("▶️ Monitoring started")
        
        def monitor_loop():
            while self.monitoring:
                try:
                    self.window.after(0, self.update_metrics)
                    time.sleep(self.update_interval)
                except:
                    break
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        self.widgets['start_btn'].config(state=tk.NORMAL)
        self.widgets['stop_btn'].config(state=tk.DISABLED)
        
        self.log_message("⏸️ Monitoring stopped")
    
    def optimize_now(self):
        """Run optimization"""
        if not self.optimizer:
            self.log_message("⚠️ Optimizer not available")
            return
        
        self.log_message("🔄 Running optimization...")
        
        try:
            result = self.optimizer.auto_optimize()
            
            mem_result = result.get('memory', {})
            if mem_result.get('success'):
                self.log_message(f"✅ Memory: Collected {mem_result.get('objects_collected', 0)} objects")
            
            temp_result = result.get('temp_files', {})
            if temp_result.get('success'):
                self.log_message(f"✅ Cleanup: Freed {temp_result.get('space_freed_mb', 0):.2f} MB")
            
            self.log_message("✅ Optimization completed")
            
            # Update metrics
            self.update_metrics()
        
        except Exception as e:
            self.log_message(f"❌ Optimization failed: {e}")
    
    def show_full_report(self):
        """Show full optimization report"""
        if not self.optimizer:
            self.log_message("⚠️ Optimizer not available")
            return
        
        self.log_message("📊 Generating full report...")
        
        try:
            report = self.optimizer.get_optimization_report()
            
            # Create report window
            report_window = tk.Toplevel(self.window)
            report_window.title("Full System Report")
            report_window.geometry("700x600")
            
            text_widget = scrolledtext.ScrolledText(
                report_window, 
                font=('Consolas', 9),
                wrap=tk.WORD
            )
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Format report
            import json
            report_text = json.dumps(report, indent=2, default=str)
            text_widget.insert(tk.END, report_text)
            
            self.log_message("✅ Report generated")
        
        except Exception as e:
            self.log_message(f"❌ Report generation failed: {e}")
    
    def run(self):
        """Run dashboard as standalone"""
        self.create_dashboard()
        if self.window:
            self.window.mainloop()


def main():
    """Main function"""
    dashboard = HealthMonitoringDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
