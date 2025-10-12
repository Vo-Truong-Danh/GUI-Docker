"""
Spark Runner Tab for the main GUI.
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, Menu, filedialog, messagebox
from ui_utils import create_tooltip
from pathlib import Path
import sys
import os
import subprocess
import shutil
from datetime import datetime
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
import time


def retry_on_error(max_retries=3, delay=1, backoff=2):
    """
    Decorator to retry a function on failure with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay after each retry
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        # Log retry attempt (if self is available for logging)
                        if args and hasattr(args[0], 'append_log'):
                            args[0].append_log(
                                f"⚠️ Retry {attempt + 1}/{max_retries} after error: {str(e)}", 
                                'warning'
                            )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        # Last attempt failed
                        if args and hasattr(args[0], 'append_log'):
                            args[0].append_log(
                                f"❌ Failed after {max_retries} retries: {str(e)}", 
                                'error'
                            )
                        raise last_exception
            
            # Should never reach here, but just in case
            raise last_exception
        
        return wrapper
    return decorator


def generate_commands(filepath: str, container: str, master: str) -> str:
    """Generate docker commands for the given file"""
    if not filepath:
        return ""
    
    path = Path(filepath)
    filename = path.name
    
    if not filename.endswith('.py'):
        filename += '.py'
    
    base = filename[:-3]

    original = (
        f"// Các lệnh thủ công:\n"
        f"// 1. Copy file\n"
        f"docker cp {filepath} {container}:/tmp\n"
        f"// 2. Mở bash (tương tác)\n"
        f"docker exec -it {container} bash\n"
        f"// 3. Chạy Spark (trong bash)\n"
        f"/spark/bin/spark-submit --master {master} /tmp/{filename}\n"
    )

    non_interactive = (
        f"\n// Lệnh tự động (non-interactive):\n"
        f"docker cp {filepath} {container}:/tmp\n"
        f"docker exec {container} /spark/bin/spark-submit --master {master} /tmp/{filename}\n"
    )

    return original + non_interactive


class SparkRunnerTab:
    def __init__(self, parent_frame, config, theme, callbacks):
        self.frame = parent_frame
        self.config = config
        self.theme = theme
        self.callbacks = callbacks
        
        # These will be set from main.py
        self.log_text = None
        self.root = None
        
        # Thread-safe logging queue
        self.log_queue = queue.Queue()
        
        # Thread pool for background operations
        self.thread_pool = ThreadPoolExecutor(max_workers=3, thread_name_prefix='spark_')
        self._active_futures = []
        
        self.create_ui()

    def create_ui(self):
        """Create modern split-view UI with scrollable left panel"""
        
        # === Main Split Container ===
        main_container = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # === LEFT PANEL with Canvas (Fixed width, Scrollable) ===
        left_outer = ttk.Frame(main_container, width=450)
        
        # Create canvas for scrolling
        canvas = tk.Canvas(left_outer, width=450, highlightthickness=0, 
                          bg=self.theme.get('bg_light', '#ffffff'))
        scrollbar = ttk.Scrollbar(left_outer, orient="vertical", command=canvas.yview)
        
        left_panel = ttk.Frame(canvas, style='Left.TFrame')
        
        # Configure scroll region
        def configure_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        left_panel.bind("<Configure>", configure_scroll)
        canvas_frame = canvas.create_window((0, 0), window=left_panel, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # === RIGHT PANEL (Expandable Log) ===
        right_panel = ttk.Frame(main_container, style='Right.TFrame')
        
        # Add panels to PanedWindow
        main_container.add(left_outer, weight=0)
        main_container.add(right_panel, weight=1)
        
        # ========== LEFT PANEL CONTENT ==========
        
        # === File Selection Frame (Compact) ===
        file_frame = ttk.LabelFrame(left_panel, text='📁 File Python', padding=6)
        file_frame.pack(fill=tk.X, pady=(0, 4))
        
        file_input_frame = ttk.Frame(file_frame)
        file_input_frame.pack(fill=tk.X, pady=(0, 3))
        
        self.file_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_input_frame, textvariable=self.file_var, 
                                     font=('Consolas', 9))
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        self.file_entry.bind('<Button-3>', lambda e: self.show_file_context_menu(e))
        
        browse_btn = ttk.Button(file_input_frame, text='Browse...', command=self.on_browse, width=10)
        browse_btn.pack(side=tk.LEFT, padx=(0, 2))
        create_tooltip(browse_btn, "Browse file (Ctrl+O)")
        
        clear_btn = ttk.Button(file_input_frame, text='Clear', command=self.clear_file, width=8)
        clear_btn.pack(side=tk.LEFT)
        create_tooltip(clear_btn, "Clear")
        
        # History dropdown (compact)
        history_frame = ttk.Frame(file_frame)
        history_frame.pack(fill=tk.X)
        
        ttk.Label(history_frame, text='History:', font=('Segoe UI', 8), width=8).pack(side=tk.LEFT, padx=(0, 2))
        
        self.history_combo = ttk.Combobox(history_frame, values=self.config.get('history', []), 
                                          state='readonly', font=('Consolas', 8))
        self.history_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        self.history_combo.bind('<<ComboboxSelected>>', self.on_history_selected)
        
        if self.config.get('history'):
            self.history_combo.current(0)
        
        clear_history_btn = ttk.Button(history_frame, text='Clear', 
                                       command=self.clear_history, width=8)
        clear_history_btn.pack(side=tk.LEFT)
        create_tooltip(clear_history_btn, "Clear history")
        
        # === Configuration Frame (Compact) ===
        config_frame = ttk.LabelFrame(left_panel, text='⚙️ Cấu Hình', padding=6)
        config_frame.pack(fill=tk.X, pady=(0, 4))
        
        # Row 1: Container
        row1 = ttk.Frame(config_frame)
        row1.pack(fill=tk.X, pady=(0, 2))
        
        ttk.Label(row1, text='Container:', font=('Segoe UI', 8), width=9).pack(side=tk.LEFT)
        self.container_var = tk.StringVar(value=self.config['container'])
        container_entry = ttk.Entry(row1, textvariable=self.container_var, 
                                    font=('Consolas', 8))
        container_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Row 2: Master
        row2 = ttk.Frame(config_frame)
        row2.pack(fill=tk.X, pady=(0, 3))
        
        ttk.Label(row2, text='Master:', font=('Segoe UI', 8), width=9).pack(side=tk.LEFT)
        self.master_var = tk.StringVar(value=self.config['master'])
        master_entry = ttk.Entry(row2, textvariable=self.master_var, 
                                font=('Consolas', 8))
        master_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Buttons
        btn_row = ttk.Frame(config_frame)
        btn_row.pack(fill=tk.X)
        
        save_config_btn = ttk.Button(btn_row, text='Save', command=self.on_save_config, width=10)
        save_config_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        reset_config_btn = ttk.Button(btn_row, text='Reset', command=self.reset_config, width=10)
        reset_config_btn.pack(side=tk.LEFT)
        
        # === Docker Control Frame (Optimized) ===
        docker_frame = ttk.LabelFrame(left_panel, text='🐳 Docker Control', padding=6)
        docker_frame.pack(fill=tk.X, pady=(0, 4))
        
        # Container Controls
        docker_row1 = ttk.Frame(docker_frame)
        docker_row1.pack(fill=tk.X, pady=(0, 2))
        
        self.docker_start_btn = ttk.Button(docker_row1, text='Start', 
                                           command=self.docker_start,
                                           style='Success.TButton', width=10)
        self.docker_start_btn.pack(side=tk.LEFT, padx=(0, 2))
        create_tooltip(self.docker_start_btn, "Start containers")
        
        self.docker_stop_btn = ttk.Button(docker_row1, text='Stop', 
                                          command=self.docker_stop, width=10)
        self.docker_stop_btn.pack(side=tk.LEFT, padx=(0, 2))
        create_tooltip(self.docker_stop_btn, "Stop containers")
        
        self.docker_status_btn = ttk.Button(docker_row1, text='Status', 
                                            command=self.docker_status,
                                            style='Primary.TButton', width=10)
        self.docker_status_btn.pack(side=tk.LEFT, padx=(0, 2))
        create_tooltip(self.docker_status_btn, "Check status")
        
        self.docker_restart_btn = ttk.Button(docker_row1, text='Restart', 
                                             command=self.docker_restart, width=10)
        self.docker_restart_btn.pack(side=tk.LEFT)
        create_tooltip(self.docker_restart_btn, "Restart all")
        
        # Maintenance row
        docker_row2 = ttk.Frame(docker_frame)
        docker_row2.pack(fill=tk.X, pady=(0, 2))
        
        ttk.Button(docker_row2, text='Build', 
                  command=self.docker_build, width=10).pack(side=tk.LEFT, padx=(0, 2))
        
        ttk.Button(docker_row2, text='Clean', 
                  command=self.docker_clean, width=10).pack(side=tk.LEFT, padx=(0, 2))
        
        ttk.Button(docker_row2, text='� Browse', 
                  command=self.browse_compose_file, width=12).pack(side=tk.LEFT, padx=(0, 2))
        
        ttk.Button(docker_row2, text='Edit', 
                  command=self.edit_compose_file, width=10).pack(side=tk.LEFT)
        
        # Compose file path (separate row)
        docker_row3 = ttk.Frame(docker_frame)
        docker_row3.pack(fill=tk.X, pady=(2, 2))
        
        ttk.Label(docker_row3, text='File:', font=('Segoe UI', 8), width=5).pack(side=tk.LEFT, padx=(0, 2))
        
        # Load compose file path from config, fallback to default
        default_compose = self.config.get('compose_file', 'docker-compose.yml')
        self.compose_file_var = tk.StringVar(value=default_compose)
        compose_entry = ttk.Entry(docker_row3, textvariable=self.compose_file_var, 
                                 font=('Courier New', 8))
        compose_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Status Display
        self.docker_status_label = ttk.Label(docker_frame, text='Status: Unknown', 
                                             font=('Segoe UI', 8), 
                                             foreground='#6b7280')
        self.docker_status_label.pack(pady=(3, 0))
        
        # === SPARK JOB EXECUTION (Optimized) ===
        action_frame = ttk.LabelFrame(left_panel, text='⚡ Spark Job', padding=6)
        action_frame.pack(fill=tk.X, pady=(0, 4))
        
        # Quick Actions
        row1 = ttk.Frame(action_frame)
        row1.pack(fill=tk.X, pady=(0, 2))
        
        self.gen_btn = ttk.Button(row1, text='Generate', 
                                  command=self.on_generate, 
                                  style='Action.TButton', width=15)
        self.gen_btn.pack(side=tk.LEFT, padx=(0, 2))
        create_tooltip(self.gen_btn, "Generate commands (F5)")
        
        self.auto_btn = ttk.Button(row1, text='Run Now', 
                                   command=self.on_auto_run,
                                   style='Success.TButton', width=15)
        self.auto_btn.pack(side=tk.LEFT)
        create_tooltip(self.auto_btn, "Auto run job (Ctrl+R)")
        
        # Manual Steps
        row2 = ttk.Frame(action_frame)
        row2.pack(fill=tk.X, pady=(0, 2))
        
        self.step1_btn = ttk.Button(row2, text='1. Copy', command=self.on_step1, width=10)
        self.step1_btn.pack(side=tk.LEFT, padx=(0, 2))
        create_tooltip(self.step1_btn, "Copy file to container")
        
        self.step2_btn = ttk.Button(row2, text='2. Bash', command=self.on_step2, width=10)
        self.step2_btn.pack(side=tk.LEFT, padx=(0, 2))
        create_tooltip(self.step2_btn, "Open bash terminal")
        
        self.step3_btn = ttk.Button(row2, text='3. Submit', command=self.on_step3, width=10)
        self.step3_btn.pack(side=tk.LEFT)
        create_tooltip(self.step3_btn, "Submit to Spark")
        
        # Job Control
        row3 = ttk.Frame(action_frame)
        row3.pack(fill=tk.X, pady=(0, 2))
        
        self.stop_btn = ttk.Button(row3, text='Stop', command=self.on_stop, 
                                   state=tk.DISABLED, width=10)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 2))
        create_tooltip(self.stop_btn, "Stop job (Esc)")
        
        self.kill_btn = ttk.Button(row3, text='Kill', command=self.force_kill, width=10)
        self.kill_btn.pack(side=tk.LEFT, padx=(0, 2))
        create_tooltip(self.kill_btn, "Force kill")
        
        ttk.Button(row3, text='Copy Cmd', command=self.on_copy, width=10).pack(
            side=tk.LEFT, padx=(0, 2))
        ttk.Button(row3, text='Clear Log', command=self.clear_log, width=10).pack(
            side=tk.LEFT)
        
        # Utilities row
        row4 = ttk.Frame(action_frame)
        row4.pack(fill=tk.X)
        
        ttk.Button(row4, text='Spark UI', command=self.open_spark_ui, width=10).pack(
            side=tk.LEFT, padx=(0, 2))
        ttk.Button(row4, text='Hadoop UI', command=self.open_hadoop_ui, width=10).pack(
            side=tk.LEFT, padx=(0, 2))
        ttk.Button(row4, text='Export Log', command=self.export_log, width=10).pack(
            side=tk.LEFT, padx=(0, 2))
        
        # Progress Indicator
        self.progress = ttk.Progressbar(action_frame, mode='indeterminate', 
                                       style='Accent.Horizontal.TProgressbar')
        self.progress.pack(fill=tk.X, pady=(3, 0))
        
        # === GENERATED COMMANDS ===
        cmd_frame = ttk.LabelFrame(left_panel, text='📋 Commands', padding=6)
        cmd_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 0))
        
        self.cmd_text = scrolledtext.ScrolledText(cmd_frame, height=8, wrap=tk.WORD, 
                                                  bg=self.theme['bg_cmd'], 
                                                  fg=self.theme['text'],
                                                  font=('Courier New', 9),
                                                  relief='flat',
                                                  borderwidth=0,
                                                  padx=6,
                                                  pady=6)
        self.cmd_text.pack(fill=tk.BOTH, expand=True)
        self.cmd_text.bind('<Button-3>', lambda e: self.show_cmd_context_menu(e))
        
        # ========== RIGHT PANEL - EXECUTION LOG ==========
        
        # === Log Frame ===
        log_frame = ttk.LabelFrame(right_panel, text='📊 Execution Log', padding=6)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text_widget = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, 
                                                  bg=self.theme['bg_log'], 
                                                  fg='#2c3e50',
                                                  font=('Courier New', 9),
                                                  relief='flat',
                                                  borderwidth=0,
                                                  insertbackground='#60a5fa',
                                                  padx=8,
                                                  pady=8)
        self.log_text_widget.pack(fill=tk.BOTH, expand=True)
        self.log_text_widget.bind('<Button-3>', lambda e: self.show_log_context_menu(e))
        
        # Configure log tags with bright modern colors
        self.log_text_widget.tag_config('success', foreground='#10b981', font=('Courier New', 9, 'bold'))
        self.log_text_widget.tag_config('error', foreground='#ef4444', font=('Courier New', 9, 'bold'))
        self.log_text_widget.tag_config('warning', foreground='#f59e0b', font=('Courier New', 9, 'bold'))
        self.log_text_widget.tag_config('info', foreground='#60a5fa', font=('Courier New', 9, 'bold'))
        self.log_text_widget.tag_config('header', foreground='#a78bfa', font=('Courier New', 10, 'bold'))
    
    # Add context menu method references
    def show_cmd_context_menu(self, event):
        """Show context menu for command text"""
        menu = Menu(self.root, tearoff=0)
        menu.add_command(label='📋 Copy All', command=self.on_copy)
        menu.add_command(label='🔍 Select All', command=lambda: self.cmd_text.tag_add('sel', '1.0', 'end'))
        menu.add_separator()
        menu.add_command(label='💾 Save to file...', command=self.save_commands)
        menu.post(event.x_root, event.y_root)
    
    def show_log_context_menu(self, event):
        """Show context menu for log text"""
        log_widget = self.log_text_widget
        menu = Menu(self.root, tearoff=0)
        try:
            menu.add_command(label='📋 Copy Selection', command=lambda: self.root.clipboard_append(log_widget.selection_get()))
        except:
            pass
        menu.add_command(label='🔍 Select All', command=lambda: log_widget.tag_add('sel', '1.0', 'end'))
        menu.add_separator()
        menu.add_command(label='🗑️ Clear Log', command=self.clear_log)
        menu.add_command(label='💾 Export Log...', command=self.export_log)
        menu.post(event.x_root, event.y_root)

    def on_browse(self):
        """Open file dialog to select Python file"""
        filepath = filedialog.askopenfilename(
            title='Chọn file Python',
            filetypes=[('Python files', '*.py'), ('All files', '*.*')]
        )
        if filepath:
            self.file_var.set(filepath)
            self.callbacks['add_to_history'](self.config, filepath)
            self.history_combo['values'] = self.config['history']
            self.on_generate()

    def on_history_selected(self, event):
        """Load selected file from history"""
        selected = self.history_combo.get()
        if selected:
            self.file_var.set(selected)
            self.on_generate()

    def on_save_config(self):
        """Save current configuration"""
        self.config['container'] = self.container_var.get()
        self.config['master'] = self.master_var.get()
        self.callbacks['save_config'](self.config)
        self.callbacks['update_status']('✅ Configuration saved')
        tk.messagebox.showinfo('Saved', 'Cấu hình đã được lưu!')

    def on_generate(self):
        """Generate docker commands"""
        filepath = self.file_var.get().strip()
        if not filepath:
            tk.messagebox.showwarning('⚠️ Thiếu file', 'Vui lòng chọn hoặc nhập đường dẫn file Python')
            return
        
        container = self.container_var.get()
        master = self.master_var.get()
        
        text = generate_commands(filepath, container, master)
        self.cmd_text.delete('1.0', tk.END)
        self.cmd_text.insert(tk.END, text)
        self.callbacks['update_status']('📝 Commands generated')
        self.append_log(f'📝 Đã tạo lệnh cho: {Path(filepath).name}', 'info')

    def on_copy(self):
        """Copy commands to clipboard"""
        text = self.cmd_text.get('1.0', tk.END).strip()
        if not text:
            tk.messagebox.showinfo('ℹ️ Không có lệnh', 'Chưa có lệnh để sao chép. Nhấn Generate (F5) trước.')
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.callbacks['update_status']('📋 Commands copied')
        self.append_log('📋 Đã copy lệnh vào clipboard', 'success')
        
        # Visual feedback
        original_bg = self.copy_btn['style']
        self.copy_btn.config(style='Success.TButton')
        self.root.after(500, lambda: self.copy_btn.config(style=original_bg))

    def _start_log_processor(self):
        """Start thread-safe log processing in main thread"""
        def process_logs():
            try:
                while True:
                    s, tag = self.log_queue.get_nowait()
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    self.log_text_widget.insert(tk.END, f'[{timestamp}] {s}\n', tag)
                    self.log_text_widget.see(tk.END)
            except queue.Empty:
                pass
            finally:
                if hasattr(self, 'root') and self.root:
                    self.root.after(100, process_logs)
        
        if hasattr(self, 'root') and self.root:
            self.root.after(100, process_logs)
    
    def append_log(self, s: str, tag='normal'):
        """Thread-safe logging - add to queue"""
        # Auto-detect tag based on content
        if tag == 'normal':
            if '✅' in s or 'thành công' in s.lower() or 'completed' in s.lower() or 'success' in s.lower():
                tag = 'success'
            elif '❌' in s or 'error' in s.lower() or 'lỗi' in s.lower() or 'failed' in s.lower():
                tag = 'error'
            elif '⚠️' in s or 'warning' in s.lower() or 'cảnh báo' in s.lower() or 'timeout' in s.lower():
                tag = 'warning'
            elif '💡' in s or '→' in s or 'info' in s.lower() or 'bước' in s.lower():
                tag = 'info'
            elif '=' in s or '🎉' in s or '🚀' in s:
                tag = 'header'
        
        self.log_queue.put((s, tag))
    
    def _cleanup_future(self, future):
        """Remove completed future from active list"""
        if future in self._active_futures:
            self._active_futures.remove(future)
        
        # Check for exceptions
        try:
            exception = future.exception(timeout=0)
            if exception:
                self.append_log(f'❌ Thread error: {exception}', 'error')
        except:
            pass
    
    def cleanup(self):
        """Cleanup resources - call on app exit"""
        try:
            # Stop running jobs
            self.is_running = False
            
            # Shutdown thread pool
            if hasattr(self, 'thread_pool'):
                self.thread_pool.shutdown(wait=False)
                
            # Cancel active futures
            for future in self._active_futures:
                future.cancel()
            
            print("✅ SparkRunnerTab cleanup completed")
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")

    def get_file_info(self):
        """Get current file path and name"""
        filepath = self.file_var.get().strip()
        if not filepath:
            tk.messagebox.showwarning('Thiếu file', 'Vui lòng chọn file Python trước')
            return None, None
        
        path = Path(filepath)
        filename = path.name
        if not filename.endswith('.py'):
            filename += '.py'
            filepath = str(path.with_suffix('.py'))
        
        return filepath, filename

    def on_step1(self):
        """Step 1: Copy file to container"""
        filepath, filename = self.get_file_info()
        if not filepath:
            return
        
        if not os.path.exists(filepath):
            tk.messagebox.showerror('File không tồn tại', f'File không tìm thấy:\n{filepath}')
            return
        
        self.callbacks['add_to_history'](self.config, filepath)
        self.history_combo['values'] = self.config['history']
        
        # Use thread pool instead of daemon thread
        future = self.thread_pool.submit(self._run_step1, filepath, filename)
        self._active_futures.append(future)
        future.add_done_callback(lambda f: self._cleanup_future(f))

    def _run_step1(self, filepath, filename):
        """Execute step 1 in thread"""
        container = self.container_var.get()
        self.callbacks['update_status']('⏳ Copying file...')
        self.start_progress()
        self.append_log('=' * 60, 'header')
        self.append_log(f'→ BƯỚC 1: Copy file {filename} vào container {container}', 'info')
        
        if not shutil.which('docker'):
            self.append_log('❌ ERROR: docker không tìm thấy trong PATH', 'error')
            self.callbacks['update_status']('❌ docker not found')
            self.stop_progress()
            return
        
        try:
            cmd = ['docker', 'cp', filepath, f'{container}:/tmp']
            self.append_log(f'💻 Chạy: {" ".join(cmd)}', 'info')
            
            p = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            if p.stdout:
                self.append_log(p.stdout.strip())
            if p.stderr:
                self.append_log(f'⚠️ {p.stderr.strip()}', 'warning')
            
            if p.returncode == 0:
                self.append_log(f'✅ File đã được copy vào /tmp/{filename}', 'success')
                self.callbacks['update_status']('✅ Step 1 completed')
            else:
                self.append_log(f'❌ Lệnh thất bại với mã {p.returncode}', 'error')
                self.callbacks['update_status']('❌ Step 1 failed')
        except Exception as ex:
            self.append_log(f'❌ Exception: {ex}', 'error')
            self.callbacks['update_status']('❌ Error')
        finally:
            self.stop_progress()

    def on_step2(self):
        """Step 2: Open bash in container (interactive)"""
        container = self.container_var.get()
        self.append_log('=' * 60, 'header')
        self.append_log(f'→ BƯỚC 2: Mở bash tương tác trong container {container}', 'info')
        self.append_log('  💡 Lưu ý: Lệnh này sẽ mở terminal riêng', 'info')
        
        if not shutil.which('docker'):
            self.append_log('❌ ERROR: docker không tìm thấy trong PATH', 'error')
            return
        
        try:
            # Open in new terminal window
            cmd = f'docker exec -it {container} bash'
            
            # For Windows, use start command
            if sys.platform == 'win32':
                subprocess.Popen(['start', 'cmd', '/k', cmd], shell=True)
                self.append_log(f'✅ Đã mở terminal mới với lệnh: {cmd}', 'success')
            else:
                # For Unix-like systems
                subprocess.Popen(['x-terminal-emulator', '-e', cmd])
                self.append_log(f'✅ Đã mở terminal với lệnh: {cmd}', 'success')
            
            self.callbacks['update_status']('✅ Terminal opened')
        except Exception as ex:
            self.append_log(f'❌ Exception: {ex}', 'error')
            self.callbacks['update_status']('❌ Error')

    def on_step3(self):
        """Step 3: Run spark-submit"""
        filepath, filename = self.get_file_info()
        if not filepath:
            return
        
        # Use thread pool
        future = self.thread_pool.submit(self._run_step3, filename)
        self._active_futures.append(future)
        future.add_done_callback(lambda f: self._cleanup_future(f))

    def _run_step3(self, filename):
        """Execute step 3 in thread"""
        container = self.container_var.get()
        master = self.master_var.get()
        
        self.callbacks['update_status']('⏳ Running Spark job...')
        self.start_progress()
        self.append_log('=' * 60, 'header')
        self.append_log(f'→ BƯỚC 3: Chạy Spark job với file /tmp/{filename}', 'info')
        
        if not shutil.which('docker'):
            self.append_log('❌ ERROR: docker không tìm thấy trong PATH', 'error')
            self.callbacks['update_status']('❌ docker not found')
            self.stop_progress()
            return
        
        try:
            cmd = [
                'docker', 'exec', container,
                '/spark/bin/spark-submit', '--master', master, f'/tmp/{filename}'
            ]
            self.append_log(f'💻 Chạy: {" ".join(cmd)}', 'info')
            
            p = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=300)  # 5 min timeout
            
            if p.stdout:
                self.append_log('--- 📊 Output ---', 'info')
                self.append_log(p.stdout.strip())
            if p.stderr:
                self.append_log('--- ⚠️ Errors/Warnings ---', 'warning')
                self.append_log(p.stderr.strip())
            
            if p.returncode == 0:
                self.append_log('✅ Spark job hoàn thành thành công!', 'success')
                self.callbacks['update_status']('✅ Step 3 completed')
            else:
                self.append_log(f'❌ Spark job thất bại với mã {p.returncode}', 'error')
                self.callbacks['update_status']('❌ Step 3 failed')
        except subprocess.TimeoutExpired:
            self.append_log('⏱️ Timeout: Job chạy quá 5 phút', 'warning')
            self.callbacks['update_status']('⏱️ Timeout')
        except Exception as ex:
            self.append_log(f'❌ Exception: {ex}', 'error')
            self.callbacks['update_status']('❌ Error')
        finally:
            self.stop_progress()

    def on_auto_run(self):
        """Auto run all steps sequentially"""
        filepath, filename = self.get_file_info()
        if not filepath:
            return
        
        if not os.path.exists(filepath):
            tk.messagebox.showerror('File không tồn tại', f'File không tìm thấy:\n{filepath}')
            return
        
        self.callbacks['add_to_history'](self.config, filepath)
        self.history_combo['values'] = self.config['history']
        
        # Use thread pool
        future = self.thread_pool.submit(self._run_auto, filepath, filename)
        self._active_futures.append(future)
        future.add_done_callback(lambda f: self._cleanup_future(f))

    def _run_auto(self, filepath, filename):
        """Execute all steps automatically"""
        container = self.container_var.get()
        master = self.master_var.get()
        
        self.callbacks['update_status']('⏳ Running auto sequence...')
        self.start_progress()
        self.append_log('=' * 70, 'header')
        self.append_log('🚀 BẮT ĐẦU CHẠY TỰ ĐỘNG', 'header')
        self.append_log('=' * 70, 'header')
        
        if not shutil.which('docker'):
            self.append_log('❌ ERROR: docker không tìm thấy trong PATH', 'error')
            self.callbacks['update_status']('❌ docker not found')
            self.stop_progress()
            return
        
        try:
            # Step 1: Copy file
            self.append_log(f'\n→ BƯỚC 1: Copy file {filename}', 'info')
            cmd1 = ['docker', 'cp', filepath, f'{container}:/tmp']
            self.append_log(f'  💻 $ {" ".join(cmd1)}', 'info')
            
            p1 = subprocess.run(cmd1, capture_output=True, text=True, encoding='utf-8', errors='replace')
            if p1.stdout:
                self.append_log(f'  {p1.stdout.strip()}')
            if p1.stderr:
                self.append_log(f'  ⚠️ {p1.stderr.strip()}', 'warning')
            
            if p1.returncode != 0:
                self.append_log(f'❌ Bước 1 thất bại với mã {p1.returncode}. Dừng lại.', 'error')
                self.callbacks['update_status']('❌ Failed at step 1')
                self.stop_progress()
                return
            
            self.append_log('✅ Bước 1 hoàn thành', 'success')
            
            # Check if should stop
            if not self.is_running:
                self.append_log('⏹️ Đã dừng theo yêu cầu người dùng', 'warning')
                self.stop_progress()
                return
            
            # Step 2: Run Spark (skip interactive bash)
            self.append_log(f'\n→ BƯỚC 2: Chạy Spark job', 'info')
            cmd2 = [
                'docker', 'exec', container,
                '/spark/bin/spark-submit', '--master', master, f'/tmp/{filename}'
            ]
            self.append_log(f'  💻 $ {" ".join(cmd2)}', 'info')
            
            p2 = subprocess.run(cmd2, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=300)
            
            if p2.stdout:
                self.append_log('\n--- 📊 Spark Output ---', 'info')
                self.append_log(p2.stdout.strip())
            if p2.stderr:
                self.append_log('\n--- ⚠️ Spark Errors/Warnings ---', 'warning')
                self.append_log(p2.stderr.strip())
            
            if p2.returncode != 0:
                self.append_log(f'\n❌ Spark job thất bại với mã {p2.returncode}', 'error')
                self.callbacks['update_status']('❌ Spark job failed')
            else:
                self.append_log('\n✅ Bước 2 hoàn thành', 'success')
                self.append_log('=' * 70, 'header')
                self.append_log('🎉 TẤT CẢ CÁC BƯỚC HOÀN THÀNH THÀNH CÔNG!', 'success')
                self.append_log('=' * 70, 'header')
                self.callbacks['update_status']('✅ All steps completed')
                
                # Success notification disabled - log already visible
                # if tk.messagebox.askyesno('🎉 Thành công', 
                #                       'Spark job đã chạy thành công!\nBạn có muốn xem log chi tiết không?'):
                #     pass  # Log already visible
        
        except subprocess.TimeoutExpired:
            self.append_log('\n⏱️ Timeout: Spark job chạy quá 5 phút', 'warning')
            self.callbacks['update_status']('⏱️ Timeout')
        except Exception as ex:
            self.append_log(f'\n❌ Exception: {ex}', 'error')
            self.callbacks['update_status']('❌ Error')
        finally:
            self.stop_progress()

    def show_file_context_menu(self, event):
        """Show context menu for file entry"""
        menu = Menu(self.root, tearoff=0)
        menu.add_command(label='📂 Browse...', command=self.on_browse)
        menu.add_command(label='📋 Paste', command=lambda: self.file_entry.event_generate('<<Paste>>'))
        menu.add_command(label='✖ Clear', command=self.clear_file)
        menu.add_separator()
        menu.add_command(label='📂 Open in Explorer', command=self.open_in_explorer)
        menu.post(event.x_root, event.y_root)
    
    def clear_file(self):
        """Clear file entry"""
        self.file_var.set('')
        self.cmd_text.delete('1.0', tk.END)
    
    def clear_history(self):
        """Clear file history"""
        if tk.messagebox.askyesno('Xác nhận', 'Bạn có chắc muốn xóa toàn bộ lịch sử file?'):
            self.config['history'] = []
            self.callbacks['save_config'](self.config)
            self.history_combo['values'] = []
            self.append_log('🗑️ Đã xóa lịch sử file', 'info')
    
    def refresh_history(self):
        """Refresh history combo"""
        self.config = self.callbacks['load_config']()
        self.history_combo['values'] = self.config['history']
        self.append_log('🔄 Đã làm mới lịch sử', 'info')
    
    def reset_config(self):
        """Reset configuration to default"""
        if tk.messagebox.askyesno('Xác nhận', 'Khôi phục cấu hình về mặc định?'):
            self.container_var.set('spark-worker')
            self.master_var.set('spark://spark-master:7077')
            self.on_save_config()
            self.append_log('↺ Đã khôi phục cấu hình mặc định', 'info')

    def clear_log(self):
        """Clear log text"""
        self.log_text_widget.delete('1.0', tk.END)
        self.append_log('🗑️ Log đã được xóa', 'info')
    
    def export_log(self):
        """Export log to file"""
        filepath = tk.filedialog.asksaveasfilename(
            defaultextension='.txt',
            filetypes=[('Text files', '*.txt'), ('All files', '*.*')],
            initialfile=f'spark_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        )
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(self.log_text_widget.get('1.0', tk.END))
                self.append_log(f'💾 Log đã được lưu: {filepath}', 'success')
                tk.messagebox.showinfo('Thành công', f'Log đã được lưu vào:\n{filepath}')
            except Exception as e:
                self.append_log(f'❌ Lỗi khi lưu log: {e}', 'error')
    
    def save_commands(self):
        """Save generated commands to file"""
        filepath = tk.filedialog.asksaveasfilename(
            defaultextension='.sh',
            filetypes=[('Shell script', '*.sh'), ('Batch file', '*.bat'), ('Text files', '*.txt')],
            initialfile='spark_commands.sh'
        )
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(self.cmd_text.get('1.0', tk.END))
                self.append_log(f'💾 Lệnh đã được lưu: {filepath}', 'success')
            except Exception as e:
                self.append_log(f'❌ Lỗi khi lưu lệnh: {e}', 'error')
    
    def open_in_explorer(self):
        """Open file location in explorer"""
        filepath = self.file_var.get().strip()
        if filepath and os.path.exists(filepath):
            folder = os.path.dirname(filepath)
            if sys.platform == 'win32':
                os.startfile(folder)
            else:
                subprocess.Popen(['xdg-open', folder])
        else:
            tk.messagebox.showwarning('File không tồn tại', 'Vui lòng chọn file hợp lệ trước')
    
    def on_stop(self):
        """Stop running process"""
        if self.is_running:
            if tk.messagebox.askyesno('Xác nhận', 'Dừng tiến trình đang chạy?'):
                self.is_running = False
                self.append_log('⏹️ Đã yêu cầu dừng tiến trình', 'warning')
                self.stop_progress()
        else:
            self.append_log('⚠️ Không có tiến trình nào đang chạy', 'warning')
    
    @retry_on_error(max_retries=3, delay=2)
    def docker_start(self):
        """Start Docker containers using docker-compose"""
        self.append_log('🐳 Đang khởi động Docker containers...', 'info')
        self.callbacks['update_status']('🐳 Starting containers...')
        
        def run_docker_start():
            try:
                # Get compose file from input
                compose_file = self.compose_file_var.get()
                
                if not os.path.exists(compose_file):
                    self.append_log(f'❌ Không tìm thấy file: {compose_file}', 'error')
                    self.callbacks['update_status']('❌ Compose file not found')
                    return
                
                # Check if Docker Desktop is running
                self.append_log('🔍 Kiểm tra Docker Desktop...', 'info')
                docker_check = subprocess.run(
                    ['docker', 'info'],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=10  # Increased timeout for initial check
                )
                
                if docker_check.returncode != 0:
                    self.append_log('⚠️ Docker Desktop chưa được khởi động!', 'warning')
                    self.append_log('🚀 Đang tự động mở Docker Desktop...', 'info')
                    
                    # Try to start Docker Desktop
                    try:
                        # Windows: Start Docker Desktop
                        if sys.platform == 'win32':
                            subprocess.Popen([
                                'powershell.exe', 
                                '-Command', 
                                'Start-Process "C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe"'
                            ])
                        elif sys.platform == 'darwin':  # macOS
                            subprocess.Popen(['open', '-a', 'Docker'])
                        else:  # Linux
                            subprocess.Popen(['systemctl', '--user', 'start', 'docker-desktop'])
                        
                        self.append_log('✅ Đã gửi lệnh khởi động Docker Desktop', 'success')
                        self.append_log('⏳ Đợi Docker Desktop sẵn sàng...', 'info')
                        
                        # Wait for Docker Desktop to be ready (max 60 seconds)
                        max_wait = 60
                        waited = 0
                        while waited < max_wait:
                            time.sleep(5)
                            waited += 5
                            
                            check = subprocess.run(
                                ['docker', 'info'],
                                capture_output=True,
                                timeout=120  # Increased timeout for Docker Desktop startup
                            )
                            
                            if check.returncode == 0:
                                self.append_log(f'✅ Docker Desktop đã sẵn sàng sau {waited}s', 'success')
                                break
                            else:
                                self.append_log(f'⏳ Đang đợi... ({waited}s/{max_wait}s)', 'info')
                        
                        if waited >= max_wait:
                            self.append_log('❌ Timeout: Docker Desktop không khởi động được', 'error')
                            self.append_log('💡 Hãy kiểm tra và mở Docker Desktop thủ công', 'warning')
                            self.callbacks['update_status']('❌ Docker Desktop timeout')
                            self.docker_status_label.config(text='Docker status: Not running ❌', foreground='#dc3545')
                            return
                            
                    except Exception as e:
                        self.append_log(f'❌ Không thể mở Docker Desktop: {e}', 'error')
                        self.append_log('💡 Hãy mở Docker Desktop thủ công và nhấn START lại', 'warning')
                        self.callbacks['update_status']('❌ Cannot start Docker Desktop')
                        self.docker_status_label.config(text='Docker status: Not running ❌', foreground='#dc3545')
                        return
                else:
                    self.append_log('✅ Docker Desktop đang chạy', 'success')
                
                # Check current status (including stopped containers)
                self.append_log('🔍 Kiểm tra trạng thái containers...', 'info')
                status_result = subprocess.run(
                    ['docker-compose', '-f', compose_file, 'ps', '-a'],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=10
                )
                
                # Check if containers are running
                if status_result.returncode == 0 and status_result.stdout.strip():
                    # Parse the output
                    has_running = 'Up' in status_result.stdout
                    has_stopped = 'Exit' in status_result.stdout or 'Created' in status_result.stdout
                    
                    if has_running and not has_stopped:
                        # All containers running
                        self.append_log('✅ Containers đã đang chạy!', 'success')
                        self.append_log(status_result.stdout, 'info')
                        self.callbacks['update_status']('✅ Containers already running')
                        self.docker_status_label.config(text='Docker status: Running ✅', foreground='#28a745')
                        return
                    
                    if has_stopped or has_running:
                        # Some stopped or mixed state - cleanup needed
                        self.append_log('🔄 Phát hiện containers cũ, đang dọn dẹp...', 'warning')
                        cleanup_result = subprocess.run(
                            ['docker-compose', '-f', compose_file, 'down', '--remove-orphans'],
                            capture_output=True,
                            text=True,
                            encoding='utf-8',
                            errors='replace',
                            timeout=60
                        )
                        if cleanup_result.returncode == 0:
                            self.append_log('✅ Đã dọn dẹp containers cũ', 'success')
                
                # Also check for orphaned containers with docker ps
                self.append_log('🔍 Kiểm tra containers bị mồ côi...', 'info')
                orphan_check = subprocess.run(
                    ['docker', 'ps', '-a', '--filter', 'name=spark-master', '--filter', 'name=namenode', 
                     '--filter', 'name=spark-worker', '--filter', 'name=datanode', '--format', '{{.Names}}'],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=10
                )
                
                if orphan_check.returncode == 0 and orphan_check.stdout.strip():
                    orphan_containers = orphan_check.stdout.strip().split('\n')
                    self.append_log(f'⚠️ Tìm thấy {len(orphan_containers)} containers cũ, đang xóa...', 'warning')
                    for container in orphan_containers:
                        subprocess.run(
                            ['docker', 'rm', '-f', container],
                            capture_output=True,
                            timeout=10
                        )
                    self.append_log('✅ Đã xóa containers cũ', 'success')
                
                # Run docker-compose up -d
                self.append_log('🚀 Đang khởi động containers...', 'info')
                result = subprocess.run(
                    ['docker-compose', '-f', compose_file, 'up', '-d'],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=180
                )
                
                if result.returncode == 0:
                    self.append_log('✅ Docker containers đã được khởi động!', 'success')
                    # Filter out warnings from output
                    output_lines = result.stdout.split('\n')
                    filtered_output = '\n'.join([
                        line for line in output_lines 
                        if 'level=warning' not in line and 'obsolete' not in line and line.strip()
                    ])
                    if filtered_output:
                        self.append_log(filtered_output, 'info')
                    self.callbacks['update_status']('✅ Containers started')
                    self.docker_status_label.config(text='Docker status: Running ✅', foreground='#28a745')
                else:
                    self.append_log('❌ Lỗi khi khởi động containers:', 'error')
                    self.append_log(result.stderr, 'error')
                    self.callbacks['update_status']('❌ Failed to start')
                    raise Exception(f"Docker start failed")
                    
            except FileNotFoundError:
                self.append_log('❌ docker-compose không được cài đặt!', 'error')
                self.append_log('💡 Cài đặt Docker Desktop: https://www.docker.com/products/docker-desktop', 'info')
                self.callbacks['update_status']('❌ docker-compose not found')
                raise
            except subprocess.TimeoutExpired:
                self.append_log('❌ Timeout: Khởi động containers quá lâu (>3 phút)', 'error')
                self.callbacks['update_status']('❌ Timeout')
                raise
            except Exception as e:
                self.append_log(f'❌ Lỗi: {e}', 'error')
                self.callbacks['update_status']('❌ Error')
                raise
        
        # Run in thread pool
        future = self.thread_pool.submit(run_docker_start)
        self._active_futures.append(future)
        future.add_done_callback(self._cleanup_future)
    
    @retry_on_error(max_retries=2, delay=1)
    def docker_stop(self):
        """Stop Docker containers using docker-compose"""
        if tk.messagebox.askyesno('Xác nhận', 'Dừng tất cả Docker containers?'):
            self.append_log('🐳 Đang dừng Docker containers...', 'info')
            self.callbacks['update_status']('🐳 Stopping containers...')
            
            def run_docker_stop():
                try:
                    compose_file = self.compose_file_var.get()
                    result = subprocess.run(
                        ['docker-compose', '-f', compose_file, 'down'],
                        capture_output=True,
                        text=True,
                        encoding='utf-8',
                        errors='replace',
                        timeout=60
                    )
                    
                    if result.returncode == 0:
                        self.append_log('✅ Docker containers đã được dừng!', 'success')
                        self.append_log(result.stdout, 'info')
                        self.callbacks['update_status']('✅ Containers stopped')
                        self.docker_status_label.config(text='Docker status: Stopped ⏹️', foreground='#dc3545')
                    else:
                        self.append_log('❌ Lỗi khi dừng containers:', 'error')
                        self.append_log(result.stderr, 'error')
                        self.callbacks['update_status']('❌ Failed to stop')
                        raise Exception(f"Docker stop failed: {result.stderr}")
                        
                except FileNotFoundError:
                    self.append_log('❌ docker-compose không được cài đặt!', 'error')
                    self.callbacks['update_status']('❌ docker-compose not found')
                    raise
                except subprocess.TimeoutExpired:
                    self.append_log('❌ Timeout: Dừng containers quá lâu (>1 phút)', 'error')
                    self.callbacks['update_status']('❌ Timeout')
                    raise
                except Exception as e:
                    self.append_log(f'❌ Lỗi: {e}', 'error')
                    self.callbacks['update_status']('❌ Error')
                    raise
            
            # Run in thread pool
            future = self.thread_pool.submit(run_docker_stop)
            self._active_futures.append(future)
            future.add_done_callback(self._cleanup_future)
    
    @retry_on_error(max_retries=2, delay=2)
    def docker_restart(self):
        """Restart Docker containers using docker-compose"""
        self.append_log('🐳 Đang khởi động lại Docker containers...', 'info')
        self.callbacks['update_status']('🐳 Restarting containers...')
        
        def run_docker_restart():
            try:
                compose_file = self.compose_file_var.get()
                result = subprocess.run(
                    ['docker-compose', '-f', compose_file, 'restart'],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=90
                )
                
                if result.returncode == 0:
                    self.append_log('✅ Docker containers đã được khởi động lại!', 'success')
                    self.append_log(result.stdout, 'info')
                    self.callbacks['update_status']('✅ Containers restarted')
                    self.docker_status_label.config(text='Docker status: Running ✅', foreground='#28a745')
                else:
                    self.append_log('❌ Lỗi khi restart containers:', 'error')
                    self.append_log(result.stderr, 'error')
                    self.callbacks['update_status']('❌ Failed to restart')
                    raise Exception(f"Docker restart failed: {result.stderr}")
                    
            except FileNotFoundError:
                self.append_log('❌ docker-compose không được cài đặt!', 'error')
                self.callbacks['update_status']('❌ docker-compose not found')
                raise
            except subprocess.TimeoutExpired:
                self.append_log('❌ Timeout: Restart containers quá lâu (>90s)', 'error')
                self.callbacks['update_status']('❌ Timeout')
                raise
            except Exception as e:
                self.append_log(f'❌ Lỗi: {e}', 'error')
                self.callbacks['update_status']('❌ Error')
                raise
        
        # Run in thread pool
        future = self.thread_pool.submit(run_docker_restart)
        self._active_futures.append(future)
        future.add_done_callback(self._cleanup_future)
    
    def docker_status(self, silent=False):
        """Check Docker containers status
        
        Args:
            silent (bool): If True, only update status label without logging
        """
        if not silent:
            self.append_log('🐳 Đang kiểm tra trạng thái containers...', 'info')
        self.callbacks['update_status']('🐳 Checking status...')
        
        def run_docker_status():
            try:
                # Check if Docker Desktop is running first
                docker_check = subprocess.run(
                    ['docker', 'info'],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=10  # Increased timeout for Docker Desktop startup
                )
                
                if docker_check.returncode != 0:
                    if not silent:
                        self.append_log('❌ Docker Desktop chưa được khởi động!', 'error')
                    self.docker_status_label.config(text='Docker status: Not running ❌', foreground='#dc3545')
                    if not silent:
                        self.callbacks['update_status']('❌ Docker not running')
                    else:
                        self.callbacks['update_status']('✅ Ready')
                    return
                
                # docker-compose ps
                compose_file = self.compose_file_var.get()
                result = subprocess.run(
                    ['docker-compose', '-f', compose_file, 'ps'],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=10
                )
                
                if result.returncode == 0:
                    if not silent:
                        self.append_log('📊 Trạng thái containers:', 'info')
                        self.append_log(result.stdout, 'info')
                    
                    # Check if any containers are running
                    if 'Up' in result.stdout:
                        self.docker_status_label.config(text='Docker status: Running ✅', foreground='#28a745')
                        self.callbacks['update_status']('✅ Containers running')
                    else:
                        self.docker_status_label.config(text='Docker status: Stopped ⏹️', foreground='#dc3545')
                        if not silent:
                            self.callbacks['update_status']('⚠️ No containers running')
                        else:
                            self.callbacks['update_status']('✅ Ready')
                else:
                    if not silent:
                        self.append_log('❌ Không thể kiểm tra trạng thái', 'error')
                        self.append_log(result.stderr, 'error')
                    self.docker_status_label.config(text='Docker status: Error ❌', foreground='#dc3545')
                    if not silent:
                        self.callbacks['update_status']('❌ Status check failed')
                    else:
                        self.callbacks['update_status']('✅ Ready')
                    
            except FileNotFoundError:
                if not silent:
                    self.append_log('❌ docker-compose không được cài đặt!', 'error')
                self.docker_status_label.config(text='Docker status: Not installed ❌', foreground='#dc3545')
                if not silent:
                    self.callbacks['update_status']('❌ docker-compose not found')
                else:
                    self.callbacks['update_status']('✅ Ready')
            except subprocess.TimeoutExpired:
                if not silent:
                    self.append_log('❌ Timeout khi kiểm tra status', 'error')
                    self.callbacks['update_status']('❌ Timeout')
                else:
                    self.docker_status_label.config(text='Docker status: Unknown ❓', foreground='#ffc107')
                    self.callbacks['update_status']('✅ Ready')
            except Exception as e:
                if not silent:
                    self.append_log(f'❌ Lỗi: {e}', 'error')
                    self.callbacks['update_status']('❌ Error')
                else:
                    self.docker_status_label.config(text='Docker status: Unknown ❓', foreground='#ffc107')
                    self.callbacks['update_status']('✅ Ready')
        
        # Run in thread pool
        future = self.thread_pool.submit(run_docker_status)
        self._active_futures.append(future)
        future.add_done_callback(self._cleanup_future)
    
    def browse_compose_file(self):
        """Browse for docker-compose.yml file"""
        filepath = tk.filedialog.askopenfilename(
            title='Chọn docker-compose file',
            filetypes=[
                ('Docker Compose files', 'docker-compose.yml;docker-compose.yaml'),
                ('YAML files', '*.yml;*.yaml'),
                ('All files', '*.*')
            ],
            initialfile='docker-compose.yml'
        )
        
        if filepath:
            self.compose_file_var.set(filepath)
            self.append_log(f'📄 Đã chọn file: {filepath}', 'success')
            self.callbacks['update_status'](f'✅ Selected: {Path(filepath).name}')
            
            # Check if file exists and is readable
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.append_log(f'✅ File hợp lệ ({len(content)} bytes)', 'success')
                except Exception as e:
                    self.append_log(f'⚠️ Không thể đọc file: {e}', 'warning')
    
    def edit_compose_file(self):
        """Open docker-compose.yml in editor"""
        compose_file = self.compose_file_var.get()
        
        if not os.path.exists(compose_file):
            if tk.messagebox.askyesno('File không tồn tại', 
                                  f'File {compose_file} không tồn tại.\n\nTạo file mới?'):
                self.create_compose_file()
                return
            else:
                return
        
        # Open editor window
        editor_window = tk.Toplevel(self.root)
        editor_window.title(f'✏️ Edit: {compose_file}')
        editor_window.geometry('900x700')
        
        # Top frame with buttons
        top_frame = ttk.Frame(editor_window, padding=10)
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text=f'📄 {compose_file}', 
                 font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 20))
        
        save_btn = ttk.Button(top_frame, text='💾 Save', 
                             command=lambda: self.save_compose_file(editor_window, text_editor),
                             width=12, style='Success.TButton')
        save_btn.pack(side=tk.LEFT, padx=5)
        
        reload_btn = ttk.Button(top_frame, text='🔄 Reload', 
                               command=lambda: self.reload_compose_file(text_editor),
                               width=12)
        reload_btn.pack(side=tk.LEFT, padx=5)
        
        validate_btn = ttk.Button(top_frame, text='✓ Validate', 
                                 command=lambda: self.validate_compose_file(text_editor),
                                 width=12)
        validate_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = ttk.Button(top_frame, text='✖ Close', 
                              command=editor_window.destroy, width=12)
        close_btn.pack(side=tk.RIGHT, padx=5)
        
        # Text editor
        editor_frame = ttk.Frame(editor_window, padding=10)
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        text_editor = scrolledtext.ScrolledText(editor_frame, wrap=tk.NONE, 
                                               font=('Courier New', 10),
                                               bg='#1e1e1e', fg='#d4d4d4',
                                               insertbackground='white')
        text_editor.pack(fill=tk.BOTH, expand=True)
        
        # Load content
        try:
            with open(compose_file, 'r', encoding='utf-8') as f:
                content = f.read()
            text_editor.insert('1.0', content)
            self.append_log(f'✏️ Đã mở editor cho: {compose_file}', 'info')
        except Exception as e:
            tk.messagebox.showerror('Error', f'Không thể đọc file:\n{e}')
            editor_window.destroy()
            return
        
        # Status bar
        status_frame = ttk.Frame(editor_window)
        status_frame.pack(fill=tk.X)
        
        status_label = ttk.Label(status_frame, text=f'Ready | Lines: {len(content.splitlines())}', 
                                relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(fill=tk.X)
        
        # Update line count on edit
        def update_line_count(event=None):
            lines = text_editor.get('1.0', tk.END).count('\n')
            status_label.config(text=f'Modified | Lines: {lines}')
        
        text_editor.bind('<<Modified>>', update_line_count)
    
    def save_compose_file(self, window, text_editor):
        """Save docker-compose.yml file"""
        compose_file = self.compose_file_var.get()
        
        try:
            content = text_editor.get('1.0', tk.END).rstrip()
            
            # Backup original file
            if os.path.exists(compose_file):
                backup_file = f"{compose_file}.backup"
                shutil.copy(compose_file, backup_file)
                self.append_log(f'💾 Backup tạo: {backup_file}', 'info')
            
            # Save new content
            with open(compose_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.append_log(f'✅ Đã lưu file: {compose_file}', 'success')
            self.callbacks['update_status']('✅ File saved')
            tk.messagebox.showinfo('Success', 'File đã được lưu thành công!\n\nRestart containers để áp dụng thay đổi.')
            
        except Exception as e:
            self.append_log(f'❌ Lỗi khi lưu file: {e}', 'error')
            tk.messagebox.showerror('Error', f'Không thể lưu file:\n{e}')
    
    def reload_compose_file(self, text_editor):
        """Reload docker-compose.yml file"""
        compose_file = self.compose_file_var.get()
        
        if tk.messagebox.askyesno('Xác nhận', 'Reload file sẽ mất các thay đổi chưa lưu.\n\nContinue?'):
            try:
                with open(compose_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                text_editor.delete('1.0', tk.END)
                text_editor.insert('1.0', content)
                self.append_log(f'🔄 Đã reload file: {compose_file}', 'info')
                
            except Exception as e:
                tk.messagebox.showerror('Error', f'Không thể reload file:\n{e}')
    
    def validate_compose_file(self, text_editor):
        """Validate docker-compose.yml syntax"""
        self.append_log('🔍 Đang validate docker-compose file...', 'info')
        
        try:
            import yaml
            content = text_editor.get('1.0', tk.END)
            data = yaml.safe_load(content)
            
            # Basic validation
            errors = []
            
            if not isinstance(data, dict):
                errors.append('❌ File không phải định dạng YAML hợp lệ')
            else:
                if 'version' not in data:
                    errors.append('⚠️ Thiếu trường "version"')
                
                if 'services' not in data:
                    errors.append('❌ Thiếu trường "services"')
                elif not isinstance(data['services'], dict):
                    errors.append('❌ Trường "services" không hợp lệ')
                elif len(data['services']) == 0:
                    errors.append('⚠️ Không có service nào được định nghĩa')
            
            if errors:
                error_msg = '\n'.join(errors)
                self.append_log('⚠️ Validation issues:', 'warning')
                for err in errors:
                    self.append_log(f'  {err}', 'warning')
                tk.messagebox.showwarning('Validation Issues', error_msg)
            else:
                service_count = len(data.get('services', {}))
                self.append_log(f'✅ File hợp lệ! ({service_count} services)', 'success')
                tk.messagebox.showinfo('Success', 
                                  f'✅ docker-compose.yml hợp lệ!\n\n'
                                  f'Version: {data.get("version", "N/A")}\n'
                                  f'Services: {service_count}\n'
                                  f'Service names: {", ".join(data.get("services", {}).keys())}')
                
        except ImportError:
            self.append_log('⚠️ Module "yaml" không được cài đặt', 'warning')
            self.append_log('💡 Cài đặt: pip install pyyaml', 'info')
            tk.messagebox.showwarning('Module Missing', 
                                 'Module "yaml" không được cài đặt.\n\n'
                                 'Cài đặt: pip install pyyaml')
        except yaml.YAMLError as e:
            self.append_log(f'❌ YAML syntax error: {e}', 'error')
            tk.messagebox.showerror('YAML Error', f'Lỗi cú pháp YAML:\n\n{e}')
        except Exception as e:
            self.append_log(f'❌ Validation error: {e}', 'error')
            tk.messagebox.showerror('Error', f'Lỗi khi validate:\n{e}')
    
    def create_compose_file(self):
        """Create new docker-compose.yml from template"""
        compose_file = self.compose_file_var.get()
        
        # Check if file exists
        if os.path.exists(compose_file):
            if not tk.messagebox.askyesno('File đã tồn tại', 
                                      f'File {compose_file} đã tồn tại.\n\nGhi đè?'):
                return
        
        # Template selection dialog
        template_window = tk.Toplevel(self.root)
        template_window.title('➕ Tạo docker-compose.yml')
        template_window.geometry('600x400')
        
        ttk.Label(template_window, text='Chọn template:', 
                 font=('Segoe UI', 11, 'bold')).pack(pady=10)
        
        # Template options
        templates = {
            'Hadoop + Spark Cluster': self.get_hadoop_spark_template(),
            'Spark Standalone': self.get_spark_standalone_template(),
            'Basic HDFS': self.get_basic_hdfs_template(),
            'Empty Template': self.get_empty_template()
        }
        
        selected_template = tk.StringVar(value='Hadoop + Spark Cluster')
        
        for name in templates.keys():
            rb = ttk.Radiobutton(template_window, text=name, 
                                variable=selected_template, value=name)
            rb.pack(anchor=tk.W, padx=30, pady=5)
        
        # Preview
        preview_frame = ttk.LabelFrame(template_window, text='Preview', padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        preview_text = scrolledtext.ScrolledText(preview_frame, height=10, 
                                                font=('Courier New', 8), wrap=tk.NONE)
        preview_text.pack(fill=tk.BOTH, expand=True)
        
        def update_preview(*args):
            template_name = selected_template.get()
            preview_text.delete('1.0', tk.END)
            preview_text.insert('1.0', templates[template_name])
        
        selected_template.trace('w', update_preview)
        update_preview()
        
        # Buttons
        btn_frame = ttk.Frame(template_window)
        btn_frame.pack(pady=10)
        
        def create_file():
            template_name = selected_template.get()
            content = templates[template_name]
            
            try:
                with open(compose_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.append_log(f'✅ Đã tạo file: {compose_file}', 'success')
                self.append_log(f'📋 Template: {template_name}', 'info')
                self.callbacks['update_status']('✅ File created')
                
                template_window.destroy()
                tk.messagebox.showinfo('Success', 
                                  f'File đã được tạo thành công!\n\n'
                                  f'File: {compose_file}\n'
                                  f'Template: {template_name}\n\n'
                                  f'Click "✏️ Edit" để chỉnh sửa.')
                
            except Exception as e:
                tk.messagebox.showerror('Error', f'Không thể tạo file:\n{e}')
        
        ttk.Button(btn_frame, text='✓ Create', command=create_file, 
                  width=15, style='Success.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text='✖ Cancel', command=template_window.destroy, 
                  width=15).pack(side=tk.LEFT, padx=5)
    
    def get_hadoop_spark_template(self):
        """Get Hadoop + Spark cluster template"""
        return """version: '3'

services:
  namenode:
    image: bde2020/hadoop-namenode:2.0.0-hadoop3.2.1-java8
    container_name: namenode
    ports:
      - "9870:9870"
      - "8020:8020"
    volumes:
      - hadoop_namenode:/hadoop/dfs/name
    environment:
      - CLUSTER_NAME=hadoop-cluster
    env_file:
      - ./hadoop.env
    networks:
      - bigdata

  datanode:
    image: bde2020/hadoop-datanode:2.0.0-hadoop3.2.1-java8
    container_name: datanode
    volumes:
      - hadoop_datanode:/hadoop/dfs/data
    environment:
      SERVICE_PRECONDITION: "namenode:9870"
    env_file:
      - ./hadoop.env
    networks:
      - bigdata

  spark-master:
    image: bde2020/spark-master:3.0.0-hadoop3.2
    container_name: spark-master
    ports:
      - "8080:8080"
      - "7077:7077"
    environment:
      - INIT_DAEMON_STEP=setup_spark
    networks:
      - bigdata

  spark-worker:
    image: bde2020/spark-worker:3.0.0-hadoop3.2
    container_name: spark-worker
    depends_on:
      - spark-master
    ports:
      - "8081:8081"
    environment:
      - "SPARK_MASTER=spark://spark-master:7077"
    networks:
      - bigdata

volumes:
  hadoop_namenode:
  hadoop_datanode:

networks:
  bigdata:
    driver: bridge
"""
    
    def get_spark_standalone_template(self):
        """Get Spark standalone template"""
        return """version: '3'

services:
  spark-master:
    image: bde2020/spark-master:3.0.0-hadoop3.2
    container_name: spark-master
    ports:
      - "8080:8080"
      - "7077:7077"
    environment:
      - INIT_DAEMON_STEP=setup_spark
    networks:
      - spark_network

  spark-worker-1:
    image: bde2020/spark-worker:3.0.0-hadoop3.2
    container_name: spark-worker-1
    depends_on:
      - spark-master
    ports:
      - "8081:8081"
    environment:
      - "SPARK_MASTER=spark://spark-master:7077"
    networks:
      - spark_network

  spark-worker-2:
    image: bde2020/spark-worker:3.0.0-hadoop3.2
    container_name: spark-worker-2
    depends_on:
      - spark-master
    ports:
      - "8082:8081"
    environment:
      - "SPARK_MASTER=spark://spark-master:7077"
    networks:
      - spark_network

networks:
  spark_network:
    driver: bridge
"""
    
    def get_basic_hdfs_template(self):
        """Get basic HDFS template"""
        return """version: '3'

services:
  namenode:
    image: bde2020/hadoop-namenode:2.0.0-hadoop3.2.1-java8
    container_name: namenode
    ports:
      - "9870:9870"
      - "8020:8020"
    volumes:
      - hadoop_namenode:/hadoop/dfs/name
    environment:
      - CLUSTER_NAME=hadoop-cluster
      - CORE_CONF_fs_defaultFS=hdfs://namenode:8020
    networks:
      - hadoop_network

  datanode:
    image: bde2020/hadoop-datanode:2.0.0-hadoop3.2.1-java8
    container_name: datanode
    volumes:
      - hadoop_datanode:/hadoop/dfs/data
    environment:
      - SERVICE_PRECONDITION=namenode:9870
      - CORE_CONF_fs_defaultFS=hdfs://namenode:8020
    networks:
      - hadoop_network

volumes:
  hadoop_namenode:
  hadoop_datanode:

networks:
  hadoop_network:
    driver: bridge
"""
    
    def get_empty_template(self):
        """Get empty template"""
        return """version: '3'

services:
  # Add your services here
  
volumes:
  # Add your volumes here

networks:
  # Add your networks here
"""
    
    def start_progress(self):
        """Start progress bar animation"""
        self.progress.start(10)
        self.is_running = True
        self.stop_btn['state'] = tk.NORMAL
        # Disable action buttons
        for btn in [self.gen_btn, self.step1_btn, self.step2_btn, self.step3_btn, self.auto_btn]:
            btn['state'] = tk.DISABLED
    
    def stop_progress(self):
        """Stop progress bar animation"""
        self.progress.stop()
        self.is_running = False
        self.stop_btn['state'] = tk.DISABLED
        # Enable action buttons
        for btn in [self.gen_btn, self.step1_btn, self.step2_btn, self.step3_btn, self.auto_btn]:
            btn['state'] = tk.NORMAL
    
    def show_help(self):
        """Show help dialog"""
        help_text = """
🚀 SPARK RUNNER GUI - HƯỚỚNG DẪN SỬ DỤNG

📁 CHỌN FILE:
  • Nhấn "Browse" hoặc Ctrl+O
  • Kéo thả file .py vào cửa sổ
  • Chọn từ lịch sử dropdown

⚙️ CẤU HÌNH:
  • Container: Tên Docker container
  • Spark Master: URL của master node
  • Nhấn "Lưu" để lưu cấu hình

🎮 CHẠY:
  • F5: Generate lệnh
  • Ctrl+R: Auto run (khuyến nghị)
  • 1-2-3: Chạy từng bước

📊 LOG:
  • Click phải: Context menu
  • Ctrl+L: Clear log
  • Ctrl+S: Export log

⌨️ SHORTCUTS:
  • Ctrl+O: Mở file
  • Ctrl+R: Chạy tự động
  • F5: Generate
  • F1: Trợ giúp
  • Esc: Dừng

💡 TIPS:
  • Drag & drop file để mở nhanh
  • Right-click để xem menu
  • Hover chuột lên nút để xem tooltip
        """
        
        dialog = tk.Toplevel(self.root)
        dialog.title('Hướng dẫn sử dụng')
        dialog.geometry('500x600')
        dialog.transient(self.root)
        
        text = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, font=('Consolas', 10), padx=10, pady=10)
        text.pack(fill=tk.BOTH, expand=True)
        text.insert('1.0', help_text)
        text.config(state=tk.DISABLED)
        
        ttk.Button(dialog, text='Đóng', command=dialog.destroy).pack(pady=10)
    
    def show_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts = """
⌨️ KEYBOARD SHORTCUTS

FILE:
  Ctrl+O         Mở file browser
  Ctrl+S         Export log

EDIT:
  Ctrl+C         Copy commands
  Ctrl+L         Clear log

RUN:
  F5             Generate commands
  Ctrl+R         Auto run all
  Esc            Stop running

GENERAL:
  F1             Help
  Alt+F4         Exit
        """
        tk.messagebox.showinfo('Keyboard Shortcuts', shortcuts)
    
    def show_about(self):
        """Show about dialog"""
        about_text = f"""
🚀 Spark Runner GUI
Version: {self.callbacks['get_version']()}

Công cụ quản lý và chạy Spark jobs trên Docker

Tính năng:
  ✅ Drag & Drop files
  ✅ File history
  ✅ Step-by-step execution
  ✅ Auto run mode
  ✅ Colored logging
  ✅ Keyboard shortcuts
  ✅ Context menus
  ✅ Export logs

Phát triển: GitHub Copilot
Năm: 2025
License: MIT
        """
        tk.messagebox.showinfo('About', about_text)
    
    # ========== NEW UTILITY FUNCTIONS ==========
    
    def docker_build(self):
        """Build Docker images from compose file"""
        self.append_log('🔨 Đang build Docker images...', 'info')
        self.callbacks['update_status']('🔨 Building images...')
        
        def run_build():
            try:
                compose_file = self.compose_file_var.get()
                result = subprocess.run(
                    ['docker-compose', '-f', compose_file, 'build'],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=600  # 10 minutes
                )
                
                if result.returncode == 0:
                    self.append_log('✅ Docker images đã được build thành công!', 'success')
                    self.append_log(result.stdout, 'info')
                    self.callbacks['update_status']('✅ Build completed')
                else:
                    self.append_log('❌ Lỗi khi build images:', 'error')
                    self.append_log(result.stderr, 'error')
                    self.callbacks['update_status']('❌ Build failed')
                    
            except subprocess.TimeoutExpired:
                self.append_log('❌ Timeout: Build quá 10 phút', 'error')
                self.callbacks['update_status']('❌ Build timeout')
            except Exception as e:
                self.append_log(f'❌ Lỗi: {e}', 'error')
                self.callbacks['update_status']('❌ Build error')
        
        threading.Thread(target=run_build, daemon=True).start()
    
    def docker_clean(self):
        """Clean Docker resources"""
        msg = """Dọn dẹp Docker resources:
        
• Dừng tất cả containers
• Xóa containers đã dừng
• Xóa images không dùng
• Xóa volumes không dùng
• Xóa networks không dùng

Tiếp tục?"""
        
        if not tk.messagebox.askyesno('⚠️ Xác nhận', msg):
            return
        
        self.append_log('🗑 Đang dọn dẹp Docker resources...', 'info')
        self.callbacks['update_status']('🗑 Cleaning...')
        
        def run_clean():
            try:
                # Stop all containers
                self.append_log('→ Dừng containers...', 'info')
                subprocess.run(['docker', 'stop', '$(docker', 'ps', '-q)'], 
                             capture_output=True, shell=True)
                
                # Prune system
                self.append_log('→ Xóa resources không dùng...', 'info')
                result = subprocess.run(
                    ['docker', 'system', 'prune', '-af', '--volumes'],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=120
                )
                
                if result.returncode == 0:
                    self.append_log('✅ Đã dọn dẹp xong!', 'success')
                    self.append_log(result.stdout, 'info')
                    self.callbacks['update_status']('✅ Cleaned')
                else:
                    self.append_log('❌ Lỗi khi dọn dẹp:', 'error')
                    self.append_log(result.stderr, 'error')
                    
            except Exception as e:
                self.append_log(f'❌ Lỗi: {e}', 'error')
        
        threading.Thread(target=run_clean, daemon=True).start()
    
    def force_kill(self):
        """Force kill all Spark processes"""
        if not tk.messagebox.askyesno('⚠️ Cảnh báo', 
                                  'Force kill tất cả Spark processes trong container?\n\nHành động này không thể hoàn tác!'):
            return
        
        self.append_log('🔴 Force killing Spark processes...', 'warning')
        self.callbacks['update_status']('🔴 Force killing...')
        
        def run_kill():
            try:
                container = self.container_var.get()
                
                # Kill all java processes (Spark)
                result = subprocess.run(
                    ['docker', 'exec', container, 'pkill', '-9', 'java'],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
                
                self.append_log('✅ Đã kill tất cả Spark processes', 'success')
                self.callbacks['update_status']('✅ Processes killed')
                
            except Exception as e:
                self.append_log(f'❌ Lỗi: {e}', 'error')
                self.callbacks['update_status']('❌ Kill failed')
        
        threading.Thread(target=run_kill, daemon=True).start()
    
    def open_spark_ui(self):
        """Open Spark UI in browser"""
        spark_ui_url = 'http://localhost:8081'
        self.append_log(f'🌐 Đang mở Spark UI: {spark_ui_url}', 'info')
        
        try:
            import webbrowser
            webbrowser.open(spark_ui_url)
            self.callbacks['update_status']('🌐 Opened Spark UI')
        except Exception as e:
            self.append_log(f'❌ Không thể mở browser: {e}', 'error')
            tk.messagebox.showerror('Error', f'Không thể mở browser.\n\nVui lòng mở thủ công: {spark_ui_url}')
    
    def open_hadoop_ui(self):
        """Open Hadoop HDFS NameNode UI in browser"""
        hadoop_ui_url = 'http://localhost:9870'
        self.append_log(f'�️ Đang mở Hadoop UI: {hadoop_ui_url}', 'info')
        
        try:
            import webbrowser
            webbrowser.open(hadoop_ui_url)
            self.callbacks['update_status']('�️ Opened Hadoop UI')
        except Exception as e:
            self.append_log(f'❌ Không thể mở browser: {e}', 'error')
            tk.messagebox.showerror('Error', f'Không thể mở browser.\n\nVui lòng mở thủ công: {hadoop_ui_url}')

