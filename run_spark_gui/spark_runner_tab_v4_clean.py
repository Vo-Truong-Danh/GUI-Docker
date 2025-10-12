"""
Spark Runner Tab V4 - Clean Professional Design
Modern, minimal, elegant - inspired by VS Code, GitHub, Notion
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import webbrowser
import os


class CleanButton(tk.Frame):
    """Modern flat button with subtle hover effect"""
    
    STYLES = {
        'primary': {
            'bg': '#0969DA',
            'hover': '#0860CA', 
            'fg': '#FFFFFF',
            'border': '#0969DA'
        },
        'success': {
            'bg': '#1A7F37',
            'hover': '#1A7F37',
            'fg': '#FFFFFF',
            'border': '#1A7F37'
        },
        'danger': {
            'bg': '#CF222E',
            'hover': '#A40E26',
            'fg': '#FFFFFF',
            'border': '#CF222E'
        },
        'secondary': {
            'bg': '#F6F8FA',
            'hover': '#F3F4F6',
            'fg': '#24292F',
            'border': '#D0D7DE'
        },
        'outline': {
            'bg': '#FFFFFF',
            'hover': '#F6F8FA',
            'fg': '#24292F',
            'border': '#D0D7DE'
        }
    }
    
    def __init__(self, parent, text, style='primary', command=None, width=100):
        super().__init__(parent, bg=parent.cget('bg'))
        
        self.style_config = self.STYLES[style]
        self.command = command
        self.default_bg = self.style_config['bg']
        self.hover_bg = self.style_config['hover']
        
        # Button label
        self.label = tk.Label(
            self,
            text=text,
            bg=self.default_bg,
            fg=self.style_config['fg'],
            font=('Segoe UI', 9),
            padx=16,
            pady=6,
            cursor='hand2',
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.style_config['border'],
            highlightcolor=self.style_config['border']
        )
        self.label.pack(fill=tk.BOTH, expand=True)
        
        # Bind events
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
        
        # Title bar (compact)
        if title:
            title_frame = tk.Frame(self, bg='#F6F8FA', height=32)
            title_frame.pack(fill=tk.X, side=tk.TOP)
            title_frame.pack_propagate(False)
            
            title_label = tk.Label(
                title_frame,
                text=title,
                font=('Segoe UI', 9, 'bold'),
                bg='#F6F8FA',
                fg='#24292F',
                anchor='w'
            )
            title_label.pack(side=tk.LEFT, padx=12, pady=6)
        
        # Content area (reduced padding)
        self.content = tk.Frame(self, bg='#FFFFFF')
        self.content.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
    
    def get_content(self):
        return self.content


class StatusBadge(tk.Frame):
    """Status indicator badge"""
    
    COLORS = {
        'success': {'bg': '#DFF6DD', 'fg': '#1A7F37', 'dot': '#2DA44E'},
        'error': {'bg': '#FFEBE9', 'fg': '#CF222E', 'dot': '#CF222E'},
        'warning': {'bg': '#FFF8C5', 'fg': '#9A6700', 'dot': '#BF8700'},
        'info': {'bg': '#DDF4FF', 'fg': '#0969DA', 'dot': '#0969DA'},
        'default': {'bg': '#F6F8FA', 'fg': '#57606A', 'dot': '#8C959F'}
    }
    
    def __init__(self, parent, text="Status", status='default'):
        super().__init__(parent, bg=parent.cget('bg'))
        
        colors = self.COLORS.get(status, self.COLORS['default'])
        
        # Container
        container = tk.Frame(
            self,
            bg=colors['bg'],
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=colors['bg']
        )
        container.pack(padx=2, pady=2)
        
        # Dot
        dot = tk.Label(
            container,
            text='●',
            font=('Segoe UI', 10),
            bg=colors['bg'],
            fg=colors['dot']
        )
        dot.pack(side=tk.LEFT, padx=(8, 4), pady=6)
        
        # Text
        self.label = tk.Label(
            container,
            text=text,
            font=('Segoe UI', 9),
            bg=colors['bg'],
            fg=colors['fg']
        )
        self.label.pack(side=tk.LEFT, padx=(0, 8), pady=6)
        
        self.container = container
        self.colors_map = self.COLORS
    
    def update_status(self, text, status='default'):
        colors = self.colors_map.get(status, self.colors_map['default'])
        self.label.config(text=text, bg=colors['bg'], fg=colors['fg'])
        self.container.config(bg=colors['bg'], highlightbackground=colors['bg'])
        # Update dot color
        for child in self.container.winfo_children():
            if isinstance(child, tk.Label) and child.cget('text') == '●':
                child.config(bg=colors['bg'], fg=colors['dot'])


class SparkRunnerTabV4:
    """Clean Professional Spark Runner UI"""
    
    def __init__(self, parent_frame, config, theme, callbacks):
        self.frame = parent_frame
        self.config = config
        self.theme = theme
        self.callbacks = callbacks
        
        self.thread_pool = ThreadPoolExecutor(max_workers=3)
        self.log_queue = queue.Queue()
        self.is_running = False
        
        self.create_clean_ui()
        self._start_log_processor()
    
    def create_clean_ui(self):
        """Create clean professional UI"""
        
        # Main background - use tk.Frame instead of ttk.Frame
        # (self.frame might be ttk.Frame passed from parent)
        
        # Top action bar
        action_bar = tk.Frame(self.frame, bg='#24292F', height=48)
        action_bar.pack(fill=tk.X, side=tk.TOP)
        action_bar.pack_propagate(False)
        
        # Title
        title = tk.Label(
            action_bar,
            text='Spark Job Runner',
            font=('Segoe UI', 11, 'bold'),
            bg='#24292F',
            fg='#F0F6FC'
        )
        title.pack(side=tk.LEFT, padx=20)
        
        # Quick actions
        quick_frame = tk.Frame(action_bar, bg='#24292F')
        quick_frame.pack(side=tk.RIGHT, padx=12)
        
        self.quick_run_btn = CleanButton(quick_frame, '▶ Run', 'success', 
                                         self.on_auto_run, 90)
        self.quick_run_btn.pack(side=tk.LEFT, padx=3)
        
        self.quick_gen_btn = CleanButton(quick_frame, '⚙ Generate', 'outline',
                                         self.on_generate, 95)
        self.quick_gen_btn.pack(side=tk.LEFT, padx=3)
        
        # Main content area (reduced padding)
        content_bg = tk.Frame(self.frame, bg='#F6F8FA')
        content_bg.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        # Scrollable canvas
        canvas = tk.Canvas(content_bg, bg='#F6F8FA', highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_bg, orient='vertical', command=canvas.yview)
        
        scroll_frame = tk.Frame(canvas, bg='#F6F8FA')
        scroll_frame.bind('<Configure>', 
                         lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        
        # Create window with proper width calculation
        canvas_window = canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
        
        def on_canvas_configure(event):
            # Update scroll region
            canvas.configure(scrollregion=canvas.bbox('all'))
            # Set window width to canvas width
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind('<Configure>', on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Mouse wheel scroll - bind to multiple widgets for better UX
        def _on_wheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), 'units')
        
        # Bind to canvas and frame
        canvas.bind('<MouseWheel>', _on_wheel)
        scroll_frame.bind('<MouseWheel>', _on_wheel)
        
        # Bind enter/leave events to enable scrolling when hovering
        def _bind_to_mousewheel(event):
            canvas.bind_all('<MouseWheel>', _on_wheel)
        def _unbind_from_mousewheel(event):
            canvas.unbind_all('<MouseWheel>')
        
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        # Two column layout - Left 30%, Right 70% (even more space for logs)
        # Use Grid layout for better control
        scroll_frame.grid_columnconfigure(0, weight=10, minsize=250)
        scroll_frame.grid_columnconfigure(1, weight=90)
        scroll_frame.grid_rowconfigure(0, weight=1)
        
        left_col = tk.Frame(scroll_frame, bg='#F6F8FA')
        left_col.grid(row=0, column=0, sticky='nsew', padx=(0, 8))
        
        right_col = tk.Frame(scroll_frame, bg='#F6F8FA')
        right_col.grid(row=0, column=1, sticky='nsew', padx=(8, 0))
        
        # === FILE SELECTION CARD (COMPACT) ===
        file_card = SectionCard(left_col, '📁 Python File')
        file_card.pack(fill=tk.X, pady=(0, 10))
        fc = file_card.get_content()
        
        # File input (full width)
        tk.Label(fc, text='Path:', font=('Segoe UI', 9),
                bg='#FFFFFF', fg='#57606A').pack(anchor='w', pady=(0, 4))
        
        self.file_var = tk.StringVar()
        file_entry = tk.Entry(
            fc,
            textvariable=self.file_var,
            font=('Segoe UI', 9),
            bg='#FFFFFF',
            fg='#24292F',
            relief=tk.SOLID,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground='#D0D7DE',
            highlightcolor='#0969DA'
        )
        file_entry.pack(fill=tk.X, ipady=4, pady=(0, 6))
        
        # Buttons row (full width, equal size)
        btn_row = tk.Frame(fc, bg='#FFFFFF')
        btn_row.pack(fill=tk.X, pady=(0, 6))
        
        CleanButton(btn_row, 'Browse', 'primary', self.on_browse, 1).pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        CleanButton(btn_row, 'Clear', 'secondary', self.clear_file, 1).pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # History (compact)
        tk.Label(fc, text='Recent:', font=('Segoe UI', 8),
                bg='#FFFFFF', fg='#57606A').pack(anchor='w', pady=(0, 3))
        
        self.history_combo = ttk.Combobox(
            fc,
            values=self.config.get('history', []),
            state='readonly',
            font=('Segoe UI', 8)
        )
        self.history_combo.pack(fill=tk.X, ipady=4)
        self.history_combo.bind('<<ComboboxSelected>>', self.on_history_selected)
        
        # === DOCKER CONTROL CARD ===
        docker_card = SectionCard(left_col, '🐳 Docker Containers')
        docker_card.pack(fill=tk.X, pady=(0, 10))
        dc = docker_card.get_content()
        
        # Status badge
        status_frame = tk.Frame(dc, bg='#FFFFFF')
        status_frame.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(status_frame, text='Status:', font=('Segoe UI', 9),
                bg='#FFFFFF', fg='#57606A').pack(side=tk.LEFT, padx=(0, 8))
        
        self.docker_status_badge = StatusBadge(status_frame, 'Checking...', 'default')
        self.docker_status_badge.pack(side=tk.LEFT)
        
        # Control buttons - Full width grid (3 columns equal width)
        grid = tk.Frame(dc, bg='#FFFFFF')
        grid.pack(fill=tk.X)
        
        # Row 1
        row1 = tk.Frame(grid, bg='#FFFFFF')
        row1.pack(fill=tk.X, pady=(0, 6))
        
        self.docker_start_btn = CleanButton(row1, 'Start', 'success', 
                                           self.docker_start, 1)
        self.docker_start_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        
        self.docker_stop_btn = CleanButton(row1, 'Stop', 'danger',
                                          self.docker_stop, 1)
        self.docker_stop_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        
        self.docker_restart_btn = CleanButton(row1, 'Restart', 'primary',
                                             self.docker_restart, 1)
        self.docker_restart_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Row 2
        row2 = tk.Frame(grid, bg='#FFFFFF')
        row2.pack(fill=tk.X)
        
        self.docker_status_btn = CleanButton(row2, 'Status', 'outline',
                                            self.docker_status, 1)
        self.docker_status_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        
        CleanButton(row2, 'Build', 'secondary', self.docker_build, 1).pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        CleanButton(row2, 'Clean', 'secondary', self.docker_clean, 1).pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # === SPARK JOB CARD (ULTRA COMPACT) ===
        spark_card = SectionCard(left_col, '⚡ Spark Job')
        spark_card.pack(fill=tk.X, pady=(0, 12))
        sc = spark_card.get_content()
        
        # Main actions - Full width
        main_row = tk.Frame(sc, bg='#FFFFFF')
        main_row.pack(fill=tk.X, pady=(0, 6))
        
        self.gen_btn = CleanButton(main_row, 'Generate', 'primary',
                                   self.on_generate, 1)
        self.gen_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        
        self.auto_btn = CleanButton(main_row, 'Run', 'success',
                                    self.on_auto_run, 1)
        self.auto_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        
        self.stop_btn = CleanButton(main_row, 'Stop', 'danger',
                                    self.on_stop, 1)
        self.stop_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Manual steps - Full width
        manual_row = tk.Frame(sc, bg='#FFFFFF')
        manual_row.pack(fill=tk.X, pady=(0, 6))
        
        self.step1_btn = CleanButton(manual_row, '1.Copy', 'outline',
                                     self.on_step1, 1)
        self.step1_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        
        self.step2_btn = CleanButton(manual_row, '2.Bash', 'outline',
                                     self.on_step2, 1)
        self.step2_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        
        self.step3_btn = CleanButton(manual_row, '3.Submit', 'outline',
                                     self.on_step3, 1)
        self.step3_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Kill button - Full width
        kill_row = tk.Frame(sc, bg='#FFFFFF')
        kill_row.pack(fill=tk.X, pady=(0, 6))
        
        self.kill_btn = CleanButton(kill_row, 'Force Kill', 'secondary',
                                    self.force_kill, 1)
        self.kill_btn.pack(fill=tk.X)
        
        # Progress bar (compact)
        self.progress = ttk.Progressbar(sc, mode='indeterminate')
        self.progress.pack(fill=tk.X)
        
        # === CONFIGURATION CARD (COMPACT) ===
        config_card = SectionCard(left_col, '⚙️ Config')
        config_card.pack(fill=tk.X, pady=(0, 12))
        cc = config_card.get_content()
        
        # Container name (compact)
        tk.Label(cc, text='Container:', font=('Segoe UI', 9),
                bg='#FFFFFF', fg='#57606A').pack(anchor='w', pady=(0, 4))
        
        self.container_var = tk.StringVar(value=self.config['container'])
        cont_entry = tk.Entry(cc, textvariable=self.container_var,
                             font=('Segoe UI', 9), bg='#FFFFFF',
                             relief=tk.SOLID, borderwidth=1,
                             highlightthickness=1, highlightbackground='#D0D7DE')
        cont_entry.pack(fill=tk.X, ipady=4, pady=(0, 8))
        
        # Spark master (compact)
        tk.Label(cc, text='Master:', font=('Segoe UI', 9),
                bg='#FFFFFF', fg='#57606A').pack(anchor='w', pady=(0, 4))
        
        self.master_var = tk.StringVar(value=self.config['master'])
        master_entry = tk.Entry(cc, textvariable=self.master_var,
                               font=('Segoe UI', 9), bg='#FFFFFF',
                               relief=tk.SOLID, borderwidth=1,
                               highlightthickness=1, highlightbackground='#D0D7DE')
        master_entry.pack(fill=tk.X, ipady=4, pady=(0, 8))
        
        # Buttons - Full width
        cfg_btn_row = tk.Frame(cc, bg='#FFFFFF')
        cfg_btn_row.pack(fill=tk.X)
        
        CleanButton(cfg_btn_row, 'Save', 'primary',
                   self.on_save_config, 1).pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        CleanButton(cfg_btn_row, 'Reset', 'secondary',
                   self.reset_config, 1).pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # === UTILITIES CARD (COMPACT) ===
        utils_card = SectionCard(left_col, '🛠️ Tools')
        utils_card.pack(fill=tk.X, pady=(0, 12))
        uc = utils_card.get_content()
        
        # All buttons in 2 rows - Full width
        utils_row1 = tk.Frame(uc, bg='#FFFFFF')
        utils_row1.pack(fill=tk.X, pady=(0, 6))
        
        CleanButton(utils_row1, 'Spark UI', 'outline',
                   self.open_spark_ui, 1).pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        CleanButton(utils_row1, 'Hadoop UI', 'outline',
                   self.open_hadoop_ui, 1).pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        utils_row2 = tk.Frame(uc, bg='#FFFFFF')
        utils_row2.pack(fill=tk.X)
        
        CleanButton(utils_row2, 'Export', 'secondary',
                   self.export_log, 1).pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        CleanButton(utils_row2, 'Clear', 'secondary',
                   self.clear_log, 1).pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # === RIGHT COLUMN (WIDER FOR LOGS) ===
        
        # Commands card (reduced height for more log space)
        cmd_card = SectionCard(right_col, '📋 Generated Commands')
        cmd_card.pack(fill=tk.X, pady=(0, 16))
        cmd_content = cmd_card.get_content()
        
        self.cmd_text = scrolledtext.ScrolledText(
            cmd_content,
            height=8,  # Reduced from 12 to 8
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg='#FFFFFF',
            fg='#24292F',
            relief=tk.SOLID,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground='#D0D7DE',
            padx=8,
            pady=8
        )
        self.cmd_text.pack(fill=tk.BOTH, expand=True)
        
        # Execution log card (takes remaining space - much larger now)
        log_card = SectionCard(right_col, '📊 Execution Log')
        log_card.pack(fill=tk.BOTH, expand=True)
        log_content = log_card.get_content()
        
        self.log_text_widget = scrolledtext.ScrolledText(
            log_content,
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg='#0D1117',
            fg='#C9D1D9',
            relief=tk.SOLID,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground='#30363D',
            padx=8,
            pady=8
        )
        self.log_text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Configure log tags
        self.log_text_widget.tag_config('success', foreground='#3FB950',
                                       font=('Consolas', 9, 'bold'))
        self.log_text_widget.tag_config('error', foreground='#F85149',
                                       font=('Consolas', 9, 'bold'))
        self.log_text_widget.tag_config('warning', foreground='#D29922',
                                       font=('Consolas', 9, 'bold'))
        self.log_text_widget.tag_config('info', foreground='#58A6FF',
                                       font=('Consolas', 9, 'bold'))
        self.log_text_widget.tag_config('header', foreground='#F0F6FC',
                                       font=('Consolas', 10, 'bold'))
        
        # Force update scroll region after all widgets are created
        scroll_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox('all'))
        
        # Initial docker status check
        self.frame.after(500, lambda: self.docker_status(silent=True))
    
    def _start_log_processor(self):
        """Start log processor thread"""
        def process_logs():
            while True:
                try:
                    message, tag = self.log_queue.get(timeout=0.1)
                    self._append_to_log(message, tag)
                except queue.Empty:
                    continue
        
        threading.Thread(target=process_logs, daemon=True).start()
    
    def _append_to_log(self, message, tag='normal'):
        """Append to log widget"""
        if hasattr(self, 'log_text_widget'):
            timestamp = datetime.now().strftime('%H:%M:%S')
            self.log_text_widget.insert(tk.END, f'[{timestamp}] {message}\n', tag)
            self.log_text_widget.see(tk.END)
    
    def append_log(self, message, tag='normal'):
        """Queue log message"""
        self.log_queue.put((message, tag))
        if 'append_log' in self.callbacks:
            self.callbacks['append_log'](message, tag, self.log_text_widget)
    
    # Event handlers
    def on_browse(self):
        filepath = filedialog.askopenfilename(
            title='Select Python File',
            filetypes=[('Python files', '*.py'), ('All files', '*.*')]
        )
        if filepath:
            self.file_var.set(filepath)
            self.append_log(f'Selected file: {os.path.basename(filepath)}', 'info')
    
    def clear_file(self):
        self.file_var.set('')
        self.append_log('File selection cleared', 'info')
    
    def on_history_selected(self, event):
        selected = self.history_combo.get()
        if selected:
            self.file_var.set(selected)
            self.append_log(f'Loaded from history: {os.path.basename(selected)}', 'info')
    
    def on_generate(self):
        if not self.file_var.get():
            messagebox.showwarning('No File Selected', 
                                 'Please select a Python file first.')
            return
        self.append_log('Generating Spark commands...', 'header')
    
    def on_auto_run(self):
        if not self.file_var.get():
            messagebox.showwarning('No File Selected',
                                 'Please select a Python file first.')
            return
        self.append_log('Starting automated job execution...', 'header')
        self.progress.start(10)
    
    def on_step1(self):
        self.append_log('Step 1: Copying file to container...', 'info')
    
    def on_step2(self):
        self.append_log('Step 2: Opening bash in container...', 'info')
    
    def on_step3(self):
        self.append_log('Step 3: Submitting Spark job...', 'info')
    
    def on_stop(self):
        self.append_log('Stopping Spark job...', 'warning')
        self.progress.stop()
    
    def force_kill(self):
        if messagebox.askyesno('Confirm Force Kill',
                              'Force kill all Spark processes?'):
            self.append_log('Force killing all processes...', 'error')
    
    def docker_start(self):
        self.append_log('Starting Docker containers...', 'header')
        self.docker_status_badge.update_status('Starting...', 'info')
    
    def docker_stop(self):
        self.append_log('Stopping Docker containers...', 'warning')
        self.docker_status_badge.update_status('Stopping...', 'warning')
    
    def docker_restart(self):
        self.append_log('Restarting Docker containers...', 'info')
        self.docker_status_badge.update_status('Restarting...', 'info')
    
    def docker_status(self, silent=False):
        if not silent:
            self.append_log('Checking Docker status...', 'info')
        self.docker_status_badge.update_status('Running', 'success')
    
    def docker_build(self):
        self.append_log('Building Docker images...', 'info')
    
    def docker_clean(self):
        if messagebox.askyesno('Confirm Clean',
                              'Remove all containers and volumes?'):
            self.append_log('Cleaning Docker resources...', 'warning')
    
    def on_save_config(self):
        self.config['container'] = self.container_var.get()
        self.config['master'] = self.master_var.get()
        if 'save_config' in self.callbacks:
            self.callbacks['save_config'](self.config)
        self.append_log('Configuration saved successfully', 'success')
    
    def reset_config(self):
        if messagebox.askyesno('Confirm Reset',
                              'Reset all settings to default values?'):
            self.container_var.set('spark-worker')
            self.master_var.set('spark://spark-master:7077')
            self.append_log('Configuration reset to defaults', 'info')
    
    def open_spark_ui(self):
        webbrowser.open('http://localhost:8080')
        self.append_log('Opening Spark UI in browser...', 'info')
    
    def open_hadoop_ui(self):
        webbrowser.open('http://localhost:9870')
        self.append_log('Opening Hadoop UI in browser...', 'info')
    
    def export_log(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension='.log',
            filetypes=[('Log files', '*.log'), ('Text files', '*.txt')]
        )
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.log_text_widget.get('1.0', tk.END))
            self.append_log(f'Log exported to {os.path.basename(filepath)}', 'success')
    
    def clear_log(self):
        self.log_text_widget.delete('1.0', tk.END)
        self.append_log('Log cleared', 'info')
    
    def cleanup(self):
        self.thread_pool.shutdown(wait=False)
