# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Build Configuration for Spark Runner GUI
Version: 6.0.1
"""

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Application name
APP_NAME = 'SparkRunnerGUI'
VERSION = '6.0.1'

# Icon file (will be used if exists)
ICON_FILE = 'icon.ico' if os.path.exists('icon.ico') else None

# Get absolute paths
GUI_PATH = os.path.abspath('run_spark_gui')
ROOT_PATH = os.path.abspath('.')

# Collect all Python files from run_spark_gui
datas = [
    (os.path.join(GUI_PATH, '*.py'), 'run_spark_gui'),
    (os.path.join(ROOT_PATH, 'docker-compose.yml'), '.'),
    (os.path.join(ROOT_PATH, 'spark_runner_config.json'), '.'),
    (os.path.join(ROOT_PATH, 'example_port_config.yaml'), '.'),
]

# Collect all submodules
hiddenimports = [
    # Core modules
    'tkinter',
    'tkinter.ttk',
    'tkinter.scrolledtext',
    'tkinter.filedialog',
    'tkinter.messagebox',
    
    # Application modules
    'validation',
    'logging_config',
    'health_check',
    'error_handler',
    'input_sanitizer',
    'auto_recovery',
    'resource_manager',
    'backup_manager',
    'spark_runner_tab_v4_clean',
    'hdfs_upload_tab_v4_clean',
    'ai_code_generator_tab_v4_clean',
    'performance_monitor_v4_clean',
    'docker_compose_editor_v4',
    'settings_tab_v4',
    'advanced_ai_tab_v8',
    'advanced_ai_engine_v8',
    'modern_theme',
    'spark_backend',
    'docker_utils',
    'hdfs_utils',
    'system_utils',
    'database',
    'advanced_cache',
    'metrics_system',
    'security_validator',
    'java_unzip_util',
    
    # Third-party
    'yaml',
    'pandas',
    'requests',
    'subprocess',
    'threading',
    'queue',
    'asyncio',
    'concurrent.futures',
    
    # AI API (optional)
    'google.generativeai',
    'openai',
    'anthropic',
]

# Analysis
a = Analysis(
    [os.path.join(GUI_PATH, 'main.py')],
    pathex=[GUI_PATH, ROOT_PATH],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
        'PyQt5',
        'PySide2',
        'jupyter',
        'notebook',
        'IPython',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# PYZ (compressed archive)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# EXE (single file)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_FILE,
    version_file=None,
)
