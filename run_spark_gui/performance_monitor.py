"""
Performance Monitor Module for Spark Runner GUI
Real-time monitoring of Docker containers: CPU, Memory, Network
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import threading
import time
import re
from datetime import datetime
import json


class PerformanceMonitor:
    """Monitor Docker container performance metrics"""
    
    def __init__(self, parent_frame, config, status_callback, log_callback):
        """
        Initialize Performance Monitor
        
        Args:
            parent_frame: Parent ttk.Frame
            config: Configuration dict
            status_callback: Function to update status bar
            log_callback: Function to append to log
        """
        self.frame = parent_frame
        self.config = config
        self.update_status = status_callback
        self.append_log = log_callback
        
        self.monitoring = False
        self.monitor_thread = None
        self.update_interval = 2000  # 2 seconds
        
        # Container stats cache
        self.stats_cache = {}
        
        self.create_ui()
    
    def create_ui(self):
        """Create Performance Monitor UI"""
        main_container = ttk.Frame(self.frame, padding=10)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Info section
        info_text = (
            "📊 Performance Monitor - Real-time monitoring Docker containers\n"
            "Track CPU, Memory, Network I/O của các containers đang chạy"
        )
        info_lbl = ttk.Label(main_container, text=info_text, foreground='#555',
                            font=('Segoe UI', 9))
        info_lbl.pack(fill=tk.X, pady=(0, 10))
        
        # === Control Section ===
        control_frame = ttk.LabelFrame(main_container, text='⚙️ Monitor Control', padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        control_row = ttk.Frame(control_frame)
        control_row.pack(fill=tk.X)
        
        self.start_btn = ttk.Button(control_row, text='▶️ Start Monitoring',
                                    command=self.start_monitoring,
                                    width=18, style='Success.TButton')
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_btn = ttk.Button(control_row, text='⏹️ Stop Monitoring',
                                   command=self.stop_monitoring,
                                   width=18, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.refresh_btn = ttk.Button(control_row, text='🔄 Refresh Once',
                                      command=self.refresh_stats,
                                      width=15)
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(control_row, text='💾 Export Stats',
                  command=self.export_stats,
                  width=15).pack(side=tk.LEFT, padx=(0, 5))
        
        # Update interval
        interval_frame = ttk.Frame(control_frame)
        interval_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(interval_frame, text='Update Interval:',
                 font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=(0, 10))
        
        self.interval_var = tk.StringVar(value='2')
        interval_combo = ttk.Combobox(interval_frame, textvariable=self.interval_var,
                                     values=['1', '2', '3', '5', '10'],
                                     width=8, state='readonly')
        interval_combo.pack(side=tk.LEFT, padx=(0, 5))
        interval_combo.bind('<<ComboboxSelected>>', self.on_interval_changed)
        
        ttk.Label(interval_frame, text='seconds',
                 font=('Segoe UI', 9)).pack(side=tk.LEFT)
        
        self.status_label = ttk.Label(interval_frame, text='Status: Ready',
                                      font=('Segoe UI', 9, 'bold'),
                                      foreground='#666')
        self.status_label.pack(side=tk.RIGHT, padx=(20, 0))
        
        # === Statistics Display ===
        stats_frame = ttk.LabelFrame(main_container, text='📈 Real-time Statistics', padding=10)
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create notebook for different views
        self.stats_notebook = ttk.Notebook(stats_frame)
        self.stats_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Table View
        table_frame = ttk.Frame(self.stats_notebook)
        self.stats_notebook.add(table_frame, text='📊 Table View')
        self.create_table_view(table_frame)
        
        # Tab 2: Detail View
        detail_frame = ttk.Frame(self.stats_notebook)
        self.stats_notebook.add(detail_frame, text='📋 Detail View')
        self.create_detail_view(detail_frame)
        
        # Tab 3: History Chart (text-based)
        history_frame = ttk.Frame(self.stats_notebook)
        self.stats_notebook.add(history_frame, text='📉 History')
        self.create_history_view(history_frame)
        
        # === Log Section ===
        log_frame = ttk.LabelFrame(main_container, text='📝 Monitor Log', padding=5)
        log_frame.pack(fill=tk.X)
        
        self.monitor_log = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD,
                                                     bg='#fafafa', font=('Courier New', 9))
        self.monitor_log.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags
        self.monitor_log.tag_config('success', foreground='#28a745', font=('Courier New', 9, 'bold'))
        self.monitor_log.tag_config('error', foreground='#dc3545', font=('Courier New', 9, 'bold'))
        self.monitor_log.tag_config('info', foreground='#17a2b8', font=('Courier New', 9, 'bold'))
        self.monitor_log.tag_config('warning', foreground='#ffc107', font=('Courier New', 9, 'bold'))
        
        # Welcome message
        self.log_monitor('📊 Performance Monitor Ready', 'info')
        self.log_monitor('💡 Click "Start Monitoring" to begin', 'info')
    
    def create_table_view(self, parent):
        """Create table view for container stats"""
        columns = ('Container', 'CPU %', 'Memory Usage', 'Memory %', 'Network I/O', 'Block I/O')
        self.stats_tree = ttk.Treeview(parent, columns=columns, show='headings', height=10)
        
        # Define headings
        self.stats_tree.heading('Container', text='Container Name')
        self.stats_tree.heading('CPU %', text='CPU %')
        self.stats_tree.heading('Memory Usage', text='Memory Usage')
        self.stats_tree.heading('Memory %', text='Memory %')
        self.stats_tree.heading('Network I/O', text='Network I/O')
        self.stats_tree.heading('Block I/O', text='Block I/O')
        
        # Define columns width
        self.stats_tree.column('Container', width=200)
        self.stats_tree.column('CPU %', width=100)
        self.stats_tree.column('Memory Usage', width=150)
        self.stats_tree.column('Memory %', width=100)
        self.stats_tree.column('Network I/O', width=150)
        self.stats_tree.column('Block I/O', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.stats_tree.yview)
        self.stats_tree.configure(yscrollcommand=scrollbar.set)
        
        self.stats_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_detail_view(self, parent):
        """Create detailed view for container stats"""
        self.detail_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD,
                                                     bg='#1e1e1e', fg='#d4d4d4',
                                                     font=('Courier New', 9))
        self.detail_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for syntax highlighting
        self.detail_text.tag_config('header', foreground='#4fc3f7', font=('Courier New', 10, 'bold'))
        self.detail_text.tag_config('label', foreground='#81c784')
        self.detail_text.tag_config('value', foreground='#ffffff')
        self.detail_text.tag_config('high', foreground='#ff5252', font=('Courier New', 9, 'bold'))
    
    def create_history_view(self, parent):
        """Create history view for stats timeline"""
        self.history_text = scrolledtext.ScrolledText(parent, wrap=tk.NONE,
                                                      bg='#1e1e1e', fg='#d4d4d4',
                                                      font=('Courier New', 8))
        self.history_text.pack(fill=tk.BOTH, expand=True)
        
        # History data storage (last 50 records)
        self.history_data = []
        self.max_history = 50
    
    def log_monitor(self, message, tag='normal'):
        """Append message to monitor log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.monitor_log.insert(tk.END, f'[{timestamp}] {message}\n', tag)
        self.monitor_log.see(tk.END)
    
    def start_monitoring(self):
        """Start real-time monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.start_btn['state'] = tk.DISABLED
        self.stop_btn['state'] = tk.NORMAL
        self.status_label.config(text='Status: Monitoring...', foreground='#28a745')
        
        self.log_monitor('▶️ Started monitoring', 'success')
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        if not self.monitoring:
            return
        
        self.monitoring = False
        self.start_btn['state'] = tk.NORMAL
        self.stop_btn['state'] = tk.DISABLED
        self.status_label.config(text='Status: Stopped', foreground='#dc3545')
        
        self.log_monitor('⏹️ Stopped monitoring', 'warning')
    
    def _monitor_loop(self):
        """Monitoring loop thread"""
        while self.monitoring:
            try:
                self.refresh_stats()
                time.sleep(self.update_interval / 1000.0)
            except Exception as e:
                self.log_monitor(f'❌ Error: {e}', 'error')
                time.sleep(5)  # Wait longer on error
    
    def refresh_stats(self):
        """Refresh container statistics"""
        try:
            # Get container stats using docker stats
            result = subprocess.run(
                ['docker', 'stats', '--no-stream', '--format',
                 'table {{.Container}}|{{.CPUPerc}}|{{.MemUsage}}|{{.MemPerc}}|{{.NetIO}}|{{.BlockIO}}'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=10
            )
            
            if result.returncode != 0:
                self.log_monitor('❌ Failed to get stats', 'error')
                return
            
            # Parse output
            lines = result.stdout.strip().split('\n')
            if len(lines) < 2:  # No containers running
                self.clear_stats()
                self.log_monitor('⚠️ No containers running', 'warning')
                return
            
            # Clear current stats
            for item in self.stats_tree.get_children():
                self.stats_tree.delete(item)
            
            # Parse and display stats
            container_stats = []
            for line in lines[1:]:  # Skip header
                parts = line.split('|')
                if len(parts) >= 6:
                    container_name = parts[0].strip()
                    cpu_perc = parts[1].strip()
                    mem_usage = parts[2].strip()
                    mem_perc = parts[3].strip()
                    net_io = parts[4].strip()
                    block_io = parts[5].strip()
                    
                    # Add to tree
                    self.stats_tree.insert('', tk.END, values=(
                        container_name, cpu_perc, mem_usage, mem_perc, net_io, block_io
                    ))
                    
                    # Store in cache
                    container_stats.append({
                        'name': container_name,
                        'cpu': cpu_perc,
                        'mem_usage': mem_usage,
                        'mem_perc': mem_perc,
                        'net_io': net_io,
                        'block_io': block_io,
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Update cache
            self.stats_cache[datetime.now().isoformat()] = container_stats
            
            # Update detail view
            self.update_detail_view(container_stats)
            
            # Update history
            self.update_history(container_stats)
            
            self.log_monitor(f'✅ Updated stats ({len(container_stats)} containers)', 'success')
            
        except subprocess.TimeoutExpired:
            self.log_monitor('⏱️ Timeout getting stats', 'warning')
        except FileNotFoundError:
            self.log_monitor('❌ Docker not installed', 'error')
            self.stop_monitoring()
        except Exception as e:
            self.log_monitor(f'❌ Error: {e}', 'error')
    
    def clear_stats(self):
        """Clear all statistics"""
        for item in self.stats_tree.get_children():
            self.stats_tree.delete(item)
        self.detail_text.delete('1.0', tk.END)
    
    def update_detail_view(self, container_stats):
        """Update detailed view with container stats"""
        self.detail_text.delete('1.0', tk.END)
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.detail_text.insert(tk.END, f'╔═══════════════════════════════════════════╗\n', 'header')
        self.detail_text.insert(tk.END, f'  DOCKER CONTAINER PERFORMANCE MONITOR\n', 'header')
        self.detail_text.insert(tk.END, f'  Updated: {timestamp}\n', 'header')
        self.detail_text.insert(tk.END, f'╚═══════════════════════════════════════════╝\n\n', 'header')
        
        for i, stats in enumerate(container_stats, 1):
            self.detail_text.insert(tk.END, f'[{i}] Container: ', 'label')
            self.detail_text.insert(tk.END, f'{stats["name"]}\n', 'value')
            
            self.detail_text.insert(tk.END, '    CPU Usage:      ', 'label')
            cpu_val = stats["cpu"].replace('%', '')
            try:
                if float(cpu_val) > 80:
                    self.detail_text.insert(tk.END, f'{stats["cpu"]} (HIGH!)\n', 'high')
                else:
                    self.detail_text.insert(tk.END, f'{stats["cpu"]}\n', 'value')
            except:
                self.detail_text.insert(tk.END, f'{stats["cpu"]}\n', 'value')
            
            self.detail_text.insert(tk.END, '    Memory Usage:   ', 'label')
            self.detail_text.insert(tk.END, f'{stats["mem_usage"]}\n', 'value')
            
            self.detail_text.insert(tk.END, '    Memory %:       ', 'label')
            mem_val = stats["mem_perc"].replace('%', '')
            try:
                if float(mem_val) > 80:
                    self.detail_text.insert(tk.END, f'{stats["mem_perc"]} (HIGH!)\n', 'high')
                else:
                    self.detail_text.insert(tk.END, f'{stats["mem_perc"]}\n', 'value')
            except:
                self.detail_text.insert(tk.END, f'{stats["mem_perc"]}\n', 'value')
            
            self.detail_text.insert(tk.END, '    Network I/O:    ', 'label')
            self.detail_text.insert(tk.END, f'{stats["net_io"]}\n', 'value')
            
            self.detail_text.insert(tk.END, '    Block I/O:      ', 'label')
            self.detail_text.insert(tk.END, f'{stats["block_io"]}\n', 'value')
            
            self.detail_text.insert(tk.END, '\n')
        
        self.detail_text.see('1.0')
    
    def update_history(self, container_stats):
        """Update history view with stats timeline"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Add to history data
        self.history_data.append({
            'time': timestamp,
            'stats': container_stats
        })
        
        # Keep only last N records
        if len(self.history_data) > self.max_history:
            self.history_data.pop(0)
        
        # Rebuild history display
        self.history_text.delete('1.0', tk.END)
        
        self.history_text.insert(tk.END, '╔═══════════════════════════════════════════════════════════════╗\n')
        self.history_text.insert(tk.END, '  PERFORMANCE HISTORY (Last 50 Records)\n')
        self.history_text.insert(tk.END, '╚═══════════════════════════════════════════════════════════════╝\n\n')
        
        # Display history in reverse (newest first)
        for record in reversed(self.history_data):
            self.history_text.insert(tk.END, f'[{record["time"]}]\n')
            for stats in record['stats']:
                self.history_text.insert(tk.END, 
                    f'  {stats["name"]:<20} | CPU: {stats["cpu"]:<8} | '
                    f'MEM: {stats["mem_perc"]:<8}\n')
            self.history_text.insert(tk.END, '\n')
    
    def on_interval_changed(self, event=None):
        """Handle interval change"""
        try:
            interval = int(self.interval_var.get())
            self.update_interval = interval * 1000
            self.log_monitor(f'⚙️ Interval changed to {interval}s', 'info')
        except ValueError:
            pass
    
    def export_stats(self):
        """Export statistics to file"""
        from tkinter import filedialog
        
        if not self.stats_cache:
            tk.messagebox.showinfo('No Data', 'No statistics data to export.')
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension='.json',
            filetypes=[('JSON files', '*.json'), ('Text files', '*.txt'), ('All files', '*.*')],
            initialfile=f'docker_stats_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(self.stats_cache, f, indent=2, ensure_ascii=False)
                
                self.log_monitor(f'💾 Exported to: {filepath}', 'success')
                tk.messagebox.showinfo('Success', f'Statistics exported to:\n{filepath}')
            except Exception as e:
                self.log_monitor(f'❌ Export failed: {e}', 'error')
                tk.messagebox.showerror('Error', f'Failed to export:\n{e}')
