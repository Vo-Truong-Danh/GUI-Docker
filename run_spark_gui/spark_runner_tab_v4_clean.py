"""
Spark Runner Tab V4 - Clean Professional Design
Modern, minimal, elegant - inspired by VS Code, GitHub, Notion
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import queue
import subprocess
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import webbrowser
import os
from pathlib import Path

# Import backend logic
from spark_backend import (
    generate_commands,
    copy_file_to_container,
    submit_spark_job,
    auto_run_spark_job,
    docker_compose_command,
    get_container_status,
    get_docker_compose_status,
    force_kill_spark_jobs
)


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
        
        # Custom Command section
        tk.Label(sc, text='Custom Args:', font=('Segoe UI', 9),
                bg='#FFFFFF', fg='#57606A').pack(anchor='w', pady=(8, 4))
        
        custom_cmd_frame = tk.Frame(sc, bg='#FFFFFF')
        custom_cmd_frame.pack(fill=tk.X, pady=(0, 6))
        
        self.custom_args_var = tk.StringVar(value='--skip_training --skip_evaluation')
        custom_args_entry = tk.Entry(
            custom_cmd_frame,
            textvariable=self.custom_args_var,
            font=('Consolas', 8),
            bg='#F6F8FA',
            fg='#24292F',
            relief=tk.SOLID,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground='#D0D7DE',
            highlightcolor='#0969DA'
        )
        custom_args_entry.pack(fill=tk.X, ipady=4)
        
        # Custom run button
        custom_run_row = tk.Frame(sc, bg='#FFFFFF')
        custom_run_row.pack(fill=tk.X, pady=(0, 6))
        
        self.custom_run_btn = CleanButton(custom_run_row, '🎯 Run Custom', 'primary',
                                         self.on_custom_run, 1)
        self.custom_run_btn.pack(fill=tk.X)
        
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
        
        # Container name (with dropdown and refresh)
        tk.Label(cc, text='Container:', font=('Segoe UI', 9),
                bg='#FFFFFF', fg='#57606A').pack(anchor='w', pady=(0, 4))

        container_row = tk.Frame(cc, bg='#FFFFFF')
        container_row.pack(fill=tk.X, pady=(0, 8))

        self.container_var = tk.StringVar(value=self.config['container'])
        self.container_combo = ttk.Combobox(container_row, textvariable=self.container_var, font=('Segoe UI', 9), state='readonly')
        self.container_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        def refresh_containers():
            import subprocess
            try:
                result = subprocess.check_output(
                    'docker ps --filter "name=spark-worker" --format "{{.Names}}"', shell=True, text=True
                )
                containers = [c for c in result.strip().splitlines() if c]
                if containers:
                    self.container_combo['values'] = containers
                    # Nếu container_var không nằm trong list thì chọn cái đầu tiên
                    if self.container_var.get() not in containers:
                        self.container_var.set(containers[0])
                else:
                    self.container_combo['values'] = ['(No spark-worker running)']
                    self.container_var.set('')
            except Exception as e:
                self.container_combo['values'] = ['(Error listing containers)']
                self.container_var.set('')

        refresh_btn = CleanButton(container_row, 'Refresh', 'outline', refresh_containers, 1)
        refresh_btn.pack(side=tk.LEFT, padx=(6,0))

        # Tự động refresh khi mở tab
        refresh_containers()
        
        # Spark master (compact)
        tk.Label(cc, text='Master:', font=('Segoe UI', 9),
                bg='#FFFFFF', fg='#57606A').pack(anchor='w', pady=(0, 4))
        
        self.master_var = tk.StringVar(value=self.config['master'])
        master_entry = tk.Entry(cc, textvariable=self.master_var,
                               font=('Segoe UI', 9), bg='#FFFFFF',
                               relief=tk.SOLID, borderwidth=1,
                               highlightthickness=1, highlightbackground='#D0D7DE')
        master_entry.pack(fill=tk.X, ipady=4, pady=(0, 8))
        
        # Docker Compose file path
        tk.Label(cc, text='Docker Compose:', font=('Segoe UI', 9),
                bg='#FFFFFF', fg='#57606A').pack(anchor='w', pady=(0, 4))
        
        compose_frame = tk.Frame(cc, bg='#FFFFFF')
        compose_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.compose_var = tk.StringVar(value=self.config.get('compose_file', 'docker-compose.yml'))
        compose_entry = tk.Entry(
            compose_frame, textvariable=self.compose_var,
            font=('Segoe UI', 8), bg='#FFFFFF',
            relief=tk.SOLID, borderwidth=1,
            highlightthickness=1, highlightbackground='#D0D7DE'
        )
        compose_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)
        
        # Browse button for compose file
        browse_compose_btn = tk.Button(
            compose_frame, text='📂',
            font=('Segoe UI', 8), bg='#F6F8FA', fg='#24292F',
            relief=tk.FLAT, cursor='hand2',
            padx=6, pady=2,
            command=self.browse_compose_file
        )
        browse_compose_btn.pack(side=tk.LEFT, padx=(4, 0))
        
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
        """Queue log message - only write to local log, no callback to avoid duplicates"""
        self.log_queue.put((message, tag))
    
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
        """Generate Spark commands"""
        filepath = self.file_var.get().strip()
        if not filepath:
            messagebox.showwarning('No File Selected', 
                                 'Please select a Python file first.')
            return
        
        container = self.container_var.get()
        master = self.master_var.get()
        
        # Generate commands using backend
        commands = generate_commands(filepath, container, master)
        self.cmd_text.delete('1.0', tk.END)
        self.cmd_text.insert(tk.END, commands)
        
        self.append_log(f'📝 Generated commands for: {Path(filepath).name}', 'success')
        if 'update_status' in self.callbacks:
            self.callbacks['update_status']('📝 Commands generated')
    
    def on_auto_run(self):
        """Auto run Spark job"""
        filepath = self.file_var.get().strip()
        if not filepath:
            messagebox.showwarning('No File Selected',
                                 'Please select a Python file first.')
            return
        
        if not os.path.exists(filepath):
            messagebox.showerror('File Not Found',
                               f'File does not exist:\n{filepath}')
            return
        
        # Add to history
        if 'add_to_history' in self.callbacks:
            self.callbacks['add_to_history'](self.config, filepath)
            self.history_combo['values'] = self.config.get('history', [])
        
        # Run in thread
        self.is_running = True
        self.progress.start(10)
        
        def run_job():
            container = self.container_var.get()
            master = self.master_var.get()
            
            success = auto_run_spark_job(
                filepath, container, master,
                log_callback=self.append_log,
                stop_check=lambda: not self.is_running
            )
            
            self.progress.stop()
            
            if success:
                if 'update_status' in self.callbacks:
                    self.callbacks['update_status']('✅ Job completed')
            else:
                if 'update_status' in self.callbacks:
                    self.callbacks['update_status']('❌ Job failed')
        
        self.thread_pool.submit(run_job)
    
    def on_custom_run(self):
        """Run Spark job with custom arguments"""
        filepath = self.file_var.get().strip()
        if not filepath:
            messagebox.showwarning('No File Selected',
                                 'Please select a Python file first.')
            return
        
        if not os.path.exists(filepath):
            messagebox.showerror('File Not Found',
                               f'File does not exist:\n{filepath}')
            return
        
        custom_args = self.custom_args_var.get().strip()
        
        # Add to history
        if 'add_to_history' in self.callbacks:
            self.callbacks['add_to_history'](self.config, filepath)
            self.history_combo['values'] = self.config.get('history', [])
        
        # Run in thread
        self.is_running = True
        self.progress.start(10)
        
        def run_custom_job():
            container = self.container_var.get()
            master = self.master_var.get()
            filename = Path(filepath).name
            
            self.append_log('🎯 Running custom Spark job...', 'header')
            self.append_log(f'📄 File: {filename}', 'info')
            self.append_log(f'🔧 Custom args: {custom_args}', 'info')
            
            # Step 1: Copy file to container
            self.append_log('\n📦 Step 1/2: Copying file to container...', 'info')
            copy_success = copy_file_to_container(filepath, container, self.append_log)
            
            if not copy_success:
                self.append_log('❌ Failed to copy file to container', 'error')
                self.progress.stop()
                if 'update_status' in self.callbacks:
                    self.callbacks['update_status']('❌ Copy failed')
                return
            
            # Step 2: Submit with custom args
            self.append_log('\n⚡ Step 2/2: Submitting Spark job with custom arguments...', 'info')
            
            # Build custom spark-submit command
            spark_submit_cmd = f'/spark/bin/spark-submit --master {master} /tmp/{filename}'
            if custom_args:
                spark_submit_cmd += f' {custom_args}'
            
            self.append_log(f'🔧 Command: {spark_submit_cmd}', 'info')
            
            try:
                import subprocess
                
                docker_cmd = [
                    'docker', 'exec', container,
                    'bash', '-c', spark_submit_cmd
                ]
                
                process = subprocess.Popen(
                    docker_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    encoding='utf-8',
                    errors='replace',
                    bufsize=1
                )
                
                # Stream output
                for line in process.stdout:
                    if not self.is_running:
                        process.terminate()
                        self.append_log('⏹️ Job stopped by user', 'warning')
                        break
                    self.append_log(line.rstrip(), 'normal')
                
                process.wait()
                
                self.progress.stop()
                
                if process.returncode == 0:
                    self.append_log('\n✅ Custom Spark job completed successfully!', 'success')
                    if 'update_status' in self.callbacks:
                        self.callbacks['update_status']('✅ Custom job completed')
                else:
                    self.append_log(f'\n❌ Job failed with exit code {process.returncode}', 'error')
                    if 'update_status' in self.callbacks:
                        self.callbacks['update_status']('❌ Custom job failed')
                
            except Exception as e:
                self.append_log(f'\n❌ Error running custom job: {str(e)}', 'error')
                self.progress.stop()
                if 'update_status' in self.callbacks:
                    self.callbacks['update_status']('❌ Error')
        
        self.thread_pool.submit(run_custom_job)
    
    def on_step1(self):
        """Step 1: Copy file to container"""
        filepath = self.file_var.get().strip()
        if not filepath:
            messagebox.showwarning('No File', 'Please select a file first.')
            return
        
        container = self.container_var.get()
        
        def run_step1():
            copy_file_to_container(filepath, container, self.append_log)
        
        self.thread_pool.submit(run_step1)
    
    def on_step2(self):
        """Step 2: Open bash in container"""
        container = self.container_var.get()
        self.append_log(f'💡 To open bash manually, run:', 'info')
        self.append_log(f'   docker exec -it {container} bash', 'info')
        
        # Try to open in new terminal
        import subprocess
        import sys
        
        if sys.platform == 'win32':
            # Windows - open in new cmd window
            cmd = f'start cmd /k docker exec -it {container} bash'
            subprocess.Popen(cmd, shell=True)
            self.append_log('✅ Opened bash in new terminal window', 'success')
        else:
            self.append_log('⚠️ Auto-open only supported on Windows', 'warning')
    
    def on_step3(self):
        """Step 3: Submit Spark job"""
        filepath = self.file_var.get().strip()
        if not filepath:
            messagebox.showwarning('No File', 'Please select a file first.')
            return
        
        container = self.container_var.get()
        master = self.master_var.get()
        filename = Path(filepath).name
        
        def run_step3():
            self.progress.start(10)
            result = submit_spark_job(container, master, filename, self.append_log, timeout=300)
            # Handle tuple return (success, missing_module)
            if isinstance(result, tuple):
                success, missing_module = result
                if not success and missing_module:
                    self.append_log(f'💡 Tip: Vào tab Python Packages để cài "{missing_module}"', 'info')
            self.progress.stop()
        
        self.thread_pool.submit(run_step3)
    
    def on_stop(self):
        """Stop current job"""
        self.is_running = False
        self.append_log('⏹️ Stopping job...', 'warning')
        self.progress.stop()
        if 'update_status' in self.callbacks:
            self.callbacks['update_status']('⏹️ Stopped')
    
    def force_kill(self):
        """Force kill all Spark processes"""
        if not messagebox.askyesno('Confirm Force Kill',
                              'Force kill all Spark processes in container?'):
            return
        
        container = self.container_var.get()
        
        def run_kill():
            force_kill_spark_jobs(container, self.append_log)
        
        self.thread_pool.submit(run_kill)
    
    def docker_start(self):
        """Start Docker containers using docker-compose up -d (tạo mới + start)"""
        compose_file = self.config.get('compose_file')
        
        # Validate compose file exists
        if not os.path.exists(compose_file):
            self.append_log(f'❌ Docker Compose file not found: {compose_file}', 'error')
            messagebox.showerror(
                'File Not Found',
                f'Docker Compose file not found:\n{compose_file}\n\n'
                'Please check the path in Config section or\n'
                'use Browse button to select the correct file.'
            )
            return
        
        self.append_log('🐳 Starting Docker containers (docker-compose up -d)...', 'header')
        self.append_log(f'📄 Using: {os.path.basename(compose_file)}', 'info')
        self.append_log('💡 Tip: Sử dụng "up -d" để tạo mới containers, tránh mất thư viện', 'info')
        self.docker_status_badge.update_status('Starting...', 'info')
        
        def run_start():
            # Start containers without destroying volumes so installed libs/cache are preserved
            self.append_log('🚀 Creating and/or starting containers (docker-compose up -d)...', 'info')
            returncode, stdout, stderr = docker_compose_command('up', compose_file, self.append_log)
            
            if returncode == 0:
                self.append_log('✅ Docker containers started successfully', 'success')
                self.append_log('📦 All libraries preserved in fresh containers', 'success')
                self.docker_status_badge.update_status('Running', 'success')
            else:
                self.append_log(f'❌ Failed to start containers', 'error')
                if stderr:
                    self.append_log(f'Error: {stderr}', 'error')
                self.docker_status_badge.update_status('Error', 'error')
        
        self.thread_pool.submit(run_start)
    
    def docker_stop(self):
        """Stop Docker containers using docker-compose stop (preserve volumes)"""
        compose_file = self.config.get('compose_file')
        
        # Validate compose file exists
        if not os.path.exists(compose_file):
            self.append_log(f'❌ Docker Compose file not found: {compose_file}', 'error')
            messagebox.showerror(
                'File Not Found',
                f'Docker Compose file not found:\n{compose_file}\n\n'
                'Please check the path in Config section or\n'
                'use Browse button to select the correct file.'
            )
            return
        
        self.append_log('🐳 Stopping Docker containers (docker-compose stop)...', 'warning')
        self.append_log(f'📄 Using: {os.path.basename(compose_file)}', 'info')
        self.append_log('💡 Tip: Sử dụng "stop" để dừng containers và giữ volumes; dùng Clean để xóa volumes nếu cần', 'info')
        self.docker_status_badge.update_status('Stopping...', 'warning')
        
        def run_stop():
            # Stop containers but DO NOT remove volumes (preserve installed libraries and caches)
            returncode, stdout, stderr = docker_compose_command('stop', compose_file, self.append_log)

            if returncode == 0:
                self.append_log('✅ Docker containers stopped', 'success')
                self.append_log('📦 Volumes preserved (libraries/cache kept)', 'info')
                self.docker_status_badge.update_status('Stopped', 'default')
            else:
                self.append_log(f'❌ Failed to stop containers', 'error')
                if stderr:
                    self.append_log(f'Error: {stderr}', 'error')
                self.docker_status_badge.update_status('Error', 'error')
        
        self.thread_pool.submit(run_stop)
    
    def docker_restart(self):
        """Restart Docker containers using docker-compose down + up (tạo mới hoàn toàn)"""
        compose_file = self.config.get('compose_file')
        
        # Validate compose file exists
        if not os.path.exists(compose_file):
            self.append_log(f'❌ Docker Compose file not found: {compose_file}', 'error')
            messagebox.showerror(
                'File Not Found',
                f'Docker Compose file not found:\n{compose_file}\n\n'
                'Please check the path in Config section or\n'
                'use Browse button to select the correct file.'
            )
            return
        
        self.append_log('🐳 Restarting Docker containers (down + up)...', 'info')
        self.append_log(f'📄 Using: {os.path.basename(compose_file)}', 'info')
        self.append_log('💡 Tip: Down + Up để refresh hoàn toàn, giữ thư viện', 'info')
        self.docker_status_badge.update_status('Restarting...', 'info')
        
        def run_restart():
            # Bước 1: Down (xóa containers + volumes)
            self.append_log('🛑 Step 1/2: Stopping and removing containers...', 'warning')
            returncode_down, stdout_down, stderr_down = docker_compose_command('down', compose_file, self.append_log)
            
            if returncode_down != 0:
                self.append_log(f'❌ Failed to stop containers', 'error')
                if stderr_down:
                    self.append_log(f'Error: {stderr_down}', 'error')
                self.docker_status_badge.update_status('Error', 'error')
                return
            
            self.append_log('✅ Containers removed successfully', 'success')
            
            # Chờ 2 giây để Docker hoàn tất cleanup
            import time
            time.sleep(2)
            
            # Bước 2: Up (tạo mới + start)
            self.append_log('🚀 Step 2/2: Creating and starting fresh containers...', 'info')
            returncode_up, stdout_up, stderr_up = docker_compose_command('up', compose_file, self.append_log)
            
            if returncode_up == 0:
                self.append_log('✅ Docker containers restarted successfully', 'success')
                self.append_log('📦 Fresh containers with all libraries', 'success')
                self.docker_status_badge.update_status('Running', 'success')
            else:
                self.append_log(f'❌ Failed to start containers', 'error')
                if stderr_up:
                    self.append_log(f'Error: {stderr_up}', 'error')
                self.docker_status_badge.update_status('Error', 'error')
        
        self.thread_pool.submit(run_restart)
    
    def docker_status(self, silent=False):
        """Check Docker container status"""
        if not silent:
            self.append_log('🔍 Checking Docker status...', 'info')
        
        def check_status():
            container = self.container_var.get()
            status = get_container_status(container)
            
            if status == 'running':
                if not silent:
                    self.append_log(f'✅ Container "{container}" is running', 'success')
                self.docker_status_badge.update_status('Running', 'success')
            elif status == 'exited':
                if not silent:
                    self.append_log(f'⚠️ Container "{container}" has exited', 'warning')
                self.docker_status_badge.update_status('Exited', 'warning')
            elif status == 'not_found':
                if not silent:
                    self.append_log(f'❌ Container "{container}" not found', 'error')
                self.docker_status_badge.update_status('Not Found', 'error')
            else:
                if not silent:
                    self.append_log(f'⚠️ Container status: {status}', 'warning')
                self.docker_status_badge.update_status(status.capitalize(), 'warning')
        
        self.thread_pool.submit(check_status)
    
    def docker_build(self):
        """Build Docker images"""
        compose_file = self.config.get('compose_file')
        
        # Validate compose file exists
        if not os.path.exists(compose_file):
            self.append_log(f'❌ Docker Compose file not found: {compose_file}', 'error')
            messagebox.showerror(
                'File Not Found',
                f'Docker Compose file not found:\n{compose_file}\n\n'
                'Please check the path in Config section or\n'
                'use Browse button to select the correct file.'
            )
            return
        
        self.append_log('🔨 Building Docker images...', 'info')
        self.append_log(f'📄 Using: {os.path.basename(compose_file)}', 'info')
        
        def run_build():
            returncode, stdout, stderr = docker_compose_command('build', compose_file, self.append_log)
            
            if stdout:
                self.append_log(stdout.strip(), 'normal')
            
            if returncode == 0:
                self.append_log('✅ Docker images built successfully', 'success')
            else:
                self.append_log(f'❌ Build failed', 'error')
                if stderr:
                    self.append_log(f'Error: {stderr}', 'error')
        
        self.thread_pool.submit(run_build)
    
    def docker_clean(self):
        """Clean Docker resources"""
        compose_file = self.config.get('compose_file')
        
        # Validate compose file exists
        if not os.path.exists(compose_file):
            self.append_log(f'❌ Docker Compose file not found: {compose_file}', 'error')
            messagebox.showerror(
                'File Not Found',
                f'Docker Compose file not found:\n{compose_file}\n\n'
                'Please check the path in Config section or\n'
                'use Browse button to select the correct file.'
            )
            return
        
        if not messagebox.askyesno('Confirm Clean',
                              'This will stop and remove all containers and volumes.\nContinue?'):
            return
        
        self.append_log('🧹 Cleaning Docker resources...', 'warning')
        self.append_log(f'📄 Using: {os.path.basename(compose_file)}', 'info')
        
        def run_clean():
            returncode, stdout, stderr = docker_compose_command('down', compose_file, self.append_log)
            
            if returncode == 0:
                self.append_log('✅ Docker resources cleaned', 'success')
                self.docker_status_badge.update_status('Cleaned', 'default')
            else:
                self.append_log(f'❌ Clean failed', 'error')
                if stderr:
                    self.append_log(f'Error: {stderr}', 'error')
        
        self.thread_pool.submit(run_clean)
    
    def on_save_config(self):
        """Save configuration including docker-compose path"""
        self.config['container'] = self.container_var.get()
        self.config['master'] = self.master_var.get()
        self.config['compose_file'] = self.compose_var.get()
        
        if 'save_config' in self.callbacks:
            self.callbacks['save_config'](self.config)
        
        self.append_log('✅ Configuration saved successfully', 'success')
        self.append_log(f'  • Container: {self.config["container"]}', 'info')
        self.append_log(f'  • Master: {self.config["master"]}', 'info')
        self.append_log(f'  • Docker Compose: {self.config["compose_file"]}', 'info')
    
    def browse_compose_file(self):
        """Browse for docker-compose.yml file"""
        from tkinter import filedialog
        
        initial_dir = os.path.dirname(self.compose_var.get()) or os.getcwd()
        
        filepath = filedialog.askopenfilename(
            title='Select docker-compose.yml',
            initialdir=initial_dir,
            filetypes=[
                ('Docker Compose files', 'docker-compose.yml docker-compose.yaml'),
                ('YAML files', '*.yml *.yaml'),
                ('All files', '*.*')
            ]
        )
        
        if filepath:
            self.compose_var.set(filepath)
            self.config['compose_file'] = filepath
            self.append_log(f'📄 Selected Docker Compose file: {os.path.basename(filepath)}', 'success')
            
            # Validate file exists
            if os.path.exists(filepath):
                self.append_log(f'✅ File exists and is accessible', 'success')
            else:
                self.append_log(f'⚠️ Warning: File does not exist yet', 'warning')
    
    def reset_config(self):
        """Reset configuration to defaults"""
        if messagebox.askyesno('Confirm Reset',
                              'Reset all settings to default values?'):
            # Get default compose file path
            script_dir = os.path.dirname(os.path.abspath(__file__))
            default_compose = os.path.join(script_dir, 'docker-compose.yml')
            
            self.container_var.set('spark-worker')
            self.master_var.set('spark://spark-master:7077')
            self.compose_var.set(default_compose)
            
            self.append_log('↺ Configuration reset to defaults', 'info')
    
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
    
    def show_help(self):
        """Show help dialog"""
        help_text = """
        🚀 SPARK RUNNER GUI - HELP
        
        📋 QUICK START:
        1. Select a Python file (Browse or drag-drop)
        2. Click "Generate" to create Docker commands
        3. Click "Run" to execute automatically
        
        ⌨️ KEYBOARD SHORTCUTS:
        • Ctrl+O - Open file
        • Ctrl+R - Run job
        • F5 - Generate commands
        • Ctrl+S - Export log
        • Ctrl+L - Clear log
        • F1 - Show this help
        • Esc - Stop job
        
        🐳 DOCKER COMMANDS:
        • Start - Start all containers
        • Stop - Stop all containers
        • Restart - Restart containers
        • Status - Check container status
        • Build - Rebuild images
        • Clean - Remove all containers
        
        ⚡ SPARK JOB STEPS:
        1. Copy - Copy file to container
        2. Bash - Open container shell
        3. Submit - Run Spark job
        
        💡 TIPS:
        • Use "Auto Run" for one-click execution
        • Check Docker status before running
        • Export logs for debugging
        • Use Force Kill for stuck processes
        """
        messagebox.showinfo('Help - Spark Runner GUI', help_text)
    
    def show_about(self):
        """Show about dialog"""
        about_text = f"""
        Spark Runner GUI V4.1
        Clean Professional Edition
        
        A modern, elegant interface for Apache Spark
        with Docker integration.
        
        Features:
        • Automated Spark job execution
        • Docker container management
        • Real-time log streaming
        • HDFS file upload
        • AI code generation
        • Performance monitoring
        • Docker Compose editor
        
        © 2025 - Built with ❤️
        """
        messagebox.showinfo('About', about_text)
    
    def show_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts_text = """
        ⌨️ KEYBOARD SHORTCUTS
        
        FILE OPERATIONS:
        • Ctrl+O - Open file
        • Ctrl+S - Export log
        • Ctrl+L - Clear log
        
        JOB EXECUTION:
        • Ctrl+R - Auto run job
        • F5 - Generate commands
        • Esc - Stop current job
        
        HELP:
        • F1 - Show help
        
        NAVIGATION:
        • Alt+1-5 - Switch tabs
        • Ctrl+Tab - Next tab
        """
        messagebox.showinfo('Keyboard Shortcuts', shortcuts_text)
    
    def refresh_history(self):
        """Refresh file history"""
        if hasattr(self, 'history_combo'):
            self.history_combo['values'] = self.config.get('history', [])
            self.append_log('History refreshed', 'info')
    
    def clear_history(self):
        """Clear file history"""
        if messagebox.askyesno('Clear History', 'Clear all file history?'):
            self.config['history'] = []
            if hasattr(self, 'history_combo'):
                self.history_combo['values'] = []
            self.append_log('History cleared', 'info')
    
    def cleanup(self):
        self.thread_pool.shutdown(wait=False)
