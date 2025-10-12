"""
HDFS Upload Tab - V4 Clean Professional Edition
Clean, minimal UI inspired by GitHub/VS Code
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from datetime import datetime


# ============================================================================
# V4 CLEAN COMPONENTS (Shared with Spark Runner Tab)
# ============================================================================

class CleanButton:
    """Clean button with GitHub-style design"""
    
    STYLES = {
        'primary': {
            'bg': '#0969DA', 'fg': 'white',
            'hover_bg': '#0860CA', 'active_bg': '#0757BA'
        },
        'success': {
            'bg': '#1A7F37', 'fg': 'white',
            'hover_bg': '#1A7F37', 'active_bg': '#18692F'
        },
        'danger': {
            'bg': '#CF222E', 'fg': 'white',
            'hover_bg': '#C11F2A', 'active_bg': '#A40E26'
        },
        'secondary': {
            'bg': '#6E7781', 'fg': 'white',
            'hover_bg': '#57606A', 'active_bg': '#424A53'
        },
        'outline': {
            'bg': '#FFFFFF', 'fg': '#24292F',
            'hover_bg': '#F3F4F6', 'active_bg': '#E5E7EB',
            'border': '#D0D7DE'
        }
    }
    
    def __init__(self, parent, text, command=None, style='primary'):
        self.command = command
        self.style_config = self.STYLES.get(style, self.STYLES['primary'])
        self.default_bg = self.style_config['bg']
        self.hover_bg = self.style_config['hover_bg']
        
        # Create label as button
        self.label = tk.Label(
            parent,
            text=text,
            bg=self.default_bg,
            fg=self.style_config['fg'],
            font=('Segoe UI', 9, 'normal'),
            cursor='hand2',
            padx=12,
            pady=7,
            relief=tk.FLAT
        )
        
        # Add border for outline style
        if style == 'outline':
            self.label.config(
                relief=tk.SOLID,
                borderwidth=1,
                highlightthickness=1,
                highlightbackground=self.style_config['border']
            )
        
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
    
    def pack(self, **kwargs):
        return self.label.pack(**kwargs)
    
    def grid(self, **kwargs):
        return self.label.grid(**kwargs)
    
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
                bg='#F6F8FA',
                fg='#24292F',
                font=('Segoe UI', 10, 'bold'),
                anchor='w',
                padx=16
            )
            title_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Content area
        self.content = tk.Frame(self, bg='#FFFFFF', padx=16, pady=12)
        self.content.pack(fill=tk.BOTH, expand=True)
    
    def get_content(self):
        return self.content


class StatusBadge(tk.Label):
    """Status badge with color coding"""
    
    COLORS = {
        'success': {'bg': '#DDF4E6', 'fg': '#1A7F37', 'dot': '●'},
        'error': {'bg': '#FFE4E6', 'fg': '#CF222E', 'dot': '●'},
        'warning': {'bg': '#FFF8C5', 'fg': '#9A6700', 'dot': '●'},
        'info': {'bg': '#DDF4FF', 'fg': '#0969DA', 'dot': '●'},
        'neutral': {'bg': '#F6F8FA', 'fg': '#6E7781', 'dot': '○'}
    }
    
    def __init__(self, parent, text="", status='neutral'):
        colors = self.COLORS.get(status, self.COLORS['neutral'])
        super().__init__(
            parent,
            text=f"{colors['dot']} {text}",
            bg=colors['bg'],
            fg=colors['fg'],
            font=('Segoe UI', 9),
            padx=10,
            pady=4,
            relief=tk.FLAT
        )


# ============================================================================
# HDFS UPLOAD TAB
# ============================================================================

class HDFSUploadTabV4Clean:
    """Clean Professional HDFS Upload Tab"""
    
    # Supported file types
    FILE_ICONS = {
        '.py': '🐍', '.csv': '📊', '.json': '📄', '.txt': '📝',
        '.zip': '📦', '.gz': '📦', '.tar': '📦',
        '.log': '📋', '.md': '📝', '.parquet': '📊',
        'default': '📁'
    }
    
    def __init__(self, parent_frame, config, status_callback, log_callback):
        self.frame = parent_frame
        self.config = config
        self.update_status = status_callback
        self.append_log = log_callback
        self.selected_files = []
        self.is_uploading = False
        
        # Thread pool for background tasks
        self.thread_pool = ThreadPoolExecutor(max_workers=3)
        
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
        
        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        # Two column layout - Left 30%, Right 70%
        scroll_frame.grid_columnconfigure(0, weight=30, minsize=400)
        scroll_frame.grid_columnconfigure(1, weight=70)
        scroll_frame.grid_rowconfigure(0, weight=1)
        
        left_col = tk.Frame(scroll_frame, bg='#F6F8FA')
        left_col.grid(row=0, column=0, sticky='nsew', padx=(0, 8))
        
        right_col = tk.Frame(scroll_frame, bg='#F6F8FA')
        right_col.grid(row=0, column=1, sticky='nsew', padx=(8, 0))
        
        # ===== LEFT COLUMN =====
        
        # Header
        header = tk.Label(
            left_col,
            text="📤 HDFS Upload",
            bg='#F6F8FA',
            fg='#24292F',
            font=('Segoe UI', 16, 'bold'),
            anchor='w'
        )
        header.pack(fill=tk.X, pady=(0, 4))
        
        subtitle = tk.Label(
            left_col,
            text="Upload files to Hadoop HDFS",
            bg='#F6F8FA',
            fg='#6E7781',
            font=('Segoe UI', 9),
            anchor='w'
        )
        subtitle.pack(fill=tk.X, pady=(0, 20))
        
        # === Config Card ===
        config_card = SectionCard(left_col, title="⚙️ Configuration")
        config_card.pack(fill=tk.X, pady=(0, 12))
        
        config_content = config_card.get_content()
        
        # Container
        tk.Label(
            config_content,
            text="Container:",
            bg='#FFFFFF',
            fg='#24292F',
            font=('Segoe UI', 9, 'bold')
        ).pack(anchor='w', pady=(0, 4))
        
        self.container_var = tk.StringVar(value=self.config.get('hdfs_container', 'namenode'))
        container_combo = ttk.Combobox(
            config_content,
            textvariable=self.container_var,
            values=['namenode', 'datanode', 'spark-worker'],
            state='readonly',
            width=35,
            font=('Segoe UI', 9)
        )
        container_combo.pack(fill=tk.X, pady=(0, 12))
        
        # HDFS Path
        tk.Label(
            config_content,
            text="Upload Path:",
            bg='#FFFFFF',
            fg='#24292F',
            font=('Segoe UI', 9, 'bold')
        ).pack(anchor='w', pady=(0, 4))
        
        self.path_var = tk.StringVar(value=self.config.get('hdfs_path', '/user/spark/data'))
        path_entry = tk.Entry(
            config_content,
            textvariable=self.path_var,
            font=('Segoe UI', 9),
            relief=tk.SOLID,
            borderwidth=1,
            highlightthickness=0
        )
        path_entry.pack(fill=tk.X, pady=(0, 12))
        
        # Options
        self.auto_extract_var = tk.BooleanVar(value=True)
        extract_check = tk.Checkbutton(
            config_content,
            text='Auto-extract compressed files',
            variable=self.auto_extract_var,
            bg='#FFFFFF',
            fg='#24292F',
            font=('Segoe UI', 9),
            activebackground='#FFFFFF',
            selectcolor='#FFFFFF'
        )
        extract_check.pack(anchor='w', pady=(0, 8))
        
        # Buttons
        btn_frame = tk.Frame(config_content, bg='#FFFFFF')
        btn_frame.pack(fill=tk.X, pady=(8, 0))
        
        CleanButton(btn_frame, "💾 Save Config", self.save_config, 'primary').pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        CleanButton(btn_frame, "🔍 Test", self.test_connection, 'secondary').pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0))
        
        # === File Selection Card ===
        files_card = SectionCard(left_col, title="📁 Select Files")
        files_card.pack(fill=tk.X, pady=(0, 12))
        
        files_content = files_card.get_content()
        
        # Add buttons
        add_btn_frame = tk.Frame(files_content, bg='#FFFFFF')
        add_btn_frame.pack(fill=tk.X, pady=(0, 8))
        
        CleanButton(add_btn_frame, "➕ Add Files", self.add_files, 'primary').pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        CleanButton(add_btn_frame, "📂 Add Folder", self.add_folder, 'primary').pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0))
        
        # File count
        self.file_count_label = tk.Label(
            files_content,
            text="0 files selected",
            bg='#FFFFFF',
            fg='#6E7781',
            font=('Segoe UI', 9)
        )
        self.file_count_label.pack(anchor='w', pady=(8, 0))
        
        # === Upload Actions Card ===
        actions_card = SectionCard(left_col, title="🚀 Actions")
        actions_card.pack(fill=tk.X, pady=(0, 12))
        
        actions_content = actions_card.get_content()
        
        CleanButton(actions_content, "▶ Upload to HDFS", self.start_upload, 'success').pack(
            fill=tk.X, pady=(0, 8))
        CleanButton(actions_content, "⏹ Stop Upload", self.stop_upload, 'danger').pack(
            fill=tk.X, pady=(0, 8))
        CleanButton(actions_content, "🗑️ Clear All", self.clear_files, 'secondary').pack(
            fill=tk.X)
        
        # === Status Card ===
        status_card = SectionCard(left_col, title="📊 Status")
        status_card.pack(fill=tk.X, pady=(0, 12))
        
        status_content = status_card.get_content()
        
        self.status_badge = StatusBadge(status_content, "Ready", 'neutral')
        self.status_badge.pack(anchor='w')
        
        # ===== RIGHT COLUMN =====
        
        # File List Card
        list_card = SectionCard(right_col, title="📋 Selected Files")
        list_card.pack(fill=tk.BOTH, expand=True, pady=(0, 12))
        
        list_content = list_card.get_content()
        
        # Scrollable file list
        list_canvas = tk.Canvas(list_content, bg='#FFFFFF', highlightthickness=0, height=200)
        list_scrollbar = tk.Scrollbar(list_content, orient='vertical', command=list_canvas.yview)
        
        self.file_list_frame = tk.Frame(list_canvas, bg='#FFFFFF')
        self.file_list_frame.bind(
            '<Configure>',
            lambda e: list_canvas.configure(scrollregion=list_canvas.bbox('all'))
        )
        
        list_canvas.create_window((0, 0), window=self.file_list_frame, anchor='nw')
        list_canvas.configure(yscrollcommand=list_scrollbar.set)
        
        list_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Upload Log Card
        log_card = SectionCard(right_col, title="📝 Upload Log")
        log_card.pack(fill=tk.BOTH, expand=True)
        
        log_content = log_card.get_content()
        
        # Log toolbar
        log_toolbar = tk.Frame(log_content, bg='#FFFFFF', height=36)
        log_toolbar.pack(fill=tk.X, side=tk.TOP, pady=(0, 8))
        log_toolbar.pack_propagate(False)
        
        # Auto-scroll toggle
        self.auto_scroll_var = tk.BooleanVar(value=True)
        auto_scroll_check = tk.Checkbutton(
            log_toolbar,
            text='🔽 Auto-scroll',
            variable=self.auto_scroll_var,
            bg='#FFFFFF',
            fg='#24292F',
            font=('Segoe UI', 9),
            activebackground='#FFFFFF',
            selectcolor='#FFFFFF',
            cursor='hand2'
        )
        auto_scroll_check.pack(side=tk.LEFT, padx=(0, 8))
        
        # Clear log button
        clear_btn = CleanButton(log_toolbar, "🗑️ Clear", self.clear_log, 'secondary')
        clear_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        # Copy log button
        copy_btn = CleanButton(log_toolbar, "📋 Copy", self.copy_log, 'secondary')
        copy_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        # Log stats
        self.log_stats_label = tk.Label(
            log_toolbar,
            text="0 lines",
            bg='#FFFFFF',
            fg='#6E7781',
            font=('Segoe UI', 8)
        )
        self.log_stats_label.pack(side=tk.RIGHT, padx=(8, 0))
        
        # Log text with scrollbar
        log_frame = tk.Frame(log_content, bg='#24292F')
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        log_scrollbar = tk.Scrollbar(log_frame, orient='vertical', bg='#24292F')
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(
            log_frame,
            height=15,
            wrap=tk.WORD,
            bg='#24292F',
            fg='#E6EDF3',
            font=('Consolas', 9),
            relief=tk.FLAT,
            borderwidth=0,
            padx=12,
            pady=12,
            yscrollcommand=log_scrollbar.set,
            cursor='arrow'
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        log_scrollbar.config(command=self.log_text.yview)
        
        # Color tags with better contrast
        self.log_text.tag_config('success', foreground='#7EE787', font=('Consolas', 9))
        self.log_text.tag_config('error', foreground='#FF7B72', font=('Consolas', 9, 'bold'))
        self.log_text.tag_config('warning', foreground='#FFA657', font=('Consolas', 9))
        self.log_text.tag_config('info', foreground='#79C0FF', font=('Consolas', 9))
        self.log_text.tag_config('normal', foreground='#E6EDF3', font=('Consolas', 9))
        self.log_text.tag_config('highlight', background='#1F6FEB', foreground='#FFFFFF')
        
        # Prevent editing
        self.log_text.bind('<Key>', lambda e: 'break')
        
        # Log line counter
        self.log_line_count = 0
        
        self.log("📤 HDFS Upload Manager ready", 'info')
        self.log(f"📁 Config file: {os.path.abspath('spark_runner_config.json')}", 'info')
    
    def log(self, message, tag='info'):
        """Add message to log with timestamp"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            full_message = f"[{timestamp}] {message}"
            
            # Check if log_text exists
            if not hasattr(self, 'log_text'):
                print(f"WARNING: log_text not initialized yet. Message: {full_message}")
                # Try to use callback only
                if self.append_log:
                    self.append_log(full_message)
                return
            
            # Always log to text widget
            self.log_text.insert(tk.END, full_message, tag)
            self.log_text.insert(tk.END, "\n" if not message.endswith("\n") else "")
            self.log_text.see(tk.END)
            self.log_text.update_idletasks()  # Force update
            
            # Also log to main log if callback exists
            if self.append_log:
                self.append_log(full_message)
        except Exception as e:
            # Fallback - print to console
            print(f"ERROR in log(): {str(e)}")
            print(f"Message was: {message}")
            import traceback
            traceback.print_exc()
    
    def update_file_list(self):
        """Update file list display"""
        # Clear current list
        for widget in self.file_list_frame.winfo_children():
            widget.destroy()
        
        # Update count
        count = len(self.selected_files)
        self.file_count_label.config(text=f"{count} file{'s' if count != 1 else ''} selected")
        
        # Show files
        for i, filepath in enumerate(self.selected_files):
            file_frame = tk.Frame(self.file_list_frame, bg='#F6F8FA', relief=tk.SOLID, 
                                borderwidth=1, highlightthickness=0)
            file_frame.pack(fill=tk.X, pady=(0, 4))
            
            # Get icon
            ext = Path(filepath).suffix.lower()
            icon = self.FILE_ICONS.get(ext, self.FILE_ICONS['default'])
            
            # File info
            info_frame = tk.Frame(file_frame, bg='#F6F8FA')
            info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=6)
            
            name_label = tk.Label(
                info_frame,
                text=f"{icon} {Path(filepath).name}",
                bg='#F6F8FA',
                fg='#24292F',
                font=('Segoe UI', 9, 'bold'),
                anchor='w'
            )
            name_label.pack(anchor='w')
            
            size = os.path.getsize(filepath)
            size_text = f"{size/1024:.1f} KB" if size < 1024*1024 else f"{size/1024/1024:.1f} MB"
            
            details_label = tk.Label(
                info_frame,
                text=f"{size_text} • {Path(filepath).parent}",
                bg='#F6F8FA',
                fg='#6E7781',
                font=('Segoe UI', 8),
                anchor='w'
            )
            details_label.pack(anchor='w')
            
            # Remove button
            remove_btn = tk.Label(
                file_frame,
                text="✕",
                bg='#F6F8FA',
                fg='#CF222E',
                font=('Segoe UI', 12, 'bold'),
                cursor='hand2',
                padx=10
            )
            remove_btn.pack(side=tk.RIGHT, pady=6)
            remove_btn.bind('<Button-1>', lambda e, f=filepath: self.remove_file(f))
            remove_btn.bind('<Enter>', lambda e, w=remove_btn: w.config(bg='#FFE4E6'))
            remove_btn.bind('<Leave>', lambda e, w=remove_btn: w.config(bg='#F6F8FA'))
    
    def add_files(self):
        """Add files to upload list"""
        self.log("📂 Opening file dialog...", 'info')
        
        files = filedialog.askopenfilenames(
            title="Select files to upload",
            filetypes=[
                ("All files", "*.*"),
                ("Data files", "*.csv *.json *.parquet"),
                ("Text files", "*.txt *.log *.md"),
                ("Compressed", "*.zip *.gz *.tar")
            ]
        )
        
        if not files:
            self.log("No files selected", 'warning')
            return
        
        added = 0
        for file in files:
            if file not in self.selected_files:
                self.selected_files.append(file)
                self.log(f"➕ Added: {Path(file).name}", 'success')
                added += 1
            else:
                self.log(f"⚠️ Already added: {Path(file).name}", 'warning')
        
        self.update_file_list()
        self.log(f"✅ Total added: {added} file(s)", 'success')
    
    def add_folder(self):
        """Add all files from folder"""
        self.log("📂 Opening folder dialog...", 'info')
        
        folder = filedialog.askdirectory(title="Select folder")
        
        if not folder:
            self.log("No folder selected", 'warning')
            return
        
        self.log(f"📁 Scanning folder: {folder}", 'info')
        count = 0
        
        for root, dirs, files in os.walk(folder):
            for file in files:
                filepath = os.path.join(root, file)
                if filepath not in self.selected_files:
                    self.selected_files.append(filepath)
                    self.log(f"➕ Added: {Path(filepath).name}", 'success')
                    count += 1
        
        self.update_file_list()
        self.log(f"✅ Total added: {count} file(s) from folder", 'success')
    
    def remove_file(self, filepath):
        """Remove file from list"""
        if filepath in self.selected_files:
            self.selected_files.remove(filepath)
            self.update_file_list()
            self.log(f"🗑️ Removed: {Path(filepath).name}", 'warning')
    
    def clear_files(self):
        """Clear all selected files"""
        count = len(self.selected_files)
        if count == 0:
            self.log("No files to clear", 'warning')
            return
        
        self.selected_files.clear()
        self.update_file_list()
        self.log(f"🗑️ Cleared {count} file(s)", 'warning')
    
    def save_config(self):
        """Save HDFS configuration to JSON file"""
        self.config['hdfs_container'] = self.container_var.get()
        self.config['hdfs_path'] = self.path_var.get()
        self.config['auto_extract'] = self.auto_extract_var.get()
        
        # Save to file
        try:
            config_file = 'spark_runner_config.json'
            with open(config_file, 'w', encoding='utf-8') as f:
                import json
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            
            self.log(f"✓ Configuration saved to {os.path.abspath(config_file)}", 'success')
            if self.update_status:
                self.update_status("Configuration saved")
            messagebox.showinfo("Success", f"Configuration saved successfully!\n\nFile: {os.path.abspath(config_file)}")
        except Exception as e:
            self.log(f"❌ Failed to save config: {str(e)}", 'error')
            messagebox.showerror("Error", f"Failed to save configuration:\n{str(e)}")
    
    def test_connection(self):
        """Test HDFS connection"""
        try:
            self.log("🔍 Testing HDFS connection...", 'info')
            self.log("  ↳ Step 1: Update status badge", 'info')
            self.status_badge.config(text="● Testing...", bg='#DDF4FF', fg='#0969DA')
            
            self.log("  ↳ Step 2: Get container name", 'info')
            container = self.container_var.get()
            self.log(f"📦 Container: {container}", 'info')
            
            self.log("  ↳ Step 3: Define test function", 'info')
            def test():
                try:
                    self.log("🔄 Thread started successfully", 'info')
                    self.log(f"💻 Executing: docker exec {container} hdfs dfs -ls /", 'info')
                    
                    result = subprocess.run(
                        ['docker', 'exec', container, 'hdfs', 'dfs', '-ls', '/'],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    self.log(f"✓ Command completed. Return code: {result.returncode}", 'info')
                    
                    if result.returncode == 0:
                        self.log("✅ Connection successful!", 'success')
                        if result.stdout:
                            self.log(f"Output:\n{result.stdout}", 'normal')
                        self.status_badge.config(text="● Connected", bg='#DFF6DD', fg='#1A7F37')
                        self.frame.after(0, lambda: messagebox.showinfo("Success", "HDFS connection test passed!"))
                    else:
                        error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                        self.log(f"❌ Connection failed: {error_msg}", 'error')
                        self.status_badge.config(text="● Error", bg='#FFEBE9', fg='#CF222E')
                        self.frame.after(0, lambda: messagebox.showerror("Connection Failed", f"HDFS test failed:\n{error_msg}"))
                except subprocess.TimeoutExpired:
                    self.log("❌ Connection timeout (10s)", 'error')
                    self.status_badge.config(text="● Timeout", bg='#FFEBE9', fg='#CF222E')
                    self.frame.after(0, lambda: messagebox.showerror("Timeout", "Connection test timed out after 10 seconds"))
                except FileNotFoundError:
                    self.log("❌ Docker command not found. Is Docker installed?", 'error')
                    self.status_badge.config(text="● Error", bg='#FFEBE9', fg='#CF222E')
                    self.frame.after(0, lambda: messagebox.showerror("Docker Not Found", "Docker command not found. Please ensure Docker is installed and in PATH."))
                except Exception as e:
                    import traceback
                    error_details = traceback.format_exc()
                    self.log(f"❌ Thread unexpected error: {str(e)}", 'error')
                    self.log(f"Details: {error_details}", 'error')
                    self.status_badge.config(text="● Error", bg='#FFEBE9', fg='#CF222E')
                    self.frame.after(0, lambda: messagebox.showerror("Error", f"Test failed:\n{str(e)}"))
            
            # Use thread pool
            self.log("  ↳ Step 4: Submit to thread pool", 'info')
            try:
                future = self.thread_pool.submit(test)
                self.log(f"✓ Thread submitted successfully. Future: {future}", 'success')
            except Exception as e:
                import traceback
                self.log(f"❌ Failed to submit thread: {str(e)}", 'error')
                self.log(f"Traceback: {traceback.format_exc()}", 'error')
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.log(f"❌ MAIN THREAD ERROR in test_connection: {str(e)}", 'error')
            self.log(f"Full traceback:\n{error_details}", 'error')
            messagebox.showerror("Error", f"Failed to start test:\n{str(e)}")
    
    def start_upload(self):
        """Start uploading files"""
        if not self.selected_files:
            self.log("❌ No files selected", 'error')
            messagebox.showwarning("No Files", "Please select files to upload")
            return
        
        if self.is_uploading:
            self.log("⚠️ Upload already in progress", 'warning')
            messagebox.showinfo("Upload in Progress", "Upload is already running")
            return
        
        self.is_uploading = True
        self.status_badge.config(text="● Uploading...", bg='#DDF4FF', fg='#0969DA')
        
        total_files = len(self.selected_files)
        container = self.container_var.get()
        hdfs_path = self.path_var.get()
        
        self.log("=" * 60, 'info')
        self.log(f"▶ Starting upload of {total_files} file(s)", 'info')
        self.log(f"📦 Container: {container}", 'info')
        self.log(f"📁 HDFS Path: {hdfs_path}", 'info')
        self.log("=" * 60, 'info')
        
        def upload():
            success = 0
            failed = 0
            
            try:
                self.log("🔄 Upload thread started", 'info')
                
                # Step 0: Ensure HDFS directory exists
                self.log("", 'info')
                self.log("📁 Checking HDFS directory...", 'info')
                mkdir_cmd = ['docker', 'exec', container, 'hdfs', 'dfs', '-mkdir', '-p', hdfs_path]
                self.log(f"  💻 $ hdfs dfs -mkdir -p {hdfs_path}", 'normal')
                
                mkdir_result = subprocess.run(mkdir_cmd, capture_output=True, text=True, timeout=30)
                if mkdir_result.returncode == 0:
                    self.log(f"  ✓ Directory ready: {hdfs_path}", 'success')
                else:
                    # Directory might already exist, that's OK
                    if "File exists" in mkdir_result.stderr:
                        self.log(f"  ✓ Directory already exists: {hdfs_path}", 'success')
                    else:
                        self.log(f"  ⚠️ mkdir warning: {mkdir_result.stderr.strip()}", 'warning')
                
                for i, filepath in enumerate(self.selected_files, 1):
                    if not self.is_uploading:
                        self.log("", 'warning')
                        self.log("⏹ Upload cancelled by user", 'warning')
                        break
                    
                    try:
                        filename = Path(filepath).name
                        self.log("", 'info')
                        self.log(f"[{i}/{total_files}] 📤 Uploading: {filename}", 'info')
                        self.log(f"      Size: {os.path.getsize(filepath) / 1024:.1f} KB", 'info')
                        
                        # Step 1: Copy to container
                        copy_cmd = ['docker', 'cp', filepath, f'{container}:/tmp/{filename}']
                        self.log(f"      Step 1/4: Copy to container", 'info')
                        self.log(f"      💻 $ docker cp \"{filename}\" {container}:/tmp/", 'normal')
                        
                        result = subprocess.run(copy_cmd, check=True, capture_output=True, timeout=60, text=True)
                        self.log(f"      ✓ Copied to container /tmp/", 'success')
                        
                        # Step 2: Put to HDFS with proper path (directory + filename)
                        target_path = f"{hdfs_path.rstrip('/')}/{filename}"
                        hdfs_cmd = ['docker', 'exec', container, 'hdfs', 'dfs', '-put', '-f',
                                   f'/tmp/{filename}', target_path]
                        self.log(f"      Step 2/4: Upload to HDFS", 'info')
                        self.log(f"      💻 $ hdfs dfs -put -f /tmp/{filename} {target_path}", 'normal')
                        
                        result = subprocess.run(hdfs_cmd, capture_output=True, text=True, timeout=60)
                        
                        if result.returncode == 0:
                            self.log(f"      ✓ Uploaded to HDFS", 'success')
                            self.log(f"      📍 Location: {target_path}", 'success')
                            success += 1
                        else:
                            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                            self.log(f"      ❌ HDFS upload failed: {error_msg}", 'error')
                            failed += 1
                        
                        # Step 3: Verify file exists in HDFS
                        verify_cmd = ['docker', 'exec', container, 'hdfs', 'dfs', '-test', '-e', target_path]
                        verify_result = subprocess.run(verify_cmd, capture_output=True, timeout=10)
                        if verify_result.returncode == 0:
                            self.log(f"      Step 3/4: File verified in HDFS ✓", 'success')
                        else:
                            self.log(f"      ⚠️ Warning: Could not verify file in HDFS", 'warning')
                        
                        # Step 4: Cleanup
                        self.log(f"      Step 4/4: Cleanup temp file", 'info')
                        subprocess.run(['docker', 'exec', container, 'rm', f'/tmp/{filename}'],
                                     capture_output=True, timeout=10)
                        self.log(f"      ✓ Cleaned up /tmp/{filename}", 'success')
                        
                    except subprocess.TimeoutExpired:
                        self.log(f"      ❌ Timeout uploading {filename}", 'error')
                        failed += 1
                    except subprocess.CalledProcessError as e:
                        error_msg = e.stderr.strip() if e.stderr else str(e)
                        self.log(f"      ❌ Command failed: {error_msg}", 'error')
                        failed += 1
                    except FileNotFoundError:
                        self.log(f"      ❌ Docker not found. Is Docker running?", 'error')
                        failed += 1
                    except Exception as e:
                        import traceback
                        self.log(f"      ❌ Error: {str(e)}", 'error')
                        self.log(f"      Details: {traceback.format_exc()}", 'error')
                        failed += 1
                
            except Exception as e:
                import traceback
                self.log(f"❌ Upload thread error: {str(e)}", 'error')
                self.log(f"Details: {traceback.format_exc()}", 'error')
            
            finally:
                self.is_uploading = False
                
                # Summary
                self.log("", 'info')
                self.log("=" * 60, 'info')
                self.log(f"📊 Upload Summary", 'info')
                self.log(f"   ✅ Success: {success}", 'success')
                self.log(f"   ❌ Failed: {failed}", 'error' if failed > 0 else 'info')
                self.log(f"   📁 Total: {success + failed}", 'info')
                self.log("=" * 60, 'info')
                
                # Update status - must use after() for thread safety
                if failed == 0 and success > 0:
                    self.status_badge.config(text="● Complete", bg='#DFF6DD', fg='#1A7F37')
                    self.frame.after(0, lambda: messagebox.showinfo("Upload Complete", f"Successfully uploaded {success} file(s)!"))
                elif failed > 0:
                    self.status_badge.config(text="● Errors", bg='#FFEBE9', fg='#CF222E')
                    self.frame.after(0, lambda: messagebox.showwarning("Upload Complete with Errors", 
                                          f"Uploaded {success} file(s)\nFailed: {failed} file(s)"))
                else:
                    self.status_badge.config(text="● Ready", bg='#F6F8FA', fg='#6E7781')
        
        # Use thread pool
        self.log("🔄 Submitting upload to thread pool...", 'info')
        try:
            future = self.thread_pool.submit(upload)
            self.log(f"✓ Upload thread submitted. Future: {future}", 'success')
        except Exception as e:
            self.log(f"❌ Failed to submit upload thread: {str(e)}", 'error')
            self.is_uploading = False
    
    def stop_upload(self):
        """Stop upload process"""
        if not self.is_uploading:
            self.log("⚠️ No upload in progress", 'warning')
            return
        
        self.is_uploading = False
        self.log("", 'warning')
        self.log("⏹ Stopping upload...", 'warning')
        self.status_badge.config(text="● Stopping...", bg='#FFF8C5', fg='#9A6700')
