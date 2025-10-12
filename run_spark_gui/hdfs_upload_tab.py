"""
HDFS Upload Tab for Spark Runner GUI
Handles uploading multiple file types to HDFS
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import subprocess
import threading
from pathlib import Path
from datetime import datetime
import mimetypes


class HDFSUploadTab:
    """HDFS Upload functionality in a separate tab"""
    
    # Supported file types
    SUPPORTED_TYPES = {
        'Data Files': ['.csv', '.json', '.parquet', '.avro', '.orc'],
        'Text Files': ['.txt', '.log', '.md'],
        'Compressed': ['.zip', '.gz', '.tar', '.tar.gz'],
        'Images': ['.jpg', '.jpeg', '.png', '.gif'],
        'Others': ['.*']  # All files
    }
    
    def __init__(self, parent_frame, config, status_callback, log_callback):
        """
        Initialize HDFS Upload tab
        
        Args:
            parent_frame: Parent ttk.Frame
            config: Configuration dict
            status_callback: Function to update status bar
            log_callback: Function to append to log
        """
        self.frame = parent_frame
        self.config = config
        self.update_status = status_callback
        self.append_log = log_callback
        self.selected_files = []
        self.upload_queue = []
        self.is_uploading = False
        
        self.create_ui()
    
    def create_ui(self):
        """Create HDFS Upload tab UI"""
        main_container = ttk.Frame(self.frame, padding=10)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Info section
        info_text = (
            "📤 Upload nhiều loại dữ liệu lên HDFS\n"
            "Hỗ trợ: CSV, JSON, Parquet, TXT, Log, ZIP và nhiều định dạng khác"
        )
        info_lbl = ttk.Label(main_container, text=info_text, foreground='#555',
                            font=('Segoe UI', 9))
        info_lbl.pack(fill=tk.X, pady=(0, 10))
        
        # === HDFS Configuration ===
        config_frame = ttk.LabelFrame(main_container, text='⚙️ HDFS Configuration', padding=10)
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Row 1: Container & HDFS Host
        row1 = ttk.Frame(config_frame)
        row1.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(row1, text='HDFS Container:', font=('Segoe UI', 9)).pack(side=tk.LEFT)
        self.hdfs_container_var = tk.StringVar(value=self.config.get('hdfs_container', 'namenode'))
        container_combo = ttk.Combobox(row1, textvariable=self.hdfs_container_var, 
                                       values=['namenode', 'datanode', 'spark-worker'],
                                       width=15, state='readonly', font=('Courier New', 9))
        container_combo.pack(side=tk.LEFT, padx=(8, 20))
        
        ttk.Label(row1, text='HDFS Host:', font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=(10, 0))
        self.hdfs_host_var = tk.StringVar(value=self.config.get('hdfs_host', 'hdfs://namenode:8020'))
        hdfs_host_entry = ttk.Entry(row1, textvariable=self.hdfs_host_var, width=25,
                                     font=('Courier New', 9))
        hdfs_host_entry.pack(side=tk.LEFT, padx=(8, 0))
        
        # Row 2: Default path & buttons
        row2 = ttk.Frame(config_frame)
        row2.pack(fill=tk.X)
        
        ttk.Label(row2, text='Default Path:', font=('Segoe UI', 9)).pack(side=tk.LEFT)
        self.hdfs_path_var = tk.StringVar(value=self.config.get('hdfs_default_path', '/user/spark/data'))
        hdfs_path_entry = ttk.Entry(row2, textvariable=self.hdfs_path_var, width=35,
                                     font=('Courier New', 9))
        hdfs_path_entry.pack(side=tk.LEFT, padx=(8, 10))
        
        save_btn = ttk.Button(row2, text='💾 Save Config', command=self.save_hdfs_config, width=12)
        save_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        test_btn = ttk.Button(row2, text='🔍 Test Connection', command=self.test_hdfs_connection, width=15)
        test_btn.pack(side=tk.LEFT)
        
        # Row 3: Options
        row3 = ttk.Frame(config_frame)
        row3.pack(fill=tk.X, pady=(5, 0))
        
        self.auto_extract_var = tk.BooleanVar(value=self.config.get('auto_extract_archives', True))
        extract_check = ttk.Checkbutton(row3, text='🗜️ Auto-extract compressed files (ZIP, GZ, TAR)', 
                                        variable=self.auto_extract_var,
                                        command=self.on_extract_option_changed)
        extract_check.pack(side=tk.LEFT)
        
        self.delete_archive_var = tk.BooleanVar(value=self.config.get('delete_archive_after_extract', True))
        delete_check = ttk.Checkbutton(row3, text='🗑️ Delete archive after extraction', 
                                       variable=self.delete_archive_var,
                                       command=self.on_extract_option_changed)
        delete_check.pack(side=tk.LEFT, padx=(20, 0))
        
        # === File Selection ===
        select_frame = ttk.LabelFrame(main_container, text='📁 File Selection', padding=10)
        select_frame.pack(fill=tk.X, pady=(0, 10))
        
        btn_row = ttk.Frame(select_frame)
        btn_row.pack(fill=tk.X, pady=(0, 5))
        
        self.add_files_btn = ttk.Button(btn_row, text='➕ Add Files', 
                                        command=self.add_files, width=15)
        self.add_files_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.add_folder_btn = ttk.Button(btn_row, text='📂 Add Folder', 
                                         command=self.add_folder, width=15)
        self.add_folder_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_btn = ttk.Button(btn_row, text='🗑️ Clear All', 
                                    command=self.clear_files, width=12)
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # File list with scrollbar
        list_frame = ttk.Frame(select_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for file list
        columns = ('File', 'Size', 'Type', 'Status')
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        self.file_tree.heading('File', text='File Name')
        self.file_tree.heading('Size', text='Size')
        self.file_tree.heading('Type', text='Type')
        self.file_tree.heading('Status', text='Status')
        
        self.file_tree.column('File', width=400)
        self.file_tree.column('Size', width=100)
        self.file_tree.column('Type', width=100)
        self.file_tree.column('Status', width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)
        
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # === Upload Actions ===
        action_frame = ttk.LabelFrame(main_container, text='🚀 Upload Actions', padding=10)
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        action_row = ttk.Frame(action_frame)
        action_row.pack()
        
        self.upload_btn = ttk.Button(action_row, text='▶️ Start Upload', 
                                     command=self.start_upload, width=20,
                                     style='Success.TButton')
        self.upload_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(action_row, text='⏹️ Stop', 
                                   command=self.stop_upload, width=12,
                                   state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress
        self.upload_progress = ttk.Progressbar(action_frame, mode='determinate', length=400)
        self.upload_progress.pack(pady=(10, 0))
        
        self.progress_label = ttk.Label(action_frame, text='Ready', font=('Segoe UI', 9))
        self.progress_label.pack(pady=(5, 0))
        
        # === Log ===
        log_frame = ttk.LabelFrame(main_container, text='📊 Upload Log', padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.hdfs_log = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD,
                                                   bg='#fafafa', font=('Courier New', 9))
        self.hdfs_log.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags
        self.hdfs_log.tag_config('success', foreground='#28a745', font=('Courier New', 9, 'bold'))
        self.hdfs_log.tag_config('error', foreground='#dc3545', font=('Courier New', 9, 'bold'))
        self.hdfs_log.tag_config('info', foreground='#17a2b8', font=('Courier New', 9, 'bold'))
        
        # Welcome message
        self.log_hdfs('📤 HDFS Upload Module Ready', 'info')
        self.log_hdfs('💡 Add files/folders and click "Start Upload"', 'info')
    
    def log_hdfs(self, message, tag='normal'):
        """Append message to HDFS log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.hdfs_log.insert(tk.END, f'[{timestamp}] {message}\n', tag)
        self.hdfs_log.see(tk.END)
    
    def save_hdfs_config(self):
        """Save HDFS configuration"""
        self.config['hdfs_container'] = self.hdfs_container_var.get()
        self.config['hdfs_host'] = self.hdfs_host_var.get()
        self.config['hdfs_default_path'] = self.hdfs_path_var.get()
        self.config['auto_extract_archives'] = self.auto_extract_var.get()
        self.config['delete_archive_after_extract'] = self.delete_archive_var.get()
        
        # Save to file
        try:
            import json
            with open('spark_runner_config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.log_hdfs('✅ Configuration saved', 'success')
            self.update_status('✅ HDFS config saved')
        except Exception as e:
            self.log_hdfs(f'❌ Failed to save config: {e}', 'error')
    
    def on_extract_option_changed(self):
        """Handle extract option change"""
        self.config['auto_extract_archives'] = self.auto_extract_var.get()
        self.config['delete_archive_after_extract'] = self.delete_archive_var.get()
        
        if self.auto_extract_var.get():
            self.log_hdfs('✅ Auto-extract enabled', 'success')
        else:
            self.log_hdfs('⚠️ Auto-extract disabled', 'info')
    
    def is_archive_file(self, filename):
        """Check if file is a compressed archive"""
        archive_extensions = ['.zip', '.gz', '.tar', '.tar.gz', '.tgz', '.bz2', '.tar.bz2']
        filename_lower = filename.lower()
        return any(filename_lower.endswith(ext) for ext in archive_extensions)
    
    def get_extract_command(self, filename):
        """Get the appropriate extract command for the archive type"""
        filename_lower = filename.lower()
        
        if filename_lower.endswith('.zip'):
            # Use jar command (Java JAR tool) which is available in Hadoop containers
            # jar xf = extract files from archive
            return f'mkdir -p /tmp/extracted && cd /tmp/extracted && jar xf /tmp/{filename} && cd - && rm /tmp/{filename}'
        elif filename_lower.endswith('.tar.gz') or filename_lower.endswith('.tgz'):
            return f'mkdir -p /tmp/extracted && tar -xzf /tmp/{filename} -C /tmp/extracted/ && rm /tmp/{filename}'
        elif filename_lower.endswith('.tar.bz2'):
            return f'mkdir -p /tmp/extracted && tar -xjf /tmp/{filename} -C /tmp/extracted/ && rm /tmp/{filename}'
        elif filename_lower.endswith('.tar'):
            return f'mkdir -p /tmp/extracted && tar -xf /tmp/{filename} -C /tmp/extracted/ && rm /tmp/{filename}'
        elif filename_lower.endswith('.gz') and not filename_lower.endswith('.tar.gz'):
            # Single .gz file (not tar.gz)
            base_name = filename[:-3]  # Remove .gz
            return f'gunzip /tmp/{filename} && mv /tmp/{base_name} /tmp/extracted/'
        elif filename_lower.endswith('.bz2'):
            base_name = filename[:-4]  # Remove .bz2
            return f'bunzip2 /tmp/{filename} && mv /tmp/{base_name} /tmp/extracted/'
        
        return None
    
    def test_hdfs_connection(self):
        """Test HDFS connection"""
        self.log_hdfs('🔍 Testing HDFS connection...', 'info')
        
        def test_thread():
            try:
                container = self.hdfs_container_var.get()
                
                # Step 1: Check if container is running
                self.log_hdfs('  📦 Checking if container is running...', 'info')
                cmd_check = ['docker', 'ps', '--filter', f'name={container}', '--format', '{{.Names}}']
                result_check = subprocess.run(cmd_check, capture_output=True, text=True, timeout=5)
                
                if container not in result_check.stdout:
                    self.log_hdfs(f'❌ Container "{container}" is not running!', 'error')
                    self.log_hdfs('💡 Start it with: docker start ' + container, 'info')
                    return
                
                self.log_hdfs(f'  ✅ Container "{container}" is running', 'success')
                
                # Step 2: Check HDFS configuration in container
                self.log_hdfs('  ⚙️ Checking HDFS configuration...', 'info')
                cmd_config = ['docker', 'exec', container, 'hadoop', 'version']
                result_config = subprocess.run(cmd_config, capture_output=True, text=True, timeout=5)
                
                if result_config.returncode == 0:
                    version_line = result_config.stdout.split('\n')[0]
                    self.log_hdfs(f'  ✅ Hadoop installed: {version_line}', 'success')
                else:
                    self.log_hdfs('  ⚠️ Hadoop command not found in container', 'error')
                    return
                
                # Step 3: Check namenode connectivity
                self.log_hdfs('  🔗 Testing namenode connectivity...', 'info')
                cmd_ping = ['docker', 'exec', container, 'ping', '-c', '1', 'namenode']
                result_ping = subprocess.run(cmd_ping, capture_output=True, text=True, timeout=5)
                
                if result_ping.returncode == 0:
                    self.log_hdfs('  ✅ Namenode is reachable', 'success')
                else:
                    self.log_hdfs('  ❌ Cannot reach namenode!', 'error')
                    self.log_hdfs('  💡 Make sure namenode container is running', 'info')
                    self.log_hdfs('  💡 Check: docker ps | grep namenode', 'info')
                    return
                
                # Step 4: Test HDFS filesystem
                self.log_hdfs('  📁 Testing HDFS filesystem...', 'info')
                cmd = ['docker', 'exec', container, 'hadoop', 'fs', '-ls', '/']
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    self.log_hdfs('✅ HDFS connection successful!', 'success')
                    self.log_hdfs(f'📁 Root directory listing:', 'info')
                    lines = result.stdout.strip().split('\n')
                    for line in lines[:5]:
                        if line.strip():
                            self.log_hdfs(f'  {line}')
                    if len(lines) > 5:
                        self.log_hdfs(f'  ... and {len(lines)-5} more items', 'info')
                else:
                    error_msg = result.stderr.strip()
                    self.log_hdfs(f'❌ HDFS connection failed!', 'error')
                    
                    # Parse common errors
                    if 'Connection refused' in error_msg:
                        self.log_hdfs('  💡 Namenode is not accepting connections', 'error')
                        self.log_hdfs('  💡 Check: docker logs namenode', 'info')
                        self.log_hdfs('  💡 Wait for namenode to fully start (may take 30s)', 'info')
                    elif 'could not be resolved' in error_msg or 'Unknown host' in error_msg:
                        self.log_hdfs('  💡 Namenode hostname cannot be resolved', 'error')
                        self.log_hdfs('  💡 Containers must be in same network', 'info')
                    elif 'safe mode' in error_msg.lower():
                        self.log_hdfs('  ⚠️ HDFS is in safe mode', 'error')
                        self.log_hdfs('  💡 Wait or run: hadoop dfsadmin -safemode leave', 'info')
                    else:
                        self.log_hdfs(f'  Error details: {error_msg[:200]}', 'error')
                        
            except subprocess.TimeoutExpired:
                self.log_hdfs('❌ Connection test timeout!', 'error')
                self.log_hdfs('💡 Container or namenode may be frozen', 'info')
            except Exception as e:
                self.log_hdfs(f'❌ Error: {e}', 'error')
        
        thread = threading.Thread(target=test_thread)
        thread.daemon = True
        thread.start()
    
    def add_files(self):
        """Add files to upload list"""
        filetypes = [
            ('All Files', '*.*'),
            ('CSV Files', '*.csv'),
            ('JSON Files', '*.json'),
            ('Parquet Files', '*.parquet'),
            ('Text Files', '*.txt'),
            ('Log Files', '*.log')
        ]
        
        files = filedialog.askopenfilenames(title='Select files to upload',
                                           filetypes=filetypes)
        
        if files:
            for filepath in files:
                self.add_file_to_list(filepath)
            self.log_hdfs(f'➕ Added {len(files)} file(s)', 'info')
    
    def add_folder(self):
        """Add all files from a folder"""
        folder = filedialog.askdirectory(title='Select folder to upload')
        
        if folder:
            count = 0
            for root, dirs, files in os.walk(folder):
                for file in files:
                    filepath = os.path.join(root, file)
                    self.add_file_to_list(filepath)
                    count += 1
            self.log_hdfs(f'📂 Added {count} file(s) from folder', 'info')
    
    def add_file_to_list(self, filepath):
        """Add a file to the tree view"""
        if filepath in self.selected_files:
            return
        
        self.selected_files.append(filepath)
        
        # Get file info
        path = Path(filepath)
        size = path.stat().st_size
        size_str = self.format_size(size)
        file_type = path.suffix or 'Unknown'
        
        # Add to treeview
        self.file_tree.insert('', tk.END, values=(path.name, size_str, file_type, 'Pending'))
    
    def format_size(self, size_bytes):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def clear_files(self):
        """Clear all files from list"""
        if self.selected_files:
            if messagebox.askyesno('Confirm', 'Clear all files from list?'):
                self.selected_files.clear()
                for item in self.file_tree.get_children():
                    self.file_tree.delete(item)
                self.log_hdfs('🗑️ File list cleared', 'info')
    
    def start_upload(self):
        """Start uploading files to HDFS"""
        if not self.selected_files:
            messagebox.showwarning('No Files', 'Please add files to upload first')
            return
        
        self.is_uploading = True
        self.upload_btn['state'] = tk.DISABLED
        self.stop_btn['state'] = tk.NORMAL
        self.add_files_btn['state'] = tk.DISABLED
        self.add_folder_btn['state'] = tk.DISABLED
        
        self.log_hdfs('=' * 60, 'info')
        self.log_hdfs('🚀 Starting batch upload to HDFS', 'info')
        self.log_hdfs('=' * 60, 'info')
        
        thread = threading.Thread(target=self._upload_thread)
        thread.daemon = True
        thread.start()
    
    def _upload_thread(self):
        """Upload files in background thread"""
        container = self.hdfs_container_var.get()
        hdfs_path = self.hdfs_path_var.get()
        total_files = len(self.selected_files)
        
        # Create HDFS directory if not exists
        self.log_hdfs(f'📁 Checking HDFS directory: {hdfs_path}', 'info')
        try:
            cmd_mkdir = ['docker', 'exec', container, 'hadoop', 'fs', '-mkdir', '-p', hdfs_path]
            result_mkdir = subprocess.run(cmd_mkdir, capture_output=True, text=True, timeout=10)
            if result_mkdir.returncode == 0:
                self.log_hdfs(f'✅ Directory ready: {hdfs_path}', 'success')
            else:
                # Directory might already exist, check if we can access it
                cmd_test = ['docker', 'exec', container, 'hadoop', 'fs', '-test', '-d', hdfs_path]
                result_test = subprocess.run(cmd_test, capture_output=True, text=True, timeout=5)
                if result_test.returncode == 0:
                    self.log_hdfs(f'✅ Directory exists: {hdfs_path}', 'success')
                else:
                    self.log_hdfs(f'❌ Cannot access directory: {hdfs_path}', 'error')
                    self.log_hdfs(f'💡 Check path permissions or create it manually', 'info')
                    self.is_uploading = False
                    self.upload_btn['state'] = tk.NORMAL
                    self.stop_btn['state'] = tk.DISABLED
                    self.add_files_btn['state'] = tk.NORMAL
                    self.add_folder_btn['state'] = tk.NORMAL
                    return
        except Exception as e:
            self.log_hdfs(f'⚠️ Could not verify directory: {e}', 'error')
        
        self.log_hdfs('')  # Empty line
        
        for idx, filepath in enumerate(self.selected_files):
            if not self.is_uploading:
                self.log_hdfs('⏹️ Upload stopped by user', 'info')
                break
            
            # Update progress
            progress = int((idx / total_files) * 100)
            self.upload_progress['value'] = progress
            self.progress_label['text'] = f'Uploading {idx + 1}/{total_files}: {Path(filepath).name}'
            
            # Upload file
            filepath_obj = Path(filepath)
            filename = filepath_obj.name
            file_size = filepath_obj.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            
            self.log_hdfs(f'\n[{idx + 1}/{total_files}] Uploading: {filename}', 'info')
            self.log_hdfs(f'  📊 File size: {self.format_size(file_size)}', 'info')
            
            # Calculate dynamic timeout based on file size (min 30s, +10s per 10MB)
            copy_timeout = max(30, int(30 + (file_size_mb / 10) * 10))
            upload_timeout = max(60, int(60 + (file_size_mb / 10) * 20))
            
            self.log_hdfs(f'  ⏱️ Timeout: {copy_timeout}s (copy) + {upload_timeout}s (upload)', 'info')
            
            try:
                # Step 1: Copy to container
                cmd1 = ['docker', 'cp', filepath, f'{container}:/tmp/{filename}']
                self.log_hdfs(f'  📦 Copying to container... (may take a while for large files)', 'info')
                
                p1 = subprocess.run(cmd1, capture_output=True, text=True, timeout=copy_timeout)
                if p1.returncode != 0:
                    self.log_hdfs(f'  ❌ Failed to copy: {p1.stderr}', 'error')
                    self.update_tree_status(idx, 'Failed - Copy')
                    continue
                
                self.log_hdfs(f'  ✅ Copied to container', 'success')
                
                # Step 1.5: Extract if archive and option enabled
                is_archive = self.is_archive_file(filename)
                auto_extract = self.auto_extract_var.get()
                delete_after = self.delete_archive_var.get()
                
                files_to_upload = [filename]  # Default: upload the original file
                upload_source = '/tmp'
                
                if is_archive and auto_extract:
                    self.log_hdfs(f'  🗜️ Detected archive file, extracting...', 'info')
                    
                    # Create extraction directory
                    cmd_mkdir = ['docker', 'exec', container, 'mkdir', '-p', '/tmp/extracted']
                    subprocess.run(cmd_mkdir, capture_output=True, timeout=5)
                    
                    # Get extract command
                    extract_cmd = self.get_extract_command(filename)
                    
                    if extract_cmd:
                        # Extract the archive
                        cmd_extract = ['docker', 'exec', container, 'sh', '-c', extract_cmd]
                        p_extract = subprocess.run(cmd_extract, capture_output=True, text=True, timeout=upload_timeout)
                        
                        if p_extract.returncode == 0:
                            self.log_hdfs(f'  ✅ Extracted successfully', 'success')
                            
                            # List extracted files
                            cmd_list = ['docker', 'exec', container, 'find', '/tmp/extracted', '-type', 'f']
                            p_list = subprocess.run(cmd_list, capture_output=True, text=True, timeout=10)
                            
                            if p_list.returncode == 0 and p_list.stdout.strip():
                                extracted_files = [f.replace('/tmp/extracted/', '') for f in p_list.stdout.strip().split('\n')]
                                extracted_files = [f for f in extracted_files if f]  # Remove empty strings
                                extracted_count = len(extracted_files)
                                self.log_hdfs(f'  📦 Found {extracted_count} file(s) in archive', 'info')
                                
                                # Show first few files
                                for i, ef in enumerate(extracted_files[:5]):
                                    self.log_hdfs(f'    - {ef}', 'info')
                                if extracted_count > 5:
                                    self.log_hdfs(f'    ... and {extracted_count - 5} more', 'info')
                                
                                # Upload extracted files instead
                                upload_source = '/tmp/extracted'
                                files_to_upload = extracted_files  # List of actual filenames
                            else:
                                self.log_hdfs(f'  ⚠️ No files found after extraction', 'error')
                                upload_source = '/tmp'
                                files_to_upload = [filename]  # Fallback to original
                        else:
                            self.log_hdfs(f'  ⚠️ Extraction failed: {p_extract.stderr[:100]}', 'error')
                            self.log_hdfs(f'  💡 Uploading original archive instead', 'info')
                    else:
                        self.log_hdfs(f'  ⚠️ Unsupported archive format', 'error')
                
                # Step 2: Upload to HDFS
                if isinstance(files_to_upload, list) and len(files_to_upload) > 0 and files_to_upload != [filename]:
                    # Upload multiple extracted files
                    self.log_hdfs(f'  📤 Uploading {len(files_to_upload)} extracted file(s) to HDFS: {hdfs_path}/', 'info')
                    
                    # Use shell command with wildcard for better handling
                    cmd2_shell = f'hadoop fs -put -f {upload_source}/* {hdfs_path}/'
                    cmd2 = ['docker', 'exec', container, 'sh', '-c', cmd2_shell]
                    
                    p2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=upload_timeout)
                    if p2.returncode != 0:
                        self.log_hdfs(f'  ❌ HDFS upload failed: {p2.stderr}', 'error')
                        self.update_tree_status(idx, 'Failed - HDFS')
                        # Cleanup
                        subprocess.run(['docker', 'exec', container, 'rm', '-rf', '/tmp/extracted', f'/tmp/{filename}'], 
                                     capture_output=True, timeout=5)
                        continue
                else:
                    # Upload single file
                    cmd2 = ['docker', 'exec', container, 'hadoop', 'fs', '-put', '-f', 
                           f'{upload_source}/{filename}', hdfs_path]
                    self.log_hdfs(f'  📤 Uploading to HDFS: {hdfs_path}/{filename}', 'info')
                    
                    p2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=upload_timeout)
                    if p2.returncode != 0:
                        self.log_hdfs(f'  ❌ HDFS upload failed: {p2.stderr}', 'error')
                        self.update_tree_status(idx, 'Failed - HDFS')
                        # Cleanup
                        subprocess.run(['docker', 'exec', container, 'rm', '-rf', '/tmp/extracted', f'/tmp/{filename}'], 
                                     capture_output=True, timeout=5)
                        continue
                
                self.log_hdfs(f'  ✅ Uploaded to HDFS', 'success')
                
                # Cleanup temp files
                cmd3 = ['docker', 'exec', container, 'rm', '-rf', '/tmp/extracted', f'/tmp/{filename}']
                subprocess.run(cmd3, capture_output=True, timeout=5)
                
                # Delete archive from HDFS if option enabled and archive was extracted
                is_extracted = isinstance(files_to_upload, list) and len(files_to_upload) > 0 and files_to_upload != [filename]
                if is_archive and auto_extract and delete_after and is_extracted:
                    self.log_hdfs(f'  🗑️ Deleting archive from HDFS...', 'info')
                    cmd_del = ['docker', 'exec', container, 'hadoop', 'fs', '-rm', '-f', f'{hdfs_path}/{filename}']
                    subprocess.run(cmd_del, capture_output=True, timeout=10)
                    self.log_hdfs(f'  ✅ Archive deleted, only extracted files remain', 'success')
                
                # Success
                self.log_hdfs(f'  🎉 Successfully uploaded!', 'success')
                self.update_tree_status(idx, 'Completed')
                
            except subprocess.TimeoutExpired:
                self.log_hdfs(f'  ⏱️ Timeout! File is too large or slow network', 'error')
                self.log_hdfs(f'  💡 Try splitting large files or increase timeout', 'info')
                self.update_tree_status(idx, 'Timeout')
                # Try cleanup
                try:
                    subprocess.run(['docker', 'exec', container, 'rm', '-rf', '/tmp/extracted', f'/tmp/{filename}'], 
                                 capture_output=True, timeout=5)
                except:
                    pass
            except Exception as e:
                self.log_hdfs(f'  ❌ Error: {e}', 'error')
                self.update_tree_status(idx, 'Error')
        
        # Finished
        self.upload_progress['value'] = 100
        self.progress_label['text'] = 'Upload completed!'
        self.log_hdfs('\n' + '=' * 60, 'info')
        self.log_hdfs('🎉 Batch upload finished!', 'success')
        self.log_hdfs('=' * 60, 'info')
        
        self.is_uploading = False
        self.upload_btn['state'] = tk.NORMAL
        self.stop_btn['state'] = tk.DISABLED
        self.add_files_btn['state'] = tk.NORMAL
        self.add_folder_btn['state'] = tk.NORMAL
        self.update_status('✅ HDFS upload completed')
    
    def update_tree_status(self, index, status):
        """Update status in treeview"""
        items = self.file_tree.get_children()
        if index < len(items):
            item = items[index]
            values = list(self.file_tree.item(item, 'values'))
            values[3] = status
            self.file_tree.item(item, values=values)
    
    def stop_upload(self):
        """Stop ongoing upload"""
        if messagebox.askyesno('Confirm', 'Stop uploading?'):
            self.is_uploading = False
            self.log_hdfs('⏹️ Stopping upload...', 'info')
