"""
Performance Monitor Tab - V4 Clean Professional Edition
Clean, minimal UI inspired by GitHub/VS Code
"""

import tkinter as tk
from tkinter import ttk
import subprocess

# Import subprocess utilities for hidden console windows
try:
    from subprocess_utils import run_hidden, popen_hidden
except ImportError:
    def run_hidden(*args, **kwargs):
        return run_hidden(*args, **kwargs)
    def popen_hidden(*args, **kwargs):
        return popen_hidden(*args, **kwargs)
import threading
import time
from datetime import datetime
import json


# ============================================================================
# V4 CLEAN COMPONENTS (Shared)
# ============================================================================

class CleanButton:
    """Clean button with GitHub-style design"""
    
    STYLES = {
        'primary': {'bg': '#0969DA', 'fg': 'white', 'hover_bg': '#0860CA'},
        'success': {'bg': '#1A7F37', 'fg': 'white', 'hover_bg': '#1A7F37'},
        'danger': {'bg': '#CF222E', 'fg': 'white', 'hover_bg': '#C11F2A'},
        'secondary': {'bg': '#6E7781', 'fg': 'white', 'hover_bg': '#57606A'},
    }
    
    def __init__(self, parent, text, command=None, style='primary'):
        self.command = command
        self.style_config = self.STYLES.get(style, self.STYLES['primary'])
        self.default_bg = self.style_config['bg']
        self.hover_bg = self.style_config['hover_bg']
        
        self.label = tk.Label(
            parent, text=text,
            bg=self.default_bg, fg=self.style_config['fg'],
            font=('Segoe UI', 9, 'normal'),
            cursor='hand2', padx=12, pady=7, relief=tk.FLAT
        )
        
        self.label.bind('<Button-1>', self._on_click)
        self.label.bind('<Enter>', self._on_enter)
        self.label.bind('<Leave>', self._on_leave)
    
    def _on_click(self, event):
        if self.command:
            self.command()
    
    def _on_enter(self, event):
        self.label.config(bg=self.hover_bg)
    
    def _on_leave(self, event):
        self.label.config(bg=self.default_bg)
    
    def pack(self, **kwargs):
        return self.label.pack(**kwargs)
    
    def config(self, **kwargs):
        if 'state' in kwargs:
            state = kwargs['state']
            if state == 'disabled':
                self.label.config(cursor='arrow', bg='#E5E7EB', fg='#9CA3AF')
                self.label.unbind('<Button-1>')
            else:
                self.label.config(cursor='hand2', bg=self.default_bg,
                                fg=self.style_config['fg'])
                self.label.bind('<Button-1>', self._on_click)


class SectionCard(tk.Frame):
    """Clean section card with subtle border"""
    
    def __init__(self, parent, title="", **kwargs):
        super().__init__(parent, bg='#FFFFFF', relief=tk.FLAT,
                        borderwidth=1, highlightthickness=1,
                        highlightbackground='#D0D7DE', **kwargs)
        
        if title:
            title_frame = tk.Frame(self, bg='#F6F8FA', height=32)
            title_frame.pack(fill=tk.X, side=tk.TOP)
            title_frame.pack_propagate(False)
            
            title_label = tk.Label(
                title_frame, text=title,
                bg='#F6F8FA', fg='#24292F',
                font=('Segoe UI', 10, 'bold'),
                anchor='w', padx=16
            )
            title_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.content = tk.Frame(self, bg='#FFFFFF', padx=16, pady=12)
        self.content.pack(fill=tk.BOTH, expand=True)
    
    def get_content(self):
        return self.content


class MetricCard(tk.Frame):
    """Metric display card with value and label"""
    
    def __init__(self, parent, label, icon="", **kwargs):
        super().__init__(parent, bg='#FFFFFF', relief=tk.SOLID,
                        borderwidth=1, **kwargs)
        
        # Icon + Label
        header_frame = tk.Frame(self, bg='#FFFFFF')
        header_frame.pack(fill=tk.X, padx=12, pady=(8, 4))
        
        tk.Label(
            header_frame,
            text=f"{icon} {label}",
            bg='#FFFFFF', fg='#6E7781',
            font=('Segoe UI', 8), anchor='w'
        ).pack(side=tk.LEFT)
        
        # Value
        self.value_label = tk.Label(
            self,
            text="--",
            bg='#FFFFFF', fg='#24292F',
            font=('Segoe UI', 16, 'bold')
        )
        self.value_label.pack(padx=12, pady=(0, 8))
    
    def set_value(self, value):
        """Update metric value"""
        self.value_label.config(text=str(value))


# ============================================================================
# PERFORMANCE MONITOR TAB
# ============================================================================

class PerformanceMonitorV4Clean:
    """Performance Monitor with Clean Professional UI"""
    
    def __init__(self, parent_frame, config, status_callback, log_callback):
        self.frame = parent_frame
        self.config = config
        self.update_status = status_callback
        self.append_log = log_callback
        
        self.monitoring = False
        self.monitor_thread = None
        self.update_interval = 2  # seconds
        self.stats_cache = {}
        
        self.create_ui()
    
    def create_ui(self):
        """Create V4 Clean Professional UI"""
        # Note: parent_frame is ttk.Frame, can't set bg directly
        
        # Main container with scrollbar
        canvas = tk.Canvas(self.frame, bg='#F6F8FA', highlightthickness=0)
        scrollbar = tk.Scrollbar(self.frame, orient='vertical', command=canvas.yview)
        
        scroll_frame = tk.Frame(canvas, bg='#F6F8FA')
        scroll_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind('<Enter>', lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind('<Leave>', lambda e: canvas.unbind_all("<MouseWheel>"))
        
        # Single column layout
        scroll_frame.grid_columnconfigure(0, weight=1)
        
        main_col = tk.Frame(scroll_frame, bg='#F6F8FA')
        main_col.grid(row=0, column=0, sticky='nsew')
        
        # Header
        header = tk.Label(
            main_col, text="📊 Performance Monitor",
            bg='#F6F8FA', fg='#24292F',
            font=('Segoe UI', 16, 'bold'), anchor='w'
        )
        header.pack(fill=tk.X, pady=(0, 4))
        
        subtitle = tk.Label(
            main_col, text="Real-time Docker container monitoring",
            bg='#F6F8FA', fg='#6E7781',
            font=('Segoe UI', 9), anchor='w'
        )
        subtitle.pack(fill=tk.X, pady=(0, 20))
        
        # === Controls Card ===
        controls_card = SectionCard(main_col, title="🎛️ Controls")
        controls_card.pack(fill=tk.X, pady=(0, 12))
        
        controls_content = controls_card.get_content()
        
        # Interval selection
        interval_frame = tk.Frame(controls_content, bg='#FFFFFF')
        interval_frame.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(
            interval_frame, text="Update Interval:",
            bg='#FFFFFF', fg='#24292F',
            font=('Segoe UI', 9, 'bold')
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        self.interval_var = tk.IntVar(value=2)
        for sec in [1, 2, 5, 10]:
            tk.Radiobutton(
                interval_frame,
                text=f"{sec}s",
                variable=self.interval_var,
                value=sec,
                bg='#FFFFFF', fg='#24292F',
                font=('Segoe UI', 9),
                activebackground='#FFFFFF',
                selectcolor='#FFFFFF',
                command=self.on_interval_change
            ).pack(side=tk.LEFT, padx=4)
        
        # Buttons
        btn_frame = tk.Frame(controls_content, bg='#FFFFFF')
        btn_frame.pack(fill=tk.X)
        
        self.start_btn = CleanButton(btn_frame, "▶ Start Monitoring", 
                                     self.start_monitoring, 'success')
        self.start_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        
        self.stop_btn = CleanButton(btn_frame, "⏹ Stop Monitoring",
                                    self.stop_monitoring, 'danger')
        self.stop_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 6))
        self.stop_btn.config(state='disabled')
        
        CleanButton(btn_frame, "💾 Export Stats", self.export_stats, 'secondary').pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0))
        
        # === Metrics Grid ===
        metrics_card = SectionCard(main_col, title="📈 Current Metrics")
        metrics_card.pack(fill=tk.X, pady=(0, 12))
        
        metrics_content = metrics_card.get_content()
        
        # Create 2x3 grid of metric cards
        metrics_grid = tk.Frame(metrics_content, bg='#FFFFFF')
        metrics_grid.pack(fill=tk.X)
        
        for i in range(3):
            metrics_grid.grid_columnconfigure(i, weight=1)
        
        self.cpu_metric = MetricCard(metrics_grid, "CPU Usage", "💻")
        self.cpu_metric.grid(row=0, column=0, sticky='nsew', padx=(0, 6), pady=(0, 6))
        
        self.mem_metric = MetricCard(metrics_grid, "Memory", "🧠")
        self.mem_metric.grid(row=0, column=1, sticky='nsew', padx=(6, 6), pady=(0, 6))
        
        self.net_metric = MetricCard(metrics_grid, "Network I/O", "🌐")
        self.net_metric.grid(row=0, column=2, sticky='nsew', padx=(6, 0), pady=(0, 6))
        
        self.block_metric = MetricCard(metrics_grid, "Block I/O", "💾")
        self.block_metric.grid(row=1, column=0, sticky='nsew', padx=(0, 6))
        
        self.pids_metric = MetricCard(metrics_grid, "PIDs", "🔢")
        self.pids_metric.grid(row=1, column=1, sticky='nsew', padx=(6, 6))
        
        self.containers_metric = MetricCard(metrics_grid, "Containers", "📦")
        self.containers_metric.grid(row=1, column=2, sticky='nsew', padx=(6, 0))
        
        # === Container Details Card ===
        details_card = SectionCard(main_col, title="📋 Container Details")
        details_card.pack(fill=tk.BOTH, expand=True, pady=(0, 12))
        
        details_content = details_card.get_content()
        
        # Container list with scrollbar
        list_frame = tk.Frame(details_content, bg='#FFFFFF')
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.container_text = tk.Text(
            list_frame,
            height=10,
            wrap=tk.NONE,
            bg='#24292F', fg='#E6EDF3',
            font=('Consolas', 9),
            relief=tk.FLAT, borderwidth=0,
            padx=12, pady=12
        )
        
        text_scroll_y = tk.Scrollbar(list_frame, orient='vertical',
                                     command=self.container_text.yview)
        text_scroll_x = tk.Scrollbar(list_frame, orient='horizontal',
                                     command=self.container_text.xview)
        
        self.container_text.configure(yscrollcommand=text_scroll_y.set,
                                     xscrollcommand=text_scroll_x.set)
        
        self.container_text.grid(row=0, column=0, sticky='nsew')
        text_scroll_y.grid(row=0, column=1, sticky='ns')
        text_scroll_x.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Color tags
        self.container_text.tag_config('header', foreground='#79C0FF', font=('Consolas', 9, 'bold'))
        self.container_text.tag_config('good', foreground='#7EE787')
        self.container_text.tag_config('warning', foreground='#FFA657')
        self.container_text.tag_config('error', foreground='#FF7B72')
        
        self.log_to_container("📊 Performance Monitor ready. Click 'Start Monitoring' to begin.\n", 'header')
    
    def log_to_container(self, message, tag='good'):
        """Add message to container text"""
        self.container_text.insert(tk.END, message, tag)
        self.container_text.see(tk.END)
    
    def on_interval_change(self):
        """Handle interval change"""
        self.update_interval = self.interval_var.get()
        if self.append_log:
            self.append_log(f"Update interval: {self.update_interval}s\n")
    
    def start_monitoring(self):
        """Start monitoring containers"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        
        self.log_to_container(f"\n▶ Monitoring started (interval: {self.update_interval}s)\n", 'header')
        
        if self.append_log:
            self.append_log("▶ Performance monitoring started\n")
        
        # Start monitor thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        
        self.log_to_container("\n⏹ Monitoring stopped\n", 'warning')
        
        if self.append_log:
            self.append_log("⏹ Performance monitoring stopped\n")
    
    def _monitor_loop(self):
        """Monitor loop (runs in thread)"""
        while self.monitoring:
            try:
                self._update_stats()
                time.sleep(self.update_interval)
            except Exception as e:
                self.log_to_container(f"\n✗ Error: {str(e)}\n", 'error')
                time.sleep(self.update_interval)
    
    def _update_stats(self):
        """Update statistics"""
        try:
            # Get docker stats
            result = run_hidden(
                ['docker', 'stats', '--no-stream', '--format', 
                 '{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}\t{{.PIDs}}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return
            
            lines = result.stdout.strip().split('\n')
            if not lines:
                return
            
            # Parse stats
            total_cpu = 0
            total_mem = 0
            total_pids = 0
            container_count = 0
            
            details = []
            
            for line in lines:
                if not line.strip():
                    continue
                
                parts = line.split('\t')
                if len(parts) < 6:
                    continue
                
                name = parts[0]
                cpu = parts[1].replace('%', '')
                mem = parts[2]
                net = parts[3]
                block = parts[4]
                pids = parts[5]
                
                try:
                    cpu_val = float(cpu)
                    total_cpu += cpu_val
                    
                    pids_val = int(pids) if pids.isdigit() else 0
                    total_pids += pids_val
                    
                    container_count += 1
                    
                    # Determine status color
                    status = 'good' if cpu_val < 50 else 'warning' if cpu_val < 80 else 'error'
                    
                    details.append({
                        'name': name,
                        'cpu': cpu,
                        'mem': mem,
                        'net': net,
                        'block': block,
                        'pids': pids,
                        'status': status
                    })
                    
                except ValueError:
                    pass
            
            # Update metrics (on main thread)
            self.frame.after(0, self._update_metrics_ui, {
                'cpu': f"{total_cpu:.1f}%",
                'mem': f"{container_count} containers",
                'net': "Active",
                'block': "Active",
                'pids': str(total_pids),
                'containers': str(container_count),
                'details': details
            })
            
        except subprocess.TimeoutExpired:
            self.log_to_container("⚠ Docker stats timeout\n", 'warning')
        except Exception as e:
            self.log_to_container(f"✗ Error updating stats: {str(e)}\n", 'error')
    
    def _update_metrics_ui(self, stats):
        """Update UI with stats (called on main thread)"""
        self.cpu_metric.set_value(stats['cpu'])
        self.mem_metric.set_value(stats['mem'])
        self.net_metric.set_value(stats['net'])
        self.block_metric.set_value(stats['block'])
        self.pids_metric.set_value(stats['pids'])
        self.containers_metric.set_value(stats['containers'])
        
        # Update container details
        self.container_text.delete('1.0', tk.END)
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_to_container(f"=== Updated at {timestamp} ===\n\n", 'header')
        
        for container in stats['details']:
            self.log_to_container(f"📦 {container['name']}\n", 'header')
            self.log_to_container(f"   CPU: {container['cpu']}%  ", container['status'])
            self.log_to_container(f"MEM: {container['mem']}  ", 'good')
            self.log_to_container(f"PIDs: {container['pids']}\n", 'good')
            self.log_to_container(f"   NET: {container['net']}  ", 'good')
            self.log_to_container(f"BLOCK: {container['block']}\n\n", 'good')
        
        # Cache stats
        self.stats_cache[datetime.now().isoformat()] = stats
    
    def export_stats(self):
        """Export statistics to JSON"""
        if not self.stats_cache:
            tk.messagebox.showwarning("No Data", "No statistics to export. Start monitoring first.")
            return
        
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension='.json',
            filetypes=[('JSON files', '*.json'), ('All files', '*.*')],
            initialfile=f'docker_stats_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.stats_cache, f, indent=2)
                
                self.log_to_container(f"\n✓ Stats exported to {filename}\n", 'good')
                
                if self.append_log:
                    self.append_log(f"✓ Stats exported to {filename}\n")
                
                tk.messagebox.showinfo("Success", f"Statistics exported to:\n{filename}")
            except Exception as e:
                tk.messagebox.showerror("Error", f"Failed to export: {str(e)}")
