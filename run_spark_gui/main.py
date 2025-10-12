import tkinter as tk
from tkinter import ttk, Menu
import os
import json
import sys
import atexit
import signal
import re
from pathlib import Path
from datetime import datetime
from hdfs_upload_tab import HDFSUploadTab
from ai_code_generator_tab import AICodeGeneratorTab
from theme import setup_theme, COLORS
from spark_runner_tab import SparkRunnerTab

APP_TITLE = "🚀 Spark Runner GUI - Pro Edition"
CONFIG_FILE = "spark_runner_config.json"
VERSION = "2.4.2"

INFO_TEXT = (
    "💡 Ctrl+O: Mở file | Ctrl+R: Chạy | F5: Generate | F1: Trợ giúp | Esc: Dừng\n"
    "Lịch sử và cấu hình được lưu tự động. Hover chuột lên nút để xem hướng dẫn chi tiết."
)


def validate_config(config):
    """
    Validate configuration values and fix invalid ones
    Returns validated config with corrections logged
    """
    validated = config.copy()
    errors = []
    
    # Validate container name (Docker naming rules)
    container_pattern = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_.-]*$')
    if not container_pattern.match(config.get('container', '')):
        errors.append(f"Invalid container name: '{config.get('container')}'. Using default 'spark-worker'")
        validated['container'] = 'spark-worker'
    
    # Validate master URL
    master = config.get('master', '')
    if not (master.startswith('spark://') or master.startswith('local') or master.startswith('yarn')):
        errors.append(f"Invalid master URL: '{master}'. Using default 'spark://spark-master:7077'")
        validated['master'] = 'spark://spark-master:7077'
    
    # Validate HDFS host
    hdfs_host = config.get('hdfs_host', '')
    if not hdfs_host.startswith('hdfs://'):
        errors.append(f"Invalid HDFS host: '{hdfs_host}'. Using default 'hdfs://namenode:8020'")
        validated['hdfs_host'] = 'hdfs://namenode:8020'
    
    # Validate HDFS path (must start with /)
    hdfs_path = config.get('hdfs_default_path', '')
    if not hdfs_path.startswith('/'):
        errors.append(f"Invalid HDFS path: '{hdfs_path}'. Using default '/user/spark/data'")
        validated['hdfs_default_path'] = '/user/spark/data'
    
    # Validate boolean flags
    for key in ['auto_extract_archives', 'delete_archive_after_extract']:
        if not isinstance(config.get(key), bool):
            errors.append(f"Invalid {key}: '{config.get(key)}'. Using default True")
            validated[key] = True
    
    # Log errors if any
    if errors:
        print("⚠️ Configuration validation errors:")
        for error in errors:
            print(f"  - {error}")
    
    return validated


def load_config():
    """Load configuration from JSON file"""
    # Get absolute path to docker-compose.yml in the same directory as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_compose_file = os.path.join(script_dir, 'docker-compose.yml')
    
    default = {
        'container': 'spark-worker',
        'master': 'spark://spark-master:7077',
        'hdfs_container': 'namenode',
        'hdfs_host': 'hdfs://namenode:8020',
        'hdfs_default_path': '/user/spark/data',
        'auto_extract_archives': True,
        'delete_archive_after_extract': True,
        'compose_file': default_compose_file,
        'history': []
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Add new keys if not exist
                if 'hdfs_container' not in config:
                    config['hdfs_container'] = default['hdfs_container']
                if 'hdfs_host' not in config:
                    config['hdfs_host'] = default['hdfs_host']
                if 'hdfs_default_path' not in config:
                    config['hdfs_default_path'] = default['hdfs_default_path']
                if 'auto_extract_archives' not in config:
                    config['auto_extract_archives'] = default['auto_extract_archives']
                if 'delete_archive_after_extract' not in config:
                    config['delete_archive_after_extract'] = default['delete_archive_after_extract']
                if 'compose_file' not in config:
                    config['compose_file'] = default_compose_file
                
                # Validate config before returning
                config = validate_config(config)
                return config
        except Exception as e:
            print(f"Failed to load config: {e}, using defaults")
            return validate_config(default)
    return validate_config(default)


def save_config(config):
    """Save configuration to JSON file"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Failed to save config: {e}")


def add_to_history(config, filepath):
    """Add file to history (max 10 entries)"""
    if filepath not in config['history']:
        config['history'].insert(0, filepath)
        config['history'] = config['history'][:10]  # Keep only last 10
        save_config(config)

class App:
    def __init__(self, root):
        self.root = root
        self.config = load_config()
        self.is_running = False
        
        root.title(APP_TITLE)
        root.geometry('1200x800')
        root.minsize(1100, 700)
        
        # Register cleanup handlers
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        setup_theme(root)
        
        # Setup menu bar
        self.create_menu()
        
        # Main container
        main_frame = ttk.Frame(root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Info label with better styling
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_lbl = ttk.Label(info_frame, text=INFO_TEXT, foreground='#555', 
                            font=('Segoe UI', 9), wraplength=950)
        info_lbl.pack(fill=tk.X)
        
        # === Notebook with Tabs ===
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        
        # Tab 1: Spark Runner
        self.spark_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.spark_tab, text='🚀 Spark Runner')
        
        # Tab 2: HDFS Upload
        self.hdfs_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.hdfs_tab, text='📤 HDFS Upload')
        
        # Tab 3: AI Code Generator
        self.ai_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.ai_tab, text='🤖 AI Code Generator')

        # Status bar
        self.status_var = tk.StringVar(value="✅ Ready")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, font=('Segoe UI', 8))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initialize Spark Runner Tab
        self.spark_runner = SparkRunnerTab(
            parent_frame=self.spark_tab,
            config=self.config,
            theme=COLORS,
            callbacks={
                'update_status': self.update_status,
                'append_log': self.append_log,
                'add_to_history': add_to_history,
                'save_config': save_config,
                'load_config': load_config,
                'get_version': lambda: VERSION,
            }
        )
        self.spark_runner.root = root # Pass root for dialogs/clipboard
        
        # Start log processor after root is set
        self.spark_runner._start_log_processor()
        
        # Initialize other tabs
        self.hdfs_upload = HDFSUploadTab(
            parent_frame=self.hdfs_tab,
            config=self.config,
            status_callback=self.update_status,
            log_callback=self.append_log
        )
        
        self.ai_generator = AICodeGeneratorTab(
            parent_frame=self.ai_tab,
            config=self.config,
            status_callback=self.update_status,
            log_callback=self.append_log
        )
        
        self.setup_shortcuts()

        # Welcome message
        self.append_log('🎉 Chào mừng đến với Spark Runner GUI!', 'header', self.spark_runner.log_text_widget)
        self.append_log('💡 Nhấn F1 để xem trợ giúp, Ctrl+O để mở file, Ctrl+R để chạy', 'info', self.spark_runner.log_text_widget)
        
        # Auto-check Docker status on startup (silent mode - no logs)
        self.root.after(1000, lambda: self.spark_runner.docker_status(silent=True))

        # Initialize file history
        if self.config['history']:
            self.spark_runner.file_var.set(self.config['history'][0])
            self.spark_runner.on_generate()

    def create_menu(self):
        """Create menu bar"""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label='File', menu=file_menu)
        file_menu.add_command(label='Mở file... (Ctrl+O)', command=lambda: self.spark_runner.on_browse(), accelerator='Ctrl+O')
        file_menu.add_command(label='Làm mới lịch sử', command=lambda: self.spark_runner.refresh_history())
        file_menu.add_separator()
        file_menu.add_command(label='Export Log... (Ctrl+S)', command=lambda: self.spark_runner.export_log(), accelerator='Ctrl+S')
        file_menu.add_separator()
        file_menu.add_command(label='Thoát (Alt+F4)', command=self.root.quit)
        
        # Edit menu
        edit_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Edit', menu=edit_menu)
        edit_menu.add_command(label='Copy Commands (Ctrl+C)', command=lambda: self.spark_runner.on_copy(), accelerator='Ctrl+C')
        edit_menu.add_command(label='Clear Log (Ctrl+L)', command=lambda: self.spark_runner.clear_log(), accelerator='Ctrl+L')
        edit_menu.add_separator()
        edit_menu.add_command(label='Clear File', command=lambda: self.spark_runner.clear_file())
        edit_menu.add_command(label='Clear History', command=lambda: self.spark_runner.clear_history())
        
        # Run menu
        run_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Run', menu=run_menu)
        run_menu.add_command(label='Generate Commands (F5)', command=lambda: self.spark_runner.on_generate(), accelerator='F5')
        run_menu.add_command(label='Auto Run All (Ctrl+R)', command=lambda: self.spark_runner.on_auto_run(), accelerator='Ctrl+R')
        run_menu.add_separator()
        run_menu.add_command(label='Step 1: Copy File', command=lambda: self.spark_runner.on_step1())
        run_menu.add_command(label='Step 2: Open Bash', command=lambda: self.spark_runner.on_step2())
        run_menu.add_command(label='Step 3: Run Spark', command=lambda: self.spark_runner.on_step3())
        run_menu.add_separator()
        run_menu.add_command(label='Stop (Esc)', command=lambda: self.spark_runner.on_stop(), accelerator='Esc')
        
        # Settings menu
        settings_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Settings', menu=settings_menu)
        settings_menu.add_command(label='Lưu cấu hình hiện tại', command=lambda: self.spark_runner.on_save_config())
        settings_menu.add_command(label='Reset về mặc định', command=lambda: self.spark_runner.reset_config())
        
        # Help menu
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Help', menu=help_menu)
        help_menu.add_command(label='Hướng dẫn (F1)', command=lambda: self.spark_runner.show_help(), accelerator='F1')
        help_menu.add_command(label='Keyboard Shortcuts', command=lambda: self.spark_runner.show_shortcuts())
        help_menu.add_separator()
        help_menu.add_command(label='About', command=lambda: self.spark_runner.show_about())
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.root.bind('<Control-o>', lambda e: self.spark_runner.on_browse())
        self.root.bind('<Control-O>', lambda e: self.spark_runner.on_browse())
        self.root.bind('<Control-r>', lambda e: self.spark_runner.on_auto_run())
        self.root.bind('<Control-R>', lambda e: self.spark_runner.on_auto_run())
        self.root.bind('<F5>', lambda e: self.spark_runner.on_generate())
        self.root.bind('<Control-s>', lambda e: self.spark_runner.export_log())
        self.root.bind('<Control-S>', lambda e: self.spark_runner.export_log())
        self.root.bind('<Control-l>', lambda e: self.spark_runner.clear_log())
        self.root.bind('<Control-L>', lambda e: self.spark_runner.clear_log())
        self.root.bind('<F1>', lambda e: self.spark_runner.show_help())
        self.root.bind('<Escape>', lambda e: self.spark_runner.on_stop())

    def update_status(self, message):
        """Update status bar message"""
        self.status_var.set(message)

    def append_log(self, s: str, tag='normal', log_widget=None):
        """Append message to a specific log widget with color tag"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Determine tag based on content if not specified
        if tag == 'normal':
            if '✅' in s or 'thành công' in s.lower() or 'completed' in s.lower():
                tag = 'success'
            elif '❌' in s or 'error' in s.lower() or 'failed' in s.lower() or 'lỗi' in s.lower():
                tag = 'error'
            elif '⚠️' in s or 'warning' in s.lower() or 'cảnh báo' in s.lower():
                tag = 'warning'
            elif '💡' in s or '→' in s or 'info' in s.lower():
                tag = 'info'
        
        log_line = f'[{timestamp}] {s}\n'
        
        # If no specific log widget is provided, try to find the active one
        if log_widget is None:
            current_tab_index = self.notebook.index(self.notebook.select())
            if current_tab_index == 0:
                log_widget = self.spark_runner.log_text_widget
            elif current_tab_index == 1:
                log_widget = self.hdfs_upload.hdfs_log
            elif current_tab_index == 2:
                # AI tab logs to the main spark_runner log for now
                log_widget = self.spark_runner.log_text_widget
            else:
                return # No known log widget for this tab

        if log_widget:
            log_widget.insert(tk.END, log_line, tag)
            log_widget.see(tk.END)
            self.root.update_idletasks()

    def cleanup(self):
        """Clean up resources before exit"""
        try:
            print("Cleaning up resources...")
            if hasattr(self, 'spark_runner'):
                self.spark_runner.cleanup()
            if hasattr(self, 'hdfs_upload'):
                # Add cleanup if HDFSUploadTab has cleanup method
                pass
            if hasattr(self, 'ai_generator'):
                # Add cleanup if AICodeGeneratorTab has cleanup method
                pass
            print("Cleanup completed.")
        except Exception as e:
            print(f"Error during cleanup: {e}")

    def signal_handler(self, signum, frame):
        """Handle Ctrl+C and other signals"""
        print(f"\nReceived signal {signum}, shutting down gracefully...")
        self.cleanup()
        sys.exit(0)

    def on_closing(self):
        """Handle window close event"""
        from tkinter import messagebox
        if messagebox.askokcancel("Thoát", "Bạn có chắc chắn muốn thoát?"):
            self.cleanup()
            self.root.destroy()

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
