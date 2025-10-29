"""
Parameter Tuning Tab - Quick retrain with different parameters
Separate tab dedicated to model parameter experimentation
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import queue
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from quick_retrain_helper import QuickRetrainHelper


class ParameterTuningTab:
    """Tab for quick model retraining with parameter tuning"""
    
    def __init__(self, parent_frame, config, theme, callbacks):
        self.frame = parent_frame
        self.config = config
        self.theme = theme
        self.callbacks = callbacks
        
        self.thread_pool = ThreadPoolExecutor(max_workers=2)
        self.log_queue = queue.Queue()
        self.is_running = False
        
        self.create_ui()
        self._start_log_processor()
    
    def create_ui(self):
        """Create the parameter tuning UI"""
        
        # Top bar
        top_bar = tk.Frame(self.frame, bg='#24292F', height=48)
        top_bar.pack(fill=tk.X)
        top_bar.pack_propagate(False)
        
        tk.Label(
            top_bar,
            text='🔥 Model Parameter Tuning',
            font=('Segoe UI', 12, 'bold'),
            bg='#24292F',
            fg='#F0F6FC'
        ).pack(side=tk.LEFT, padx=20)
        
        tk.Label(
            top_bar,
            text='Quick retrain without data reload',
            font=('Segoe UI', 9),
            bg='#24292F',
            fg='#8B949E'
        ).pack(side=tk.LEFT, padx=10)
        
        # Main content
        content = tk.Frame(self.frame, bg='#F6F8FA')
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left panel (controls) - 35%
        left_panel = tk.Frame(content, bg='#FFFFFF', relief=tk.SOLID, 
                             borderwidth=1, highlightthickness=1,
                             highlightbackground='#D0D7DE')
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10), pady=0)
        left_panel.pack_propagate(False)
        left_panel.configure(width=350)
        
        # Right panel (logs) - 60%
        right_panel = tk.Frame(content, bg='#FFFFFF', relief=tk.SOLID,
                              borderwidth=1, highlightthickness=1,
                              highlightbackground='#D0D7DE')
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=0)
        
        # === LEFT PANEL CONTENT ===
        left_scroll = tk.Canvas(left_panel, bg='#FFFFFF', highlightthickness=0)
        left_scrollbar = ttk.Scrollbar(left_panel, orient='vertical', command=left_scroll.yview)
        left_content = tk.Frame(left_scroll, bg='#FFFFFF')
        
        left_window = left_scroll.create_window((0, 0), window=left_content, anchor='nw')
        left_scroll.configure(yscrollcommand=left_scrollbar.set)
        
        def on_left_configure(e):
            left_scroll.configure(scrollregion=left_scroll.bbox('all'))
            # Make sure content fills width
            left_scroll.itemconfig(left_window, width=e.width)
        
        left_scroll.bind('<Configure>', on_left_configure)
        left_content.bind('<Configure>', lambda e: left_scroll.configure(scrollregion=left_scroll.bbox('all')))
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            left_scroll.yview_scroll(int(-1*(event.delta/120)), "units")
        
        left_scroll.bind_all("<MouseWheel>", _on_mousewheel)
        left_content.bind("<MouseWheel>", _on_mousewheel)
        
        left_scroll.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # File selection
        self._create_section(left_content, '📁 Python File')
        
        tk.Label(left_content, text='Training Script:', font=('Segoe UI', 8),
                bg='#FFFFFF', fg='#57606A').pack(anchor='w', pady=(0, 3))
        
        file_row = tk.Frame(left_content, bg='#FFFFFF')
        file_row.pack(fill=tk.X, pady=(0, 10))
        
        self.file_var = tk.StringVar()
        file_entry = tk.Entry(
            file_row,
            textvariable=self.file_var,
            font=('Segoe UI', 8),
            bg='#F6F8FA',
            relief=tk.SOLID,
            borderwidth=1
        )
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3, padx=(0, 4))
        
        tk.Button(
            file_row,
            text='Browse',
            font=('Segoe UI', 8),
            bg='#0969DA',
            fg='#FFFFFF',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.browse_file,
            padx=8,
            pady=2
        ).pack(side=tk.LEFT)
        
        # Docker config
        self._create_section(left_content, '⚙️ Configuration')
        
        tk.Label(left_content, text='Container:', font=('Segoe UI', 8),
                bg='#FFFFFF', fg='#57606A').pack(anchor='w', pady=(0, 3))
        
        self.container_var = tk.StringVar(value='gui-docker-spark-worker-1')
        container_combo = ttk.Combobox(
            left_content,
            textvariable=self.container_var,
            font=('Segoe UI', 8),
            values=['gui-docker-spark-worker-1', 'gui-docker-spark-worker-2'],
            state='readonly'
        )
        container_combo.pack(fill=tk.X, ipady=3, pady=(0, 6))
        
        tk.Label(left_content, text='Master:', font=('Segoe UI', 8),
                bg='#FFFFFF', fg='#57606A').pack(anchor='w', pady=(0, 3))
        
        self.master_var = tk.StringVar(value='spark://spark-master:7077')
        master_entry = tk.Entry(
            left_content,
            textvariable=self.master_var,
            font=('Segoe UI', 8),
            bg='#F6F8FA',
            relief=tk.SOLID,
            borderwidth=1
        )
        master_entry.pack(fill=tk.X, ipady=3, pady=(0, 10))
        
        # Preset selection
        self._create_section(left_content, '🎯 Training Preset')
        
        tk.Label(left_content, text='Chọn 1 preset hoặc dùng custom bên dưới:', 
                font=('Segoe UI', 8), bg='#FFFFFF', fg='#57606A',
                wraplength=300, justify=tk.LEFT).pack(anchor='w', pady=(0, 8))
        
        self.preset_var = tk.StringVar(value='default')
        
        presets_frame = tk.Frame(left_content, bg='#FFFFFF')
        presets_frame.pack(fill=tk.X, pady=(0, 10))
        
        presets = [
            ('default', 'Default (Baseline)', 'MAP: 5.5-6.0%', '~18min'),
            ('moderate', 'Moderate (Better)', 'MAP: 6.0-6.5%', '~22min'),
            ('aggressive', 'Aggressive (High)', 'MAP: 7.0-7.5%', '~27min'),
            ('maximum', 'Maximum (Best)', 'MAP: 8.0-8.5%', '~35min'),
        ]
        
        for value, name, map_range, time in presets:
            frame = tk.Frame(presets_frame, bg='#FFFFFF')
            frame.pack(fill=tk.X, pady=1)
            
            btn = tk.Radiobutton(
                frame,
                text=f"{name}\n{map_range} | {time}",
                variable=self.preset_var,
                value=value,
                font=('Segoe UI', 8),
                bg='#FFFFFF',
                fg='#24292F',
                selectcolor='#DDF4FF',
                indicatoron=False,
                width=28,
                height=2,
                relief=tk.GROOVE,
                borderwidth=1,
                command=self.on_preset_changed,
                anchor='w',
                padx=10
            )
            btn.pack(fill=tk.X)
        
        # Custom parameters
        self._create_section(left_content, '🔧 Custom Parameters')
        
        custom_toggle = tk.Checkbutton(
            left_content,
            text='Use custom parameters',
            font=('Segoe UI', 9),
            bg='#FFFFFF',
            fg='#24292F',
            command=self.toggle_custom_params
        )
        custom_toggle.pack(anchor='w', pady=(0, 8))
        self.custom_toggle_var = tk.BooleanVar(value=False)
        custom_toggle.configure(variable=self.custom_toggle_var)
        
        self.param_frame = tk.Frame(left_content, bg='#F6F8FA', relief=tk.SOLID, borderwidth=1)
        
        params_inner = tk.Frame(self.param_frame, bg='#F6F8FA')
        params_inner.pack(fill=tk.BOTH, padx=10, pady=10)
        
        params = [
            ('Rank (latent factors):', 'rank', '50', 'Higher = better but slower'),
            ('Alpha (confidence):', 'alpha', '40.0', 'Implicit feedback weight'),
            ('RegParam (regularization):', 'regParam', '0.1', 'Lower = less regularization'),
            ('MaxIter (iterations):', 'maxIter', '20', 'More = longer training'),
        ]
        
        self.param_vars = {}
        for label, key, default, hint in params:
            row = tk.Frame(params_inner, bg='#F6F8FA')
            row.pack(fill=tk.X, pady=4)
            
            tk.Label(row, text=label, font=('Segoe UI', 9, 'bold'),
                    bg='#F6F8FA', fg='#24292F').pack(anchor='w')
            
            var = tk.StringVar(value=default)
            self.param_vars[key] = var
            
            entry = tk.Entry(
                row,
                textvariable=var,
                font=('Segoe UI', 10),
                bg='#FFFFFF',
                relief=tk.SOLID,
                borderwidth=1
            )
            entry.pack(fill=tk.X, ipady=4, pady=2)
            
            tk.Label(row, text=hint, font=('Segoe UI', 8),
                    bg='#F6F8FA', fg='#57606A').pack(anchor='w')
        
        # Action buttons
        self._create_section(left_content, '🚀 Actions')
        
        btn_frame = tk.Frame(left_content, bg='#FFFFFF')
        btn_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.retrain_btn = tk.Button(
            btn_frame,
            text='🚀 Start Training',
            font=('Segoe UI', 10, 'bold'),
            bg='#1A7F37',
            fg='#FFFFFF',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.start_training,
            height=2
        )
        self.retrain_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 4))
        
        self.stop_btn = tk.Button(
            btn_frame,
            text='⏹️ Stop',
            font=('Segoe UI', 9),
            bg='#CF222E',
            fg='#FFFFFF',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.stop_training,
            state=tk.DISABLED,
            width=8
        )
        self.stop_btn.pack(side=tk.LEFT)
        
        self.progress = ttk.Progressbar(left_content, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(8, 0))
        
        # === RIGHT PANEL CONTENT (LOGS) ===
        log_header = tk.Frame(right_panel, bg='#F6F8FA', height=40)
        log_header.pack(fill=tk.X)
        log_header.pack_propagate(False)
        
        tk.Label(
            log_header,
            text='📊 Training Output',
            font=('Segoe UI', 10, 'bold'),
            bg='#F6F8FA',
            fg='#24292F'
        ).pack(side=tk.LEFT, padx=15, pady=10)
        
        tk.Button(
            log_header,
            text='Clear',
            font=('Segoe UI', 8),
            bg='#FFFFFF',
            fg='#24292F',
            relief=tk.SOLID,
            borderwidth=1,
            cursor='hand2',
            command=self.clear_log
        ).pack(side=tk.RIGHT, padx=15)
        
        # Log area
        log_frame = tk.Frame(right_panel, bg='#FFFFFF')
        log_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=('Consolas', 9),
            bg='#0D1117',
            fg='#C9D1D9',
            insertbackground='#C9D1D9',
            relief=tk.FLAT,
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure log tags
        self.log_text.tag_config('header', foreground='#58A6FF', font=('Consolas', 9, 'bold'))
        self.log_text.tag_config('success', foreground='#3FB950')
        self.log_text.tag_config('error', foreground='#F85149')
        self.log_text.tag_config('warning', foreground='#D29922')
        self.log_text.tag_config('info', foreground='#79C0FF')
        self.log_text.tag_config('normal', foreground='#C9D1D9')
    
    def _create_section(self, parent, title):
        """Create a section header"""
        tk.Label(
            parent,
            text=title,
            font=('Segoe UI', 9, 'bold'),
            bg='#FFFFFF',
            fg='#24292F'
        ).pack(anchor='w', pady=(10, 6))
        
        tk.Frame(parent, bg='#D0D7DE', height=1).pack(fill=tk.X, pady=(0, 6))
    
    def browse_file(self):
        """Browse for Python file"""
        filename = filedialog.askopenfilename(
            title='Select Training Script',
            filetypes=[('Python Files', '*.py'), ('All Files', '*.*')]
        )
        if filename:
            self.file_var.set(filename)
    
    def on_preset_changed(self):
        """Handle preset change"""
        preset = self.preset_var.get()
        preset_data = QuickRetrainHelper.PRESETS.get(preset, QuickRetrainHelper.PRESETS['default'])
        
        # Update parameter values
        self.param_vars['rank'].set(str(preset_data['rank']))
        self.param_vars['alpha'].set(str(preset_data['alpha']))
        self.param_vars['regParam'].set(str(preset_data['regParam']))
        self.param_vars['maxIter'].set(str(preset_data['maxIter']))
        
        # Uncheck custom
        self.custom_toggle_var.set(False)
        self.param_frame.pack_forget()
    
    def toggle_custom_params(self):
        """Toggle custom parameters visibility"""
        if self.custom_toggle_var.get():
            self.param_frame.pack(fill=tk.X, pady=(0, 15))
        else:
            self.param_frame.pack_forget()
    
    def start_training(self):
        """Start training with selected parameters"""
        filepath = self.file_var.get().strip()
        if not filepath:
            messagebox.showwarning('No File', 'Please select a training script first.')
            return
        
        if not os.path.exists(filepath):
            messagebox.showerror('File Not Found', f'File does not exist:\n{filepath}')
            return
        
        # Get parameters
        if self.custom_toggle_var.get():
            try:
                params = {
                    'rank': int(self.param_vars['rank'].get()),
                    'alpha': float(self.param_vars['alpha'].get()),
                    'regParam': float(self.param_vars['regParam'].get()),
                    'maxIter': int(self.param_vars['maxIter'].get())
                }
                msg = f"Train with custom parameters?\n\nRank: {params['rank']}\nAlpha: {params['alpha']}\nRegParam: {params['regParam']}\nMaxIter: {params['maxIter']}"
                preset_name = None
            except ValueError as e:
                messagebox.showerror('Invalid Parameters', f'Please enter valid numbers:\n{e}')
                return
        else:
            preset = self.preset_var.get()
            preset_data = QuickRetrainHelper.PRESETS[preset]
            params = None
            preset_name = preset
            msg = f"Train with {preset_data['name']}?\n\nExpected MAP: {preset_data['expected_map']}\nTime: {preset_data['time']}"
        
        if not messagebox.askyesno('Confirm Training', msg):
            return
        
        # Start training
        self.is_running = True
        self.retrain_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress.start(10)
        self.clear_log()
        
        self.append_log('=' * 80, 'header')
        self.append_log('🔥 PARAMETER TUNING - Starting Training', 'header')
        self.append_log('=' * 80, 'header')
        
        def run_training():
            container = self.container_var.get()
            master = self.master_var.get()
            
            success = QuickRetrainHelper.quick_retrain(
                filepath, container, master,
                preset_name=preset_name,
                custom_params=params,
                log_callback=self.append_log
            )
            
            self.is_running = False
            self.progress.stop()
            self.retrain_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            
            if success:
                self.append_log('\n' + '=' * 80, 'header')
                self.append_log('✅ TRAINING COMPLETED SUCCESSFULLY!', 'success')
                self.append_log('=' * 80, 'header')
            else:
                self.append_log('\n' + '=' * 80, 'header')
                self.append_log('❌ TRAINING FAILED', 'error')
                self.append_log('=' * 80, 'header')
        
        self.thread_pool.submit(run_training)
    
    def stop_training(self):
        """Stop training"""
        if messagebox.askyesno('Stop Training', 'Stop the current training job?'):
            self.is_running = False
            self.append_log('\n⏹️ Training stopped by user', 'warning')
    
    def _start_log_processor(self):
        """Start log queue processor"""
        def process_queue():
            try:
                while True:
                    message, tag = self.log_queue.get(timeout=0.1)
                    self._append_to_log(message, tag)
            except:
                pass
            self.frame.after(100, process_queue)
        
        process_queue()
    
    def _append_to_log(self, message, tag='normal'):
        """Append to log (must be called from main thread)"""
        self.log_text.insert(tk.END, message + '\n', tag)
        self.log_text.see(tk.END)
    
    def append_log(self, message, tag='normal'):
        """Thread-safe log append"""
        self.log_queue.put((message, tag))
    
    def clear_log(self):
        """Clear log"""
        self.log_text.delete('1.0', tk.END)
    
    def cleanup(self):
        """Cleanup resources"""
        self.is_running = False
        self.thread_pool.shutdown(wait=False)

