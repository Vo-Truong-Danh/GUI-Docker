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
        
        self.create_ui()

    def create_ui(self):
        # === File Selection Frame ===
        file_frame = ttk.LabelFrame(self.frame, text='📁 File Selection', padding=10)
        file_frame.pack(fill=tk.X, pady=(0, 8))
        
        file_input_frame = ttk.Frame(file_frame)
        file_input_frame.pack(fill=tk.X)
        
        ttk.Label(file_input_frame, text='File Python:', font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT)
        self.file_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_input_frame, textvariable=self.file_var, width=50, 
                                     font=('Consolas', 9))
        self.file_entry.pack(side=tk.LEFT, padx=(8, 8), fill=tk.X, expand=True)
        
        self.file_entry.bind('<Button-3>', lambda e: self.callbacks['show_file_context_menu'](e))
        
        browse_btn = ttk.Button(file_input_frame, text='📂 Browse...', command=self.on_browse)
        browse_btn.pack(side=tk.LEFT, padx=(0, 4))
        create_tooltip(browse_btn, "Ctrl+O: Mở file browser để chọn file Python")
        
        clear_btn = ttk.Button(file_input_frame, text='✖', command=self.clear_file, width=3)
        clear_btn.pack(side=tk.LEFT)
        create_tooltip(clear_btn, "Xóa file hiện tại")
        
        drop_lbl = ttk.Label(file_frame, text='💡 Tip: Bạn có thể paste đường dẫn trực tiếp hoặc dùng Browse', 
                            foreground='#666', font=('Segoe UI', 8, 'italic'))
        drop_lbl.pack(pady=(4, 0))
        
        history_frame = ttk.Frame(file_frame)
        history_frame.pack(fill=tk.X, pady=(8, 0))
        
        ttk.Label(history_frame, text='📜 Lịch sử:', font=('Segoe UI', 9)).pack(side=tk.LEFT)
        self.history_combo = ttk.Combobox(history_frame, values=self.config.get('history', []), 
                                          state='readonly', width=60, font=('Consolas', 9))
        self.history_combo.pack(side=tk.LEFT, padx=(8, 8), fill=tk.X, expand=True)
        self.history_combo.bind('<<ComboboxSelected>>', self.on_history_selected)
        create_tooltip(self.history_combo, "10 file gần nhất bạn đã chạy")
        
        if self.config.get('history'):
            self.history_combo.current(0)
        
        clear_history_btn = ttk.Button(history_frame, text='🗑️ Xóa lịch sử', 
                                       command=self.clear_history, width=12)
        clear_history_btn.pack(side=tk.LEFT)
        create_tooltip(clear_history_btn, "Xóa toàn bộ lịch sử file")
        
        # === Docker Control Frame ===
        docker_frame = ttk.LabelFrame(self.frame, text='🐳 Docker Control', padding=10)
        docker_frame.pack(fill=tk.X, pady=(0, 8))
        
        docker_btn_frame = ttk.Frame(docker_frame)
        docker_btn_frame.pack()
        
        self.docker_start_btn = ttk.Button(docker_btn_frame, text='▶️ Start Containers', 
                                           command=self.docker_start, width=20,
                                           style='Success.TButton')
        self.docker_start_btn.pack(side=tk.LEFT, padx=5)
        create_tooltip(self.docker_start_btn, "Khởi động Docker containers\n(docker-compose up -d)")
        
        self.docker_stop_btn = ttk.Button(docker_btn_frame, text='⏹️ Stop Containers', 
                                          command=self.docker_stop, width=20)
        self.docker_stop_btn.pack(side=tk.LEFT, padx=5)
        create_tooltip(self.docker_stop_btn, "Dừng Docker containers\n(docker-compose down)")
        
        self.docker_restart_btn = ttk.Button(docker_btn_frame, text='🔄 Restart Containers', 
                                             command=self.docker_restart, width=20)
        self.docker_restart_btn.pack(side=tk.LEFT, padx=5)
        create_tooltip(self.docker_restart_btn, "Khởi động lại containers\n(docker-compose restart)")
        
        self.docker_status_btn = ttk.Button(docker_btn_frame, text='📊 Status', 
                                            command=self.docker_status, width=15)
        self.docker_status_btn.pack(side=tk.LEFT, padx=5)
        create_tooltip(self.docker_status_btn, "Kiểm tra trạng thái containers\n(docker-compose ps)")
        
        docker_file_frame = ttk.Frame(docker_frame)
        docker_file_frame.pack(pady=(10, 5), fill=tk.X)
        
        ttk.Label(docker_file_frame, text='📄 docker-compose.yml:', 
                 font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        self.compose_file_var = tk.StringVar(value='docker-compose.yml')
        compose_entry = ttk.Entry(docker_file_frame, textvariable=self.compose_file_var, 
                                 width=40, font=('Courier New', 9))
        compose_entry.pack(side=tk.LEFT, padx=(0, 5))
        create_tooltip(compose_entry, "Đường dẫn đến file docker-compose.yml")
        
        browse_compose_btn = ttk.Button(docker_file_frame, text='📂 Browse', 
                                       command=self.browse_compose_file, width=10)
        browse_compose_btn.pack(side=tk.LEFT, padx=(0, 5))
        create_tooltip(browse_compose_btn, "Chọn file docker-compose.yml")
        
        edit_compose_btn = ttk.Button(docker_file_frame, text='✏️ Edit', 
                                     command=self.edit_compose_file, width=10)
        edit_compose_btn.pack(side=tk.LEFT, padx=(0, 5))
        create_tooltip(edit_compose_btn, "Mở editor để chỉnh sửa file")
        
        create_compose_btn = ttk.Button(docker_file_frame, text='➕ Create', 
                                       command=self.create_compose_file, width=10)
        create_compose_btn.pack(side=tk.LEFT)
        create_tooltip(create_compose_btn, "Tạo file docker-compose.yml mới từ template")
        
        self.docker_status_label = ttk.Label(docker_frame, text='Docker status: Unknown', 
                                             font=('Segoe UI', 9), foreground='#666')
        self.docker_status_label.pack(pady=(5, 0))
        
        # === Configuration Frame ===
        config_frame = ttk.LabelFrame(self.frame, text='⚙️ Configuration', padding=10)
        config_frame.pack(fill=tk.X, pady=(0, 8))
        
        config_grid = ttk.Frame(config_frame)
        config_grid.pack(fill=tk.X)
        
        ttk.Label(config_grid, text='Container:', font=('Segoe UI', 9)).grid(row=0, column=0, sticky=tk.W, padx=(0, 8))
        self.container_var = tk.StringVar(value=self.config['container'])
        container_entry = ttk.Entry(config_grid, textvariable=self.container_var, width=25, 
                                    font=('Consolas', 9))
        container_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        create_tooltip(container_entry, "Tên Docker container chứa Spark")
        
        ttk.Label(config_grid, text='Spark Master:', font=('Segoe UI', 9)).grid(row=0, column=2, sticky=tk.W, padx=(0, 8))
        self.master_var = tk.StringVar(value=self.config['master'])
        master_entry = ttk.Entry(config_grid, textvariable=self.master_var, width=35, 
                                font=('Consolas', 9))
        master_entry.grid(row=0, column=3, sticky=tk.W)
        create_tooltip(master_entry, "URL của Spark master node")
        
        save_config_btn = ttk.Button(config_grid, text='💾 Lưu', command=self.on_save_config, width=10)
        save_config_btn.grid(row=0, column=4, padx=(10, 0))
        create_tooltip(save_config_btn, "Lưu cấu hình này làm mặc định")
        
        reset_config_btn = ttk.Button(config_grid, text='↺ Reset', command=self.reset_config, width=8)
        reset_config_btn.grid(row=0, column=5, padx=(5, 0))
        create_tooltip(reset_config_btn, "Khôi phục cấu hình mặc định")
        
        # === Action Buttons Frame ===
        action_frame = ttk.LabelFrame(self.frame, text='🎮 Actions', padding=10)
        action_frame.pack(fill=tk.X, pady=(0, 8))
        
        btn_frame = ttk.Frame(action_frame)
        btn_frame.pack()
        
        row1 = ttk.Frame(btn_frame)
        row1.pack(pady=(0, 5))
        
        self.gen_btn = ttk.Button(row1, text='📝 Generate (F5)', command=self.on_generate, 
                                  width=18, style='Action.TButton')
        self.gen_btn.pack(side=tk.LEFT, padx=3)
        create_tooltip(self.gen_btn, "F5: Tạo các lệnh Docker/Spark từ file đã chọn")
        
        self.copy_btn = ttk.Button(row1, text='📋 Copy', command=self.on_copy, width=12)
        self.copy_btn.pack(side=tk.LEFT, padx=3)
        create_tooltip(self.copy_btn, "Ctrl+C: Copy các lệnh vào clipboard")
        
        ttk.Separator(row1, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)
        
        self.step1_btn = ttk.Button(row1, text='1️⃣ Copy File', command=self.on_step1, width=15)
        self.step1_btn.pack(side=tk.LEFT, padx=3)
        create_tooltip(self.step1_btn, "Chỉ copy file Python vào container\n(docker cp)")
        
        self.step2_btn = ttk.Button(row1, text='2️⃣ Open Bash', command=self.on_step2, width=15)
        self.step2_btn.pack(side=tk.LEFT, padx=3)
        create_tooltip(self.step2_btn, "Mở terminal tương tác trong container\n(docker exec -it bash)")
        
        self.step3_btn = ttk.Button(row1, text='3️⃣ Run Spark', command=self.on_step3, width=15)
        self.step3_btn.pack(side=tk.LEFT, padx=3)
        create_tooltip(self.step3_btn, "Chỉ chạy spark-submit\n(Cần đã copy file trước)")
        
        row2 = ttk.Frame(btn_frame)
        row2.pack()
        
        self.auto_btn = ttk.Button(row2, text='▶️ Auto Run All (Ctrl+R)', 
                                   command=self.on_auto_run, width=25, 
                                   style='Success.TButton')
        self.auto_btn.pack(side=tk.LEFT, padx=3)
        create_tooltip(self.auto_btn, "Ctrl+R: Tự động chạy copy + spark-submit\n(Khuyến nghị)")
        
        self.stop_btn = ttk.Button(row2, text='⏹️ Stop', command=self.on_stop, 
                                   width=12, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=3)
        create_tooltip(self.stop_btn, "Dừng job đang chạy (nếu có thể)")
        
        ttk.Separator(row2, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)
        
        self.clear_log_btn = ttk.Button(row2, text='🗑️ Clear Log', command=self.clear_log, width=12)
        self.clear_log_btn.pack(side=tk.LEFT, padx=3)
        create_tooltip(self.clear_log_btn, "Xóa toàn bộ log hiển thị")
        
        self.export_log_btn = ttk.Button(row2, text='💾 Export Log', command=self.export_log, width=12)
        self.export_log_btn.pack(side=tk.LEFT, padx=3)
        create_tooltip(self.export_log_btn, "Lưu log ra file .txt")
        
        self.progress = ttk.Progressbar(action_frame, mode='indeterminate', length=300)
        self.progress.pack(pady=(8, 0))
        
        # === Split View: Commands (Left) and Log (Right) ===
        split_frame = ttk.Frame(self.frame)
        split_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 0))
        
        cmd_frame = ttk.LabelFrame(split_frame, text='📜 Generated Commands', padding=5)
        cmd_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 4))
        
        self.cmd_text = scrolledtext.ScrolledText(cmd_frame, height=20, wrap=tk.WORD, 
                                                  bg=self.theme['bg_cmd'], 
                                                  font=('Courier New', 9))
        self.cmd_text.pack(fill=tk.BOTH, expand=True)
        self.cmd_text.bind('<Button-3>', lambda e: self.callbacks['show_cmd_context_menu'](e))
        
        log_frame = ttk.LabelFrame(split_frame, text='📊 Execution Log', padding=5)
        log_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(4, 0))
        
        self.log_text_widget = scrolledtext.ScrolledText(log_frame, height=20, wrap=tk.WORD, 
                                                  bg=self.theme['bg_log'], 
                                                  font=('Courier New', 9))
        self.log_text_widget.pack(fill=tk.BOTH, expand=True)
        self.log_text_widget.bind('<Button-3>', lambda e: self.callbacks['show_log_context_menu'](e))
        
        self.log_text_widget.tag_config('success', foreground=self.theme['success'], font=('Courier New', 9, 'bold'))
        self.log_text_widget.tag_config('error', foreground=self.theme['error'], font=('Courier New', 9, 'bold'))
        self.log_text_widget.tag_config('warning', foreground=self.theme['warning'], font=('Courier New', 9, 'bold'))
        self.log_text_widget.tag_config('info', foreground=self.theme['info'], font=('Courier New', 9, 'bold'))
        self.log_text_widget.tag_config('header', foreground=self.theme['primary'], font=('Courier New', 10, 'bold'))

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

    def append_log(self, s: str, tag='normal'):
        """Append message to log with color tag"""
        self.callbacks['append_log'](s, tag, self.log_text_widget)

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
        
        thread = threading.Thread(target=self._run_step1, args=(filepath, filename))
        thread.daemon = True
        thread.start()

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
            
            p = subprocess.run(cmd, capture_output=True, text=True)
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
        
        thread = threading.Thread(target=self._run_step3, args=(filename,))
        thread.daemon = True
        thread.start()

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
            
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5 min timeout
            
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
        
        thread = threading.Thread(target=self._run_auto, args=(filepath, filename))
        thread.daemon = True
        thread.start()

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
            
            p1 = subprocess.run(cmd1, capture_output=True, text=True)
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
            
            p2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=300)
            
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
                
                # Success notification
                if tk.messagebox.askyesno('🎉 Thành công', 
                                      'Spark job đã chạy thành công!\nBạn có muốn xem log chi tiết không?'):
                    pass  # Log already visible
        
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
        menu.add_command(label='📋 Copy Selection', command=lambda: self.root.clipboard_append(log_widget.selection_get()))
        menu.add_command(label='🔍 Select All', command=lambda: log_widget.tag_add('sel', '1.0', 'end'))
        menu.add_separator()
        menu.add_command(label='🗑️ Clear Log', command=self.clear_log)
        menu.add_command(label='💾 Export Log...', command=self.export_log)
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
                
                # Run docker-compose up -d
                result = subprocess.run(
                    ['docker-compose', '-f', compose_file, 'up', '-d'],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode == 0:
                    self.append_log('✅ Docker containers đã được khởi động!', 'success')
                    self.append_log(result.stdout, 'info')
                    self.callbacks['update_status']('✅ Containers started')
                    self.docker_status_label.config(text='Docker status: Running ✅', foreground='#28a745')
                else:
                    self.append_log('❌ Lỗi khi khởi động containers:', 'error')
                    self.append_log(result.stderr, 'error')
                    self.callbacks['update_status']('❌ Failed to start')
                    
            except FileNotFoundError:
                self.append_log('❌ docker-compose không được cài đặt!', 'error')
                self.append_log('💡 Cài đặt Docker Desktop: https://www.docker.com/products/docker-desktop', 'info')
                self.callbacks['update_status']('❌ docker-compose not found')
            except subprocess.TimeoutExpired:
                self.append_log('❌ Timeout: Khởi động containers quá lâu (>2 phút)', 'error')
                self.callbacks['update_status']('❌ Timeout')
            except Exception as e:
                self.append_log(f'❌ Lỗi: {e}', 'error')
                self.callbacks['update_status']('❌ Error')
        
        # Run in background thread
        threading.Thread(target=run_docker_start, daemon=True).start()
    
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
                        
                except FileNotFoundError:
                    self.append_log('❌ docker-compose không được cài đặt!', 'error')
                    self.callbacks['update_status']('❌ docker-compose not found')
                except subprocess.TimeoutExpired:
                    self.append_log('❌ Timeout: Dừng containers quá lâu (>1 phút)', 'error')
                    self.callbacks['update_status']('❌ Timeout')
                except Exception as e:
                    self.append_log(f'❌ Lỗi: {e}', 'error')
                    self.callbacks['update_status']('❌ Error')
            
            threading.Thread(target=run_docker_stop, daemon=True).start()
    
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
                    
            except FileNotFoundError:
                self.append_log('❌ docker-compose không được cài đặt!', 'error')
                self.callbacks['update_status']('❌ docker-compose not found')
            except subprocess.TimeoutExpired:
                self.append_log('❌ Timeout: Restart containers quá lâu (>90s)', 'error')
                self.callbacks['update_status']('❌ Timeout')
            except Exception as e:
                self.append_log(f'❌ Lỗi: {e}', 'error')
                self.callbacks['update_status']('❌ Error')
        
        threading.Thread(target=run_docker_restart, daemon=True).start()
    
    def docker_status(self):
        """Check Docker containers status"""
        self.append_log('🐳 Đang kiểm tra trạng thái containers...', 'info')
        self.callbacks['update_status']('🐳 Checking status...')
        
        def run_docker_status():
            try:
                # docker-compose ps
                compose_file = self.compose_file_var.get()
                result = subprocess.run(
                    ['docker-compose', '-f', compose_file, 'ps'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    self.append_log('📊 Trạng thái containers:', 'info')
                    self.append_log(result.stdout, 'info')
                    
                    # Check if any containers are running
                    if 'Up' in result.stdout:
                        self.docker_status_label.config(text='Docker status: Running ✅', foreground='#28a745')
                        self.callbacks['update_status']('✅ Containers running')
                    else:
                        self.docker_status_label.config(text='Docker status: Stopped ⏹️', foreground='#dc3545')
                        self.callbacks['update_status']('⚠️ No containers running')
                else:
                    self.append_log('❌ Không thể kiểm tra trạng thái', 'error')
                    self.append_log(result.stderr, 'error')
                    self.docker_status_label.config(text='Docker status: Error ❌', foreground='#dc3545')
                    self.callbacks['update_status']('❌ Status check failed')
                    
            except FileNotFoundError:
                self.append_log('❌ docker-compose không được cài đặt!', 'error')
                self.docker_status_label.config(text='Docker status: Not installed ❌', foreground='#dc3545')
                self.callbacks['update_status']('❌ docker-compose not found')
            except subprocess.TimeoutExpired:
                self.append_log('❌ Timeout khi kiểm tra status', 'error')
                self.callbacks['update_status']('❌ Timeout')
            except Exception as e:
                self.append_log(f'❌ Lỗi: {e}', 'error')
                self.callbacks['update_status']('❌ Error')
        
        threading.Thread(target=run_docker_status, daemon=True).start()
    
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
