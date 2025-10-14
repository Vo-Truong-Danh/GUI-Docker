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

# Import enhanced modules
try:
    from validation import ConfigValidator, ValidationError
    VALIDATION_AVAILABLE = True
except ImportError:
    print("⚠️ Warning: Validation module not available")
    VALIDATION_AVAILABLE = False
    ConfigValidator = None

try:
    from logging_config import get_logger
    LOGGING_AVAILABLE = True
    # Create application logger
    app_logger = get_logger('main_app', log_to_file=True, log_to_console=False)
except ImportError:
    print("⚠️ Warning: Logging module not available")
    LOGGING_AVAILABLE = False
    app_logger = None

try:
    from health_check import health_checker
    HEALTH_CHECK_AVAILABLE = True
except ImportError:
    print("⚠️ Warning: Health check module not available")
    HEALTH_CHECK_AVAILABLE = False
    health_checker = None

# Import new enhanced error handling modules
try:
    from error_handler import get_error_handler, safe_execute, ErrorSeverity, with_error_handling
    ERROR_HANDLER_AVAILABLE = True
    error_handler = get_error_handler(app_logger if LOGGING_AVAILABLE else None)
    print("✅ Enhanced error handling enabled (v2.0)")
except ImportError:
    print("⚠️ Warning: Enhanced error handler not available")
    ERROR_HANDLER_AVAILABLE = False
    error_handler = None

try:
    from input_sanitizer import InputSanitizer, InputValidator
    INPUT_SANITIZER_AVAILABLE = True
    print("✅ Input sanitizer enabled")
except ImportError:
    print("⚠️ Warning: Input sanitizer not available")
    INPUT_SANITIZER_AVAILABLE = False
    InputSanitizer = None

try:
    from auto_recovery import get_auto_recovery_manager
    AUTO_RECOVERY_AVAILABLE = True
    auto_recovery = get_auto_recovery_manager(app_logger if LOGGING_AVAILABLE else None)
    print("✅ Auto-recovery system enabled")
except ImportError:
    print("⚠️ Warning: Auto-recovery not available")
    AUTO_RECOVERY_AVAILABLE = False
    auto_recovery = None

# Import NEW resource and backup managers
try:
    from resource_manager import get_resource_tracker, temp_file, temp_directory
    RESOURCE_MANAGER_AVAILABLE = True
    resource_tracker = get_resource_tracker()
    print("✅ Resource manager enabled")
except ImportError:
    print("⚠️ Warning: Resource manager not available")
    RESOURCE_MANAGER_AVAILABLE = False
    resource_tracker = None

try:
    from backup_manager import get_backup_manager
    BACKUP_MANAGER_AVAILABLE = True
    backup_manager = get_backup_manager(max_backups=10)
    print("✅ Backup manager enabled")
except ImportError:
    print("⚠️ Warning: Backup manager not available")
    BACKUP_MANAGER_AVAILABLE = False
    backup_manager = None

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

# Import AI Engine V8.3 (PySpark + Real HDFS + Fixed Provider Mapping)
try:
    print("🔄 Loading AI Engine V8.3...")
    from advanced_ai_tab_v8 import AdvancedAITabV8 as AdvancedAITab
    ADVANCED_AI_AVAILABLE = True
    print("✅ AI Engine V8.3 loaded successfully!")
except ImportError as e:
    print(f"❌ Error loading AI Engine V8.3: {e}")
    ADVANCED_AI_AVAILABLE = False
    AdvancedAITab = None

print("✅ Using Clean Professional UI V4 (all tabs)")
from modern_theme import setup_modern_theme, ModernTheme, Typography, Spacing, LightTheme

APP_TITLE = "Spark Runner GUI V6.0"
CONFIG_FILE = "spark_runner_config.json"
VERSION = "6.0.0"  # Enhanced with resource management, backup, and improved error handling

INFO_TEXT = ""  # Removed to save space


def validate_config(config):
    """
    Validate configuration values and fix invalid ones
    Returns validated config with corrections logged
    """
    if LOGGING_AVAILABLE and app_logger:
        app_logger.info("Validating configuration")
    
    # Use new validation module if available
    if VALIDATION_AVAILABLE and ConfigValidator:
        is_valid, errors = ConfigValidator.validate_config(config)
        
        if not is_valid:
            if LOGGING_AVAILABLE and app_logger:
                app_logger.warning(f"Configuration has {len(errors)} validation errors")
                for error in errors:
                    app_logger.warning(f"  - {error}")
            
            print("⚠️ Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
            
            # Try to fix config
            fixed_config = ConfigValidator.fix_config(config)
            
            # Validate again
            is_valid_after_fix, errors_after_fix = ConfigValidator.validate_config(fixed_config)
            
            if is_valid_after_fix:
                print("✅ Configuration automatically fixed")
                if LOGGING_AVAILABLE and app_logger:
                    app_logger.info("Configuration automatically fixed")
                return fixed_config
            else:
                print("⚠️ Could not automatically fix all errors")
                if LOGGING_AVAILABLE and app_logger:
                    app_logger.warning("Could not automatically fix all configuration errors")
                return fixed_config
        else:
            if LOGGING_AVAILABLE and app_logger:
                app_logger.info("Configuration is valid")
            return config
    
    # Fallback to old validation
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
        if LOGGING_AVAILABLE and app_logger:
            for error in errors:
                app_logger.warning(error)
    
    return validated


def load_config():
    """Load configuration from JSON file with enhanced validation and error handling"""
    if LOGGING_AVAILABLE and app_logger:
        app_logger.info(f"Loading configuration from {CONFIG_FILE}")
    
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
        def load_and_parse():
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
                
                if LOGGING_AVAILABLE and app_logger:
                    app_logger.info("Configuration loaded successfully")
                
                return config
        
        # Use safe_execute if available
        if ERROR_HANDLER_AVAILABLE and error_handler:
            config = error_handler.safe_execute(
                load_and_parse,
                default=validate_config(default),
                context="Loading configuration file"
            )
            return config
        else:
            # Fallback to traditional try-except
            try:
                return load_and_parse()
            except json.JSONDecodeError as e:
                error_msg = f"Failed to parse config file: {e}"
                print(f"❌ {error_msg}, using defaults")
                if LOGGING_AVAILABLE and app_logger:
                    app_logger.error(error_msg)
                return validate_config(default)
            except Exception as e:
                error_msg = f"Failed to load config: {e}"
                print(f"❌ {error_msg}, using defaults")
                if LOGGING_AVAILABLE and app_logger:
                    app_logger.error(error_msg, exc_info=True)
                return validate_config(default)
    
    if LOGGING_AVAILABLE and app_logger:
        app_logger.info("No config file found, using defaults")
    
    return validate_config(default)


def save_config(config):
    """Save configuration to JSON file with error handling and automatic backup"""
    try:
        # Create backup before saving (if backup manager available)
        if BACKUP_MANAGER_AVAILABLE and backup_manager and os.path.exists(CONFIG_FILE):
            try:
                success, backup_id = backup_manager.create_backup([CONFIG_FILE])
                if success:
                    if LOGGING_AVAILABLE and app_logger:
                        app_logger.info(f"Configuration backed up: {backup_id}")
                else:
                    if LOGGING_AVAILABLE and app_logger:
                        app_logger.warning(f"Failed to backup configuration: {backup_id}")
            except Exception as e:
                print(f"⚠️ Backup failed: {e}")
                if LOGGING_AVAILABLE and app_logger:
                    app_logger.warning(f"Configuration backup failed: {e}")
        
        # Validate before saving
        if VALIDATION_AVAILABLE and ConfigValidator:
            is_valid, errors = ConfigValidator.validate_config(config)
            if not is_valid:
                print("⚠️ Warning: Saving invalid configuration")
                if LOGGING_AVAILABLE and app_logger:
                    app_logger.warning("Saving invalid configuration")
                    for error in errors:
                        app_logger.warning(f"  - {error}")
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        if LOGGING_AVAILABLE and app_logger:
            app_logger.info(f"Configuration saved to {CONFIG_FILE}")
    
    except PermissionError as e:
        error_msg = f"Permission denied when saving config: {e}"
        print(f"❌ {error_msg}")
        if LOGGING_AVAILABLE and app_logger:
            app_logger.error(error_msg)
    
    except Exception as e:
        error_msg = f"Failed to save config: {e}"
        print(f"❌ {error_msg}")
        if LOGGING_AVAILABLE and app_logger:
            app_logger.error(error_msg, exc_info=True)


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
        
        # Set window to maximized/full screen on startup
        root.state('zoomed')  # Windows: maximized
        # root.attributes('-fullscreen', True)  # Uncomment for true fullscreen
        
        # Minimum size
        root.minsize(1150, 750)
        
        # Register cleanup handlers
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Setup modern theme
        self.theme = setup_modern_theme(root, mode='light')
        
        # Fullscreen toggle support (F11 to toggle, Esc to exit)
        self.is_fullscreen = False
        root.bind('<F11>', self.toggle_fullscreen)
        root.bind('<Escape>', self.exit_fullscreen)
        
        # Setup menu bar
        self.create_menu()
        
        # Main container - NO PADDING for full screen usage
        main_frame = ttk.Frame(root, padding=(0, 0, 0, 0))
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # === Notebook with Tabs (Direct - No Header) ===
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Tab 1: Spark Runner
        # Tab 1: Spark Runner
        self.spark_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.spark_tab, text='🚀 Spark Runner')
        
        # Tab 2: HDFS Upload
        self.hdfs_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.hdfs_tab, text='📤 HDFS Upload')
        
        # Tab 3: AI Code Generator (Old)
        self.ai_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.ai_tab, text='🤖 AI Code Generator')
        
        # Tab 4: AI Engine V8.3 Optimized (PySpark + Real HDFS)
        self.advanced_ai_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.advanced_ai_tab, text='🤖 AI Engine V8.3')
        
        # Tab 5: Performance Monitor
        self.perf_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.perf_tab, text='📊 Performance Monitor')
        
        # Tab 6: Docker Compose Editor
        self.compose_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.compose_tab, text='🐳 Docker Compose')
        
        # Tab 7: Settings
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
        
        # Initialize AI Engine V8.3 Optimized
        if ADVANCED_AI_AVAILABLE:
            try:
                print("🔄 Initializing AI Engine V8.3 Optimized (PySpark + Real HDFS)...")
                
                # Create simple config manager wrapper
                class SimpleConfigManager:
                    def __init__(self, config):
                        self.config = config
                    
                    def save_config(self):
                        save_config(self.config)
                
                config_manager = SimpleConfigManager(self.config)
                
                self.advanced_ai = AdvancedAITab(
                    parent=self.advanced_ai_tab,
                    config_manager=config_manager
                )
                
                # Link Spark Runner tab for integration
                self.advanced_ai.spark_runner_tab = self.spark_runner
                self.advanced_ai.main_notebook = self.notebook
                
                print("✅ AI Engine V8.3 Optimized initialized successfully!")
                print("✅ Integrated with Spark Runner for direct execution")
            except Exception as e:
                print(f"⚠️ AI Engine V8.3 Optimized initialization failed: {e}")
                import traceback
                traceback.print_exc()
                # Create fallback message in tab
                error_label = tk.Label(
                    self.advanced_ai_tab,
                    text=f"❌ AI Engine V8.3 Optimized failed to load:\n{str(e)}\n\n"
                         f"Cài đặt dependencies:\n"
                         f"pip install openai anthropic google-generativeai\n\n"
                         f"Xem chi tiết trong console.",
                    font=('Segoe UI', 10),
                    fg='#CF222E',
                    bg='#FFFFFF',
                    justify=tk.LEFT,
                    padx=20, pady=20
                )
                error_label.pack(fill=tk.BOTH, expand=True)
        else:
            # Show installation instruction
            install_frame = tk.Frame(self.advanced_ai_tab, bg='#FFFFFF')
            install_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)
            
            icon_label = tk.Label(
                install_frame, text="🤖",
                bg='#FFFFFF', font=('Arial', 48)
            )
            icon_label.pack(pady=(0, 20))
            
            title_label = tk.Label(
                install_frame,
                text="AI Engine V8.3 - System Instruction",
                bg='#FFFFFF', fg='#24292F',
                font=('Segoe UI', 18, 'bold')
            )
            title_label.pack(pady=(0, 10))
            
            desc_label = tk.Label(
                install_frame,
                text="Code Generator Machine | Temperature 0.0 | Code Only Output",
                bg='#FFFFFF', fg='#57606A',
                font=('Segoe UI', 11)
            )
            desc_label.pack(pady=(0, 30))
            
            features_label = tk.Label(
                install_frame,
                text="✨ Tính năng mới:\n\n"
                     "• HDFS File Browser tích hợp\n"
                     "• Quick Actions và Keyboard Shortcuts\n"
                     "• Auto-detect data patterns\n"
                     "• Collapsible sections tiết kiệm không gian\n"
                     "• Smart templates và suggestions\n"
                     "• Export code với 1 click",
                bg='#F6F8FA', fg='#24292F',
                font=('Segoe UI', 10),
                justify=tk.LEFT,
                padx=20, pady=15,
                relief=tk.SOLID, borderwidth=1
            )
            features_label.pack(pady=(0, 20))
            
            install_label = tk.Label(
                install_frame,
                text="📦 Cài đặt dependencies:\n\n"
                     "pip install openai>=1.0.0\n"
                     "pip install anthropic>=0.7.0\n"
                     "pip install google-generativeai>=0.3.0\n\n"
                     "Hoặc:\n\n"
                     "pip install -r run_spark_gui/requirements_ai.txt",
                bg='#F6F8FA', fg='#24292F',
                font=('Consolas', 9),
                justify=tk.LEFT,
                padx=20, pady=20,
                relief=tk.SOLID, borderwidth=1
            )
            install_label.pack(pady=(0, 20))
            
            restart_label = tk.Label(
                install_frame,
                text="Sau khi cài đặt, khởi động lại ứng dụng",
                bg='#FFFFFF', fg='#57606A',
                font=('Segoe UI', 9, 'italic')
            )
            restart_label.pack()
        
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
    
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode (F11)"""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)
        return 'break'
    
    def exit_fullscreen(self, event=None):
        """Exit fullscreen mode (Escape)"""
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.root.attributes('-fullscreen', False)
        return 'break'
    
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
            except Exception as e:
                if LOGGING_AVAILABLE and app_logger:
                    app_logger.warning(f'Failed to auto-save config on exit: {e}')
        
        if messagebox.askokcancel("Thoát", "Bạn có chắc chắn muốn thoát?"):
            self.cleanup()
            self.root.destroy()

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
