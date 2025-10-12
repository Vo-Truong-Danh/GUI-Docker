import tkinter as tk
from tkinter import ttk, Menu, scrolledtext
import os
import json
import sys
import atexit
import signal
import re
import subprocess
from pathlib import Path
from datetime import datetime

# Import V4 Clean Professional Design for all tabs
print("🔄 Loading Spark Runner Tab V4...")
from spark_runner_tab_v4_clean import SparkRunnerTabV4 as SparkRunnerTab
print("🔄 Loading HDFS Upload Tab V4...")
from hdfs_upload_tab_v4_clean import HDFSUploadTabV4Clean as HDFSUploadTab
print("🔄 Loading AI Code Generator Tab V4...")
from ai_code_generator_tab_v4_clean import AICodeGeneratorTabV4Clean as AICodeGeneratorTab
print("🔄 Loading Performance Monitor V4...")
from performance_monitor_v4_clean import PerformanceMonitorV4Clean as PerformanceMonitor
print("🔄 Loading Docker Compose Editor V4...")
from docker_compose_editor_v4 import DockerComposeEditorV4
print("🔄 Loading Settings Tab V4...")
from settings_tab_v4 import SettingsTabV4
print("✅ Using Clean Professional UI V4 (all tabs)")
from modern_theme import setup_modern_theme, ModernTheme, Typography, Spacing, LightTheme

APP_TITLE = "Spark Runner GUI V4.1"
CONFIG_FILE = "spark_runner_config.json"
VERSION = "4.1.0"  # Complete UI redesign with Material Design 3

INFO_TEXT = ""  # Removed to save space


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
        self.auto_save_enabled = True
        self.last_save_time = datetime.now()
        
        root.title(APP_TITLE)
        root.geometry('1280x850')  # Increased size for better visibility
        root.minsize(1150, 750)
        
        # Center window on screen
        self.center_window(root)
        
        # Register cleanup handlers
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Setup modern theme
        self.theme = setup_modern_theme(root, mode='light')
        
        # Setup menu bar
        self.create_menu()
        
        # Main container with modern styling (no padding top for more space)
        main_frame = ttk.Frame(root, padding=(Spacing.LG, 0, Spacing.LG, Spacing.LG))
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # === Notebook with Tabs (Direct - No Header) ===
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(8, 8))
        
        # Tab 1: Spark Runner
        self.spark_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.spark_tab, text='🚀 Spark Runner')
        
        # Tab 2: HDFS Upload
        self.hdfs_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.hdfs_tab, text='📤 HDFS Upload')
        
        # Tab 3: AI Code Generator
        self.ai_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.ai_tab, text='🤖 AI Code Generator')
        
        # Tab 4: Performance Monitor
        self.perf_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.perf_tab, text='📊 Performance Monitor')
        
        # Tab 5: Docker Compose Editor
        self.compose_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.compose_tab, text='🐳 Docker Compose')
        
        # Tab 6: Settings
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text='⚙️ Settings')

        # Enhanced Status bar with multiple sections
        status_frame = tk.Frame(root, bg='#F0F0F0', relief=tk.SUNKEN, borderwidth=1)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Status message (left)
        self.status_var = tk.StringVar(value="✅ Ready")
        status_label = tk.Label(
            status_frame, 
            textvariable=self.status_var,
            bg='#F0F0F0', fg='#24292F',
            font=('Segoe UI', 8),
            anchor=tk.W,
            padx=8, pady=2
        )
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Separator
        ttk.Separator(status_frame, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=2)
        
        # Docker status (middle-left)
        self.docker_status_var = tk.StringVar(value="🐳 Docker: Checking...")
        docker_status_label = tk.Label(
            status_frame,
            textvariable=self.docker_status_var,
            bg='#F0F0F0', fg='#0969DA',
            font=('Segoe UI', 8, 'bold'),
            padx=8, pady=2
        )
        docker_status_label.pack(side=tk.LEFT)
        
        # Separator
        ttk.Separator(status_frame, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=2)
        
        # Active tab indicator (middle-right)
        self.active_tab_var = tk.StringVar(value="📑 Tab: Spark Runner")
        tab_label = tk.Label(
            status_frame,
            textvariable=self.active_tab_var,
            bg='#F0F0F0', fg='#57606A',
            font=('Segoe UI', 8),
            padx=8, pady=2
        )
        tab_label.pack(side=tk.LEFT)
        
        # Separator
        ttk.Separator(status_frame, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=2)
        
        # Time indicator (right)
        self.time_var = tk.StringVar(value=datetime.now().strftime("%H:%M:%S"))
        time_label = tk.Label(
            status_frame,
            textvariable=self.time_var,
            bg='#F0F0F0', fg='#57606A',
            font=('Segoe UI', 8),
            padx=8, pady=2
        )
        time_label.pack(side=tk.RIGHT)
        
        # Separator
        ttk.Separator(status_frame, orient='vertical').pack(side=tk.RIGHT, fill=tk.Y, padx=2)
        
        # Version info (right)
        version_label = tk.Label(
            status_frame,
            text=f"v{VERSION}",
            bg='#F0F0F0', fg='#57606A',
            font=('Segoe UI', 8),
            padx=8, pady=2
        )
        version_label.pack(side=tk.RIGHT)
        
        # Update time every second
        def update_time():
            self.time_var.set(datetime.now().strftime("%H:%M:%S"))
            root.after(1000, update_time)
        update_time()
        
        # Track active tab changes
        def on_tab_changed(event):
            tab_names = ['Spark Runner', 'HDFS Upload', 'AI Code Generator', 
                        'Performance Monitor', 'Docker Compose']
            current_tab = self.notebook.index(self.notebook.select())
            if current_tab < len(tab_names):
                self.active_tab_var.set(f"📑 Tab: {tab_names[current_tab]}")
        
        self.notebook.bind('<<NotebookTabChanged>>', on_tab_changed)
        
        # Initialize Spark Runner Tab
        # Create theme dictionary for backward compatibility
        theme_dict = {
            # Background colors
            'bg_light': '#FFFFFF',
            'bg_primary': LightTheme.BG_PRIMARY,
            'bg_secondary': LightTheme.BG_SECONDARY,
            'bg_cmd': '#1E1E1E',  # Dark background for command output
            'bg_log': '#F5F5F5',  # Light gray for log output
            
            # Text colors
            'text': LightTheme.TEXT_PRIMARY,
            'text_primary': LightTheme.TEXT_PRIMARY,
            'text_secondary': LightTheme.TEXT_SECONDARY,
            
            # Brand colors
            'primary': LightTheme.PRIMARY,
            'success': LightTheme.SUCCESS,
            'error': LightTheme.ERROR,
            'warning': '#FF9800',  # Orange for warnings
            
            # Border colors
            'border': LightTheme.BORDER,
        }
        
        self.spark_runner = SparkRunnerTab(
            parent_frame=self.spark_tab,
            config=self.config,
            theme=theme_dict,  # Pass theme as dictionary
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
        self.spark_runner.app_instance = self  # Pass app instance for callbacks
        
        # Note: _start_log_processor() is already called in SparkRunnerTabV4.__init__
        
        # Start auto-save timer
        self.start_auto_save_timer()
        
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
        
        self.perf_monitor = PerformanceMonitor(
            parent_frame=self.perf_tab,
            config=self.config,
            status_callback=self.update_status,
            log_callback=self.append_log
        )
        
        # Initialize Docker Compose Editor with error handling
        try:
            print("🔄 Initializing Docker Compose Editor...")
            self.compose_editor = DockerComposeEditorV4(
                parent_frame=self.compose_tab,
                config=self.config,
                status_callback=self.update_status,
                log_callback=self.append_log
            )
            print("✅ Docker Compose Editor initialized")
        except Exception as e:
            print(f"⚠️ Docker Compose Editor initialization failed: {e}")
            import traceback
            traceback.print_exc()
            # Create fallback message in tab
            error_label = tk.Label(
                self.compose_tab,
                text=f"❌ Docker Compose Editor failed to load:\n{str(e)}\n\nPlease check console for details.",
                font=('Segoe UI', 10),
                fg='#CF222E',
                bg='#FFFFFF',
                justify=tk.LEFT,
                padx=20, pady=20
            )
            error_label.pack(fill=tk.BOTH, expand=True)
        
        # Initialize Settings Tab
        try:
            print("🔄 Initializing Settings Tab...")
            self.settings = SettingsTabV4(
                parent=self.settings_tab,
                config_file=CONFIG_FILE,
                append_log=self.append_log
            )
            print("✅ Settings Tab initialized")
        except Exception as e:
            print(f"⚠️ Settings Tab initialization failed: {e}")
            import traceback
            traceback.print_exc()
            # Create fallback message in tab
            error_label = tk.Label(
                self.settings_tab,
                text=f"❌ Settings Tab failed to load:\n{str(e)}\n\nPlease check console for details.",
                font=('Segoe UI', 10),
                fg='#CF222E',
                bg='#FFFFFF',
                justify=tk.LEFT,
                padx=20, pady=20
            )
            error_label.pack(fill=tk.BOTH, expand=True)
        
        self.setup_shortcuts()
        
        # Welcome message - THIS MARKS UI AS READY
        print("=" * 60)
        print("🎉 GUI READY! Application window should be visible now.")
        print("=" * 60)
        print("If you don't see the window:")
        print("  1. Check taskbar for 'Spark Runner GUI V4.1'")
        print("  2. Press Alt+Tab to switch windows")
        print("  3. Window might be behind other windows")
        print("=" * 60)
        
        self.append_log('🎉 Chào mừng đến với Spark Runner GUI!', 'header', self.spark_runner.log_text_widget)
        self.append_log('💡 Nhấn F1 để xem trợ giúp, Ctrl+O để mở file, Ctrl+R để chạy', 'info', self.spark_runner.log_text_widget)
        
        # Auto-check Docker status on startup and update status bar
        self.root.after(1000, self.check_docker_status_startup)

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
        settings_menu.add_separator()
        settings_menu.add_checkbutton(label='Auto-save config', command=self.toggle_auto_save)
        settings_menu.add_separator()
        settings_menu.add_command(label='Open Config Folder', command=self.open_config_folder)
        settings_menu.add_command(label='Backup Configuration', command=self.backup_config)
        settings_menu.add_command(label='Restore Configuration', command=self.restore_config)
        
        # Help menu
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Help', menu=help_menu)
        help_menu.add_command(label='Hướng dẫn (F1)', command=lambda: self.spark_runner.show_help(), accelerator='F1')
        help_menu.add_command(label='Keyboard Shortcuts', command=lambda: self.spark_runner.show_shortcuts())
        help_menu.add_command(label='Check for Updates', command=self.check_updates)
        help_menu.add_separator()
        help_menu.add_command(label='View Logs', command=self.view_app_logs)
        help_menu.add_command(label='Report Issue', command=self.report_issue)
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
        """Update main status bar message"""
        self.status_var.set(message)
    
    def update_docker_status(self, status_text, color='#57606A'):
        """Update Docker status in status bar"""
        if hasattr(self, 'docker_status_var'):
            self.docker_status_var.set(f"🐳 Docker: {status_text}")
    
    def check_docker_status_startup(self):
        """Check Docker status on startup and update status bar"""
        def check():
            from spark_backend import get_container_status
            container = self.config.get('container', 'spark-worker')
            status = get_container_status(container)
            
            if status == 'running':
                self.update_docker_status('✅ Running', '#1A7F37')
            elif status == 'exited':
                self.update_docker_status('⚠️ Stopped', '#9A6700')
            elif status == 'not_found':
                self.update_docker_status('❌ Not Found', '#CF222E')
            else:
                self.update_docker_status(f'⚠️ {status}', '#9A6700')
        
        import threading
        threading.Thread(target=check, daemon=True).start()

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
            if hasattr(self, 'perf_monitor'):
                # Stop monitoring if active
                if self.perf_monitor.monitoring:
                    self.perf_monitor.stop_monitoring()
            print("Cleanup completed.")
        except Exception as e:
            print(f"Error during cleanup: {e}")

    def signal_handler(self, signum, frame):
        """Handle Ctrl+C and other signals"""
        print(f"\nReceived signal {signum}, shutting down gracefully...")
        self.cleanup()
        sys.exit(0)
    
    def open_config_folder(self):
        """Open configuration folder"""
        config_dir = os.path.dirname(os.path.abspath(CONFIG_FILE))
        if sys.platform == 'win32':
            os.startfile(config_dir)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', config_dir])
        else:
            subprocess.Popen(['xdg-open', config_dir])
    
    def backup_config(self):
        """Backup configuration"""
        from tkinter import filedialog
        import shutil
        
        backup_file = filedialog.asksaveasfilename(
            defaultextension='.json',
            filetypes=[('JSON files', '*.json')],
            initialfile=f'spark_config_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        
        if backup_file:
            try:
                shutil.copy2(CONFIG_FILE, backup_file)
                tk.messagebox.showinfo('Success', f'Configuration backed up to:\n{backup_file}')
            except Exception as e:
                tk.messagebox.showerror('Error', f'Failed to backup config:\n{e}')
    
    def restore_config(self):
        """Restore configuration from backup"""
        from tkinter import filedialog
        import shutil
        
        backup_file = filedialog.askopenfilename(
            title='Select backup file',
            filetypes=[('JSON files', '*.json')]
        )
        
        if backup_file:
            if tk.messagebox.askyesno('Confirm', 'This will overwrite current configuration. Continue?'):
                try:
                    shutil.copy2(backup_file, CONFIG_FILE)
                    self.config = load_config()
                    tk.messagebox.showinfo('Success', 'Configuration restored. Please restart the application.')
                except Exception as e:
                    tk.messagebox.showerror('Error', f'Failed to restore config:\n{e}')
    
    def check_updates(self):
        """Check for application updates"""
        tk.messagebox.showinfo(
            'Version Info',
            f'Current Version: {VERSION}\n\n'
            'This is the latest version with:\n'
            '• Enhanced UI/UX\n'
            '• Improved performance\n'
            '• Better error handling\n'
            '• Auto-save functionality\n'
            '• Real-time monitoring'
        )
    
    def view_app_logs(self):
        """View application logs"""
        log_window = tk.Toplevel(self.root)
        log_window.title('Application Logs')
        log_window.geometry('800x600')
        
        log_text = scrolledtext.ScrolledText(log_window, wrap=tk.WORD,
                                             bg='#1e1e1e', fg='#ffffff',
                                             font=('Courier New', 9))
        log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Get main log content
        if hasattr(self.spark_runner, 'log_text_widget'):
            log_text.insert('1.0', self.spark_runner.log_text_widget.get('1.0', tk.END))
        else:
            log_text.insert('1.0', 'No logs available yet.')
    
    def report_issue(self):
        """Open issue reporting dialog"""
        tk.messagebox.showinfo(
            'Report Issue',
            'To report issues:\n\n'
            '1. Export your logs (Ctrl+S)\n'
            '2. Describe the problem\n'
            '3. Include steps to reproduce\n'
            '4. Note your OS and Docker version\n\n'
            'Contact: GitHub Issues or support@example.com'
        )

    def center_window(self, window):
        """Center window on screen"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f'{width}x{height}+{x}+{y}')
    
    def start_auto_save_timer(self):
        """Start auto-save timer - saves config every 30 seconds"""
        def auto_save():
            if self.auto_save_enabled:
                try:
                    save_config(self.config)
                    time_diff = (datetime.now() - self.last_save_time).seconds
                    if time_diff >= 30:  # Only update status if 30+ seconds passed
                        self.update_status('💾 Auto-saved')
                        self.last_save_time = datetime.now()
                except Exception as e:
                    print(f"Auto-save error: {e}")
            
            # Schedule next auto-save
            self.root.after(30000, auto_save)  # Every 30 seconds
        
        # Start first auto-save after 30 seconds
        self.root.after(30000, auto_save)
    
    def toggle_auto_save(self):
        """Toggle auto-save feature"""
        self.auto_save_enabled = not self.auto_save_enabled
        status = "enabled" if self.auto_save_enabled else "disabled"
        self.update_status(f'💾 Auto-save {status}')
        tk.messagebox.showinfo('Auto-Save', f'Auto-save has been {status}')
    
    def on_closing(self):
        """Handle window close event"""
        from tkinter import messagebox
        # Auto-save before closing
        if self.auto_save_enabled:
            try:
                save_config(self.config)
            except:
                pass
        
        if messagebox.askokcancel("Thoát", "Bạn có chắc chắn muốn thoát?"):
            self.cleanup()
            self.root.destroy()

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
