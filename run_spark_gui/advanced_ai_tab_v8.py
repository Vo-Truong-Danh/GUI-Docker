#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced AI Tab V8.3 - Optimized for PySpark
Features:
- Real HDFS integration
- PySpark code generation (temperature 0.0)
- System instruction for code-only output
- Clean, professional UI
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import asyncio
import os
import subprocess
from pathlib import Path

# Import AI Engine V8.3
try:
    from advanced_ai_engine_v8 import (
        AdvancedAIEngine, AIConfig, AIProvider,
        AnalysisResult, DataAnalyzer
    )
    AI_ENGINE_AVAILABLE = True
except ImportError:
    AI_ENGINE_AVAILABLE = False
    print("⚠️ AI Engine V8.3 not available")

# ============================================================================
# HDFS UTILITIES
# ============================================================================

def get_hdfs_files(hdfs_path="/", hdfs_host="namenode", hdfs_port="8020"):
    """Get list of files from HDFS using hdfs dfs -ls
    
    Returns list of dicts with:
        - name: basename only (e.g., "data")
        - path: full HDFS path (e.g., "/input/data")
        - size: file size or '-' for directories
        - is_dir: True if directory
        - type: 'DIR' or 'FILE'
    """
    try:
        # Normalize path: remove trailing slash except for root
        if hdfs_path != '/' and hdfs_path.endswith('/'):
            hdfs_path = hdfs_path.rstrip('/')
        
        cmd = f"docker exec namenode hdfs dfs -ls {hdfs_path}"
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            files = []
            
            for line in lines[1:]:  # Skip header "Found X items"
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 8:
                        permissions = parts[0]
                        size = parts[4]
                        full_path = parts[7]  # This is the FULL path from HDFS
                        is_dir = permissions.startswith('d')
                        
                        # Extract basename for display
                        basename = os.path.basename(full_path) or full_path
                        
                        files.append({
                            'name': basename,
                            'path': full_path,  # Keep full path for navigation
                            'size': size if not is_dir else '-',
                            'is_dir': is_dir,
                            'type': 'DIR' if is_dir else 'FILE'
                        })
            
            return files
        else:
            print(f"HDFS ls error: {result.stderr}")
            return []
    
    except Exception as e:
        print(f"Error listing HDFS: {e}")
        return []


class HDFSBrowser(tk.Toplevel):
    """Real HDFS Browser"""
    
    def __init__(self, parent, hdfs_host='namenode', hdfs_port='8020', initial_path='/'):
        super().__init__(parent)
        self.title("📁 HDFS Browser - Real Connection")
        self.geometry("900x650")
        self.hdfs_host = hdfs_host
        self.hdfs_port = hdfs_port
        self.current_path = initial_path
        self.selected_file = None
        self.file_map = {}
        
        self.transient(parent)
        self.grab_set()
        
        self._create_ui()
        self._load_directory(initial_path)
    
    def _create_ui(self):
        """Create UI"""
        # Header
        header = tk.Frame(self, bg='#24292F', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="📁 HDFS File Browser",
            bg='#24292F',
            fg='white',
            font=('Segoe UI', 14, 'bold')
        ).pack(side=tk.LEFT, padx=15, pady=15)
        
        # Connection info
        info_text = f"Connected to: hdfs://{self.hdfs_host}:{self.hdfs_port}"
        tk.Label(
            header,
            text=info_text,
            bg='#24292F',
            fg='#7EE787',
            font=('Consolas', 9)
        ).pack(side=tk.RIGHT, padx=15)
        
        # Path bar
        path_frame = tk.Frame(self, bg='white', relief=tk.SOLID, borderwidth=1)
        path_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            path_frame,
            text="📂",
            bg='white',
            font=('Segoe UI', 12)
        ).pack(side=tk.LEFT, padx=(10, 5), pady=8)
        
        self.path_var = tk.StringVar(value=self.current_path)
        path_entry = tk.Entry(
            path_frame,
            textvariable=self.path_var,
            font=('Consolas', 10),
            relief=tk.FLAT,
            bg='#F6F8FA'
        )
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=8)
        
        # Navigation buttons
        btn_frame = tk.Frame(path_frame, bg='white')
        btn_frame.pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="⟳ Refresh",
            command=self._refresh
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            btn_frame,
            text="↑ Up",
            command=self._go_up
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            btn_frame,
            text="🏠 Root",
            command=lambda: self._load_directory('/')
        ).pack(side=tk.LEFT, padx=2)
        
        # Tree view
        tree_frame = tk.Frame(self, bg='white', relief=tk.SOLID, borderwidth=1)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=('size', 'type', 'path'),
            show='tree headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        self.tree.heading('#0', text='Name', anchor='w')
        self.tree.heading('size', text='Size', anchor='e')
        self.tree.heading('type', text='Type', anchor='center')
        self.tree.heading('path', text='Full Path', anchor='w')
        
        self.tree.column('#0', width=300, minwidth=200)
        self.tree.column('size', width=100, minwidth=80, anchor='e')
        self.tree.column('type', width=80, minwidth=60, anchor='center')
        self.tree.column('path', width=400, minwidth=200)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        
        self.tree.bind('<Double-Button-1>', self._on_double_click)
        self.tree.bind('<Return>', self._on_return)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(
            self,
            textvariable=self.status_var,
            bg='#F6F8FA',
            fg='#57606A',
            font=('Segoe UI', 9),
            anchor='w',
            relief=tk.SUNKEN,
            borderwidth=1
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Action buttons
        btn_container = tk.Frame(self, bg='white')
        btn_container.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            btn_container,
            text="✅ Select File",
            command=self._select,
            bg='#0969DA',
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=25,
            pady=10
        ).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(
            btn_container,
            text="❌ Cancel",
            command=self._cancel,
            bg='#6E7781',
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=25,
            pady=10
        ).pack(side=tk.RIGHT)
    
    def _load_directory(self, path):
        """Load HDFS directory"""
        self.status_var.set(f"Loading {path}...")
        self.tree.delete(*self.tree.get_children())
        self.file_map.clear()
        self.current_path = path
        self.path_var.set(path)
        
        try:
            files = get_hdfs_files(path, self.hdfs_host, self.hdfs_port)
            
            if not files:
                self.status_var.set("No files found or connection error")
                # Show error in tree
                self.tree.insert('', 'end', text="⚠️ No files or connection error", values=('', '', ''))
                return
            
            # Sort: directories first, then files
            files.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
            
            for item in files:
                icon = "📁" if item['is_dir'] else "📄"
                name = f"{icon} {item['name']}"
                
                item_id = self.tree.insert(
                    '',
                    'end',
                    text=name,
                    values=(item['size'], item['type'], item['path'])
                )
                self.file_map[item_id] = item
            
            self.status_var.set(f"Loaded {len(files)} items from {path}")
        
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to load directory:\n{str(e)}")
    
    def _on_double_click(self, event):
        """Handle double click"""
        sel = self.tree.selection()
        if sel and sel[0] in self.file_map:
            item = self.file_map[sel[0]]
            if item['is_dir']:
                self._load_directory(item['path'])
            else:
                self.selected_file = f"hdfs://{self.hdfs_host}:{self.hdfs_port}{item['path']}"
                self.destroy()
    
    def _on_return(self, event):
        """Handle Enter key"""
        self._select()
    
    def _select(self):
        """Select file"""
        sel = self.tree.selection()
        if sel and sel[0] in self.file_map:
            item = self.file_map[sel[0]]
            if item['is_dir']:
                self._load_directory(item['path'])
            else:
                self.selected_file = f"hdfs://{self.hdfs_host}:{self.hdfs_port}{item['path']}"
                self.destroy()
        else:
            messagebox.showwarning("No Selection", "Please select a file")
    
    def _cancel(self):
        """Cancel"""
        self.selected_file = None
        self.destroy()
    
    def _refresh(self):
        """Refresh current directory"""
        self._load_directory(self.current_path)
    
    def _go_up(self):
        """Go to parent directory"""
        if self.current_path != '/':
            parent = os.path.dirname(self.current_path) or '/'
            self._load_directory(parent)


# ============================================================================
# ADVANCED AI TAB V8.3 - OPTIMIZED
# ============================================================================

class AdvancedAITabV8Optimized:
    """Advanced AI Tab V8.3 - Optimized for PySpark"""
    
    def __init__(self, parent, config_manager=None):
        self.parent = parent
        self.config_manager = config_manager
        self.config = config_manager.config if config_manager else {}
        
        self.ai_engine = None
        self.last_generated_code = ""  # Store clean code
        
        # Variables
        self.provider_var = tk.StringVar(value="Gemini 2.5 Flash (Free)")
        self.api_key_var = tk.StringVar()
        self.hdfs_file_var = tk.StringVar()
        self.question_var = tk.StringVar()
        
        self._create_ui()
        self._load_config()
    
    def _create_ui(self):
        """Create optimized UI"""
        main = tk.Frame(self.parent, bg='#F6F8FA')
        main.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = tk.Frame(main, bg='#24292F', height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg='#24292F')
        header_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        tk.Label(
            header_content,
            text="🤖 AI API",
            bg='#24292F',
            fg='white',
            font=('Segoe UI', 16, 'bold')
        ).pack(side=tk.LEFT)
        
        tk.Label(
            header_content,
            text="PySpark Code Generator | Temperature 0.0",
            bg='#24292F',
            fg='#7EE787',
            font=('Segoe UI', 10, 'italic')
        ).pack(side=tk.LEFT, padx=(15, 0))
        
        self.status_label = tk.Label(
            header_content,
            text="⚪ Not Initialized",
            bg='#24292F',
            fg='#7EE787',
            font=('Segoe UI', 9)
        )
        self.status_label.pack(side=tk.RIGHT)
        
        # Main content (2 columns)
        content = tk.Frame(main, bg='#F6F8FA')
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # LEFT: Configuration
        left = tk.Frame(content, bg='white', relief=tk.SOLID, borderwidth=1)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 5), ipadx=10, ipady=10)
        left.configure(width=400)
        
        self._create_config_section(left)
        
        # RIGHT: Input/Output
        right = tk.Frame(content, bg='white', relief=tk.SOLID, borderwidth=1)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self._create_io_section(right)
    
    def _create_config_section(self, parent):
        """Create configuration section"""
        # Title
        tk.Label(
            parent,
            text="⚙️ Configuration",
            bg='white',
            fg='#24292F',
            font=('Segoe UI', 12, 'bold')
        ).pack(anchor='w', padx=15, pady=(15, 10))
        
        # Provider
        tk.Label(
            parent,
            text="AI Provider:",
            bg='white',
            fg='#57606A',
            font=('Segoe UI', 9, 'bold')
        ).pack(anchor='w', padx=15, pady=(5, 2))
        
        ttk.Combobox(
            parent,
            textvariable=self.provider_var,
            values=[
                "Gemini 2.5 Flash (Free)",
                "Claude 3.5 Haiku",
                "GPT-4o Mini"
            ],
            state='readonly',
            font=('Segoe UI', 9)
        ).pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # API Key (optional)
        tk.Label(
            parent,
            text="API Key (optional for Gemini):",
            bg='white',
            fg='#57606A',
            font=('Segoe UI', 9, 'bold')
        ).pack(anchor='w', padx=15, pady=(5, 2))
        
        tk.Entry(
            parent,
            textvariable=self.api_key_var,
            show='*',
            font=('Consolas', 9),
            relief=tk.SOLID,
            borderwidth=1
        ).pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # Temperature control
        tk.Label(
            parent,
            text="Temperature (0.0 = code only, 1.0 = creative):",
            bg='white',
            fg='#57606A',
            font=('Segoe UI', 9, 'bold')
        ).pack(anchor='w', padx=15, pady=(5, 2))
        
        temp_frame = tk.Frame(parent, bg='white')
        temp_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # Temperature slider
        self.temp_var = tk.DoubleVar(value=0.0)
        temp_slider = tk.Scale(
            temp_frame,
            variable=self.temp_var,
            from_=0.0,
            to=1.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            bg='white',
            fg='#24292F',
            highlightthickness=0,
            font=('Segoe UI', 8),
            length=200
        )
        temp_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Temperature value display
        self.temp_label = tk.Label(
            temp_frame,
            textvariable=self.temp_var,
            bg='#F6F8FA',
            fg='#24292F',
            font=('Consolas', 9, 'bold'),
            width=4,
            relief=tk.SOLID,
            borderwidth=1
        )
        self.temp_label.pack(side=tk.LEFT)
        
        # Initialize button
        tk.Button(
            parent,
            text="🚀 Initialize Engine",
            command=self._initialize_engine,
            bg='#0969DA',
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            pady=10
        ).pack(fill=tk.X, padx=15, pady=10)
        
        # Separator
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, padx=15, pady=15)
        
        # HDFS Configuration
        tk.Label(
            parent,
            text="📁 HDFS File Selection",
            bg='white',
            fg='#24292F',
            font=('Segoe UI', 12, 'bold')
        ).pack(anchor='w', padx=15, pady=(5, 10))
        
        tk.Label(
            parent,
            text="Selected File:",
            bg='white',
            fg='#57606A',
            font=('Segoe UI', 9, 'bold')
        ).pack(anchor='w', padx=15, pady=(5, 2))
        
        file_frame = tk.Frame(parent, bg='white')
        file_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        tk.Entry(
            file_frame,
            textvariable=self.hdfs_file_var,
            font=('Consolas', 9),
            relief=tk.SOLID,
            borderwidth=1,
            state='readonly'
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        tk.Button(
            file_frame,
            text="📂 Browse",
            command=self._browse_hdfs,
            bg='#6E7781',
            fg='white',
            font=('Segoe UI', 9, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=5
        ).pack(side=tk.LEFT)
        
        # Info
        info_frame = tk.Frame(parent, bg='#DDF4FF', relief=tk.SOLID, borderwidth=1)
        info_frame.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(
            info_frame,
            text="💡 Tips:",
            bg='#DDF4FF',
            fg='#0969DA',
            font=('Segoe UI', 9, 'bold')
        ).pack(anchor='w', padx=10, pady=(8, 5))
        
        tips = [
            "• Browse HDFS để chọn file",
            "• AI sẽ tạo PySpark code",
            "• Temperature: 0.0=code only, 1.0=creative",
            "• Click 'Run Code' để tự động chạy"
        ]
        
        for tip in tips:
            tk.Label(
                info_frame,
                text=tip,
                bg='#DDF4FF',
                fg='#57606A',
                font=('Segoe UI', 8),
                justify='left'
            ).pack(anchor='w', padx=10, pady=2)
        
        tk.Label(
            info_frame,
            text="",
            bg='#DDF4FF'
        ).pack(pady=5)
    
    def _create_io_section(self, parent):
        """Create input/output section - COMPACT VERSION"""
        # Question input - COMPACT (no examples box)
        input_frame = tk.Frame(parent, bg='white')
        input_frame.pack(fill=tk.X, padx=15, pady=(10, 5))  # Reduced padding
        
        # Question input and button in ONE row
        question_row = tk.Frame(input_frame, bg='white')
        question_row.pack(fill=tk.X)
        
        tk.Entry(
            question_row,
            textvariable=self.question_var,
            font=('Segoe UI', 10),
            relief=tk.SOLID,
            borderwidth=1
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        tk.Button(
            question_row,
            text="🚀 Generate",
            command=self._generate_code,
            bg='#2DA44E',
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=8
        ).pack(side=tk.LEFT)
        
        # Output - MORE SPACE
        output_frame = tk.Frame(parent, bg='white')
        output_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5, 15))  # Reduced top padding
        
        tk.Label(
            output_frame,
            text="📄 Generated Code:",
            bg='white',
            fg='#24292F',
            font=('Segoe UI', 11, 'bold')
        ).pack(anchor='w', pady=(0, 8))
        
        # Output container with FIXED height to ensure buttons are visible
        output_container = tk.Frame(output_frame, bg='#0D1117', relief=tk.SOLID, borderwidth=1)
        output_container.pack(fill=tk.BOTH, expand=True)
        
        self.output_text = scrolledtext.ScrolledText(
            output_container,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg='#0D1117',
            fg='#C9D1D9',
            insertbackground='white',
            relief=tk.FLAT,
            padx=10,
            pady=10,
            height=25  # INCREASED from 20 to 25 (more space now)
        )
        self.output_text.pack(fill=tk.BOTH, expand=False)  # expand=False to prevent overflow
        
        # Action buttons - ALWAYS VISIBLE
        btn_frame = tk.Frame(output_frame, bg='white')
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(
            btn_frame,
            text="📋 Copy Code",
            command=self._copy_code,
            bg='#6E7781',
            fg='white',
            font=('Segoe UI', 9, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(
            btn_frame,
            text="💾 Save to File",
            command=self._save_code,
            bg='#6E7781',
            fg='white',
            font=('Segoe UI', 9, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="▶️ Run Code",
            command=self._run_code,
            bg='#0969DA',
            fg='white',
            font=('Segoe UI', 9, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="🗑️ Clear",
            command=lambda: self.output_text.delete('1.0', tk.END),
            bg='#CF222E',
            fg='white',
            font=('Segoe UI', 9, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=8
        ).pack(side=tk.RIGHT)
    
    def _browse_hdfs(self):
        """Browse HDFS files"""
        browser = HDFSBrowser(
            self.parent,
            hdfs_host=self.config.get('namenode_host', 'namenode'),
            hdfs_port=self.config.get('namenode_port', '8020')
        )
        
        self.parent.wait_window(browser)
        
        if browser.selected_file:
            self.hdfs_file_var.set(browser.selected_file)
    
    def _initialize_engine(self):
        """Initialize AI Engine"""
        if not AI_ENGINE_AVAILABLE:
            messagebox.showerror("Error", "AI Engine V8.3 not available!\n\nInstall: pip install google-generativeai")
            return
        
        try:
            self.status_label.config(text="⏳ Initializing...")
            
            # Fixed provider mapping
            provider_map = {
                "Gemini 2.5 Flash (Free)": AIProvider.GOOGLE_GEMINI_25_FLASH,
                "Claude 3.5 Haiku": AIProvider.ANTHROPIC_CLAUDE_3_HAIKU,
                "GPT-4o Mini": AIProvider.OPENAI_GPT4O  # Use GPT4O, not GPT4O_MINI
            }
            
            provider = provider_map.get(self.provider_var.get(), AIProvider.GOOGLE_GEMINI_25_FLASH)
            
            # Log for debugging
            print(f"🔧 Selected: {self.provider_var.get()}")
            print(f"🔧 Mapped to: {provider}")
            
            # Save API key to config
            api_key = self.api_key_var.get().strip()
            if api_key and self.config_manager:
                self.config_manager.config['ai_api_key'] = api_key
                self.config_manager.config['ai_provider'] = self.provider_var.get()
                self.config_manager.save_config()
                print(f"💾 API key saved to config")
            
            # Get temperature from slider
            temperature = self.temp_var.get()
            
            # V8.3 Config with adjustable temperature
            config = AIConfig(
                provider=provider,
                api_key=api_key or None,
                temperature=temperature,  # User-adjustable
                max_tokens=2048,  # V8.3: Limited for conciseness
                enable_quality_check=True,
                min_quality_score=0.7
            )
            
            self.ai_engine = AdvancedAIEngine(config)
            
            self.status_label.config(text="✅ Engine Ready")
            messagebox.showinfo(
                "Success", 
                f"AI Engine V8.3 initialized!\n\nProvider: {provider.value}\nTemperature: {temperature}\nAPI Key: {'Saved ✅' if api_key else 'Not provided'}"
            )
            
        except Exception as e:
            self.status_label.config(text="❌ Error")
            print(f"❌ Error details: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to initialize:\n{str(e)}")
    
    def _extract_python_code(self, text):
        """Extract only Python code from response (remove verbose explanations)"""
        import re
        
        # Method 1: Extract from code blocks
        code_blocks = re.findall(r'```(?:python)?\n(.*?)```', text, re.DOTALL)
        if code_blocks:
            # Return all code blocks joined
            return '\n\n'.join(block.strip() for block in code_blocks)
        
        # Method 2: If no code blocks, try to find Python-like code
        lines = text.split('\n')
        code_lines = []
        in_code = False
        
        for line in lines:
            # Start of code (imports, def, class, etc.)
            if re.match(r'^(import |from |def |class |if |for |while |with |@)', line.strip()):
                in_code = True
            
            # Skip verbose lines
            if in_code and not line.strip().startswith(('#', '//', '**', '*', '<!--')):
                code_lines.append(line)
            
            # Stop at markdown headers or long explanations
            if line.startswith('##') or line.startswith('**Note'):
                in_code = False
        
        if code_lines:
            return '\n'.join(code_lines).strip()
        
        # Method 3: Return original if can't extract
        return text.strip()
    
    def _generate_code(self):
        """Generate PySpark code"""
        if not self.ai_engine:
            messagebox.showwarning("Warning", "Please initialize AI Engine first!")
            return
        
        question = self.question_var.get().strip()
        if not question:
            messagebox.showwarning("Warning", "Please enter a question!")
            return
        
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert('1.0', "⏳ Generating code...\n\n")
        
        def run():
            try:
                # Build context with HDFS file if selected
                context = ""
                if self.hdfs_file_var.get():
                    context = f"HDFS File: {self.hdfs_file_var.get()}\n"
                
                # Run async code generation
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.ai_engine.analyze_data(context, question)
                )
                loop.close()
                
                # Display result
                self.output_text.delete('1.0', tk.END)
                
                if result.success:
                    # Extract ONLY Python code (no verbose text)
                    python_code = self._extract_python_code(result.response)
                    
                    # Store clean code for later use
                    self.last_generated_code = python_code
                    
                    # Display code
                    self.output_text.insert('1.0', python_code)
                    
                    # Stats (optional - can be hidden)
                    stats = f"\n\n{'='*70}\n"
                    stats += f"⏱️  Time: {result.processing_time:.2f}s | "
                    stats += f"🎯 Quality: {result.quality_score:.0%} | "
                    stats += f"💰 Cost: ${result.cost:.4f}\n"
                    stats += f"🤖 Provider: {result.provider_used}\n"
                    stats += f"{'='*70}"
                    
                    # Comment out to hide stats
                    # self.output_text.insert(tk.END, stats)
                else:
                    self.output_text.insert('1.0', f"❌ Error: {result.error}")
            
            except Exception as e:
                self.output_text.delete('1.0', tk.END)
                self.output_text.insert('1.0', f"❌ Exception: {str(e)}")
        
        threading.Thread(target=run, daemon=True).start()
    
    def _copy_code(self):
        """Copy ONLY clean code to clipboard (no stats)"""
        if self.last_generated_code:
            code = self.last_generated_code
        else:
            # Fallback: get from text widget and remove stats
            code = self.output_text.get('1.0', tk.END).strip()
            # Remove stats footer
            if '=' * 70 in code:
                code = code.split('=' * 70)[0].strip()
        
        self.parent.clipboard_clear()
        self.parent.clipboard_append(code)
        messagebox.showinfo("Success", "✅ Code copied to clipboard!\n\n(Stats không được copy)")
    
    def _save_code(self):
        """Save ONLY clean code to file (no stats)"""
        if self.last_generated_code:
            code = self.last_generated_code
        else:
            # Fallback: get from text widget and remove stats
            code = self.output_text.get('1.0', tk.END).strip()
            # Remove stats footer
            if '=' * 70 in code:
                code = code.split('=' * 70)[0].strip()
        
        if not code:
            messagebox.showwarning("Warning", "No code to save!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")],
            initialfile="generated_pyspark_code.py"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(code)
                messagebox.showinfo("Success", f"✅ Code saved to:\n{filename}\n\n(Stats không được lưu)")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save:\n{str(e)}")
    
    def _run_code(self):
        """Run ONLY clean code - Integrated with Spark Runner"""
        if self.last_generated_code:
            code = self.last_generated_code
        else:
            # Fallback: get from text widget and remove stats
            code = self.output_text.get('1.0', tk.END).strip()
            # Remove stats footer
            if '=' * 70 in code:
                code = code.split('=' * 70)[0].strip()
        
        if not code:
            messagebox.showwarning("Warning", "No code to run!")
            return
        
        # Ask where to save
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")],
            initialfile="ai_generated_code.py",
            title="💾 Save PySpark Code to Run in Spark Runner"
        )
        
        if not filename:
            return  # User cancelled
        
        # Save code to file
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(code)
            print(f"✅ Code saved to: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save code:\n{str(e)}")
            return
        
        # Try to integrate with Spark Runner tab
        try:
            # Check if Spark Runner tab reference exists
            if hasattr(self, 'spark_runner_tab') and self.spark_runner_tab:
                spark_tab = self.spark_runner_tab
                
                # Set file path in Spark Runner (correct variable name: file_var)
                if hasattr(spark_tab, 'file_var'):
                    spark_tab.file_var.set(filename)
                    print(f"✅ File path set in Spark Runner: {filename}")
                else:
                    print(f"⚠️ file_var not found in Spark Runner")
                
                # Switch to Spark Runner tab
                if hasattr(self, 'main_notebook') and self.main_notebook:
                    # Find Spark Runner tab index
                    for i in range(self.main_notebook.index('end')):
                        tab_text = self.main_notebook.tab(i, 'text').lower()
                        if 'spark runner' in tab_text or 'spark job' in tab_text:
                            self.main_notebook.select(i)
                            print(f"✅ Switched to Spark Runner tab (index {i})")
                            break
                
                # Auto-click Run button after a short delay
                def auto_run():
                    import time
                    time.sleep(0.8)  # Wait for UI to update
                    
                    # Try multiple methods to trigger run
                    if hasattr(spark_tab, 'on_auto_run'):
                        spark_tab.on_auto_run()
                        print(f"✅ Auto-running Spark job via on_auto_run()")
                    elif hasattr(spark_tab, 'quick_run_btn'):
                        spark_tab.quick_run_btn.invoke()
                        print(f"✅ Auto-clicked quick_run_btn")
                    else:
                        print(f"⚠️ No run method found, user needs to click Run manually")
                
                import threading
                threading.Thread(target=auto_run, daemon=True).start()
                
                messagebox.showinfo(
                    "✅ Running in Spark Runner",
                    f"Code saved and executing!\n\n"
                    f"📁 File: {os.path.basename(filename)}\n\n"
                    f"Check 'Spark Runner' tab for execution log."
                )
            else:
                # Fallback: Manual instruction
                messagebox.showinfo(
                    "Code Saved",
                    f"✅ Code saved to:\n{filename}\n\n"
                    f"📌 Next steps:\n"
                    f"1. Go to 'Spark Runner' tab\n"
                    f"2. Browse to file: {os.path.basename(filename)}\n"
                    f"3. Click '▶️ Run'"
                )
        
        except Exception as e:
            print(f"⚠️ Integration error: {e}")
            import traceback
            traceback.print_exc()
            # Fallback message
            messagebox.showinfo(
                "Code Saved",
                f"✅ Code saved to:\n{filename}\n\n"
                f"Go to 'Spark Runner' tab to run it."
            )
    
    def _load_config(self):
        """Load saved configuration (API key, provider)"""
        if self.config:
            # Load saved API key
            saved_key = self.config.get('ai_api_key', '') or self.config.get('gemini_api_key', '')
            if saved_key:
                self.api_key_var.set(saved_key)
                print(f"✅ Loaded saved API key")
            
            # Load saved provider
            saved_provider = self.config.get('ai_provider', '')
            if saved_provider:
                self.provider_var.set(saved_provider)
                print(f"✅ Loaded saved provider: {saved_provider}")


# Alias for compatibility
AdvancedAITabV8 = AdvancedAITabV8Optimized
