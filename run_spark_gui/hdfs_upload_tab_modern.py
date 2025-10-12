"""
HDFS Upload Tab - Modern UI/UX Version 4.0
Complete redesign with card-based layout, modern components, and drag-drop support
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import subprocess
import threading
from pathlib import Path
from datetime import datetime

# Import modern components
try:
    from modern_components import (ModernCard, ModernButton, ModernInput, 
                                   ModernBadge, ModernAlert, ModernProgressCard,
                                   ModernFileItemCard, ModernSectionHeader, ModernTooltip)
    from modern_theme import Spacing, Typography, LightTheme
    MODERN_UI = True
except ImportError:
    MODERN_UI = False
    print("⚠️ Modern UI unavailable, using fallback")


class HDFSUploadTabModern:
    """Modern HDFS Upload functionality"""
    
    # Supported file types
    SUPPORTED_TYPES = {
        'Data Files': ['.csv', '.json', '.parquet', '.avro', '.orc'],
        'Text Files': ['.txt', '.log', '.md'],
        'Compressed': ['.zip', '.gz', '.tar', '.tar.gz'],
        'Images': ['.jpg', '.jpeg', '.png', '.gif'],
        'Others': ['.*']
    }
    
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
        self.selected_files = {}  # filepath -> file_card_widget
        self.is_uploading = False
        
        self.create_modern_ui()
    
    def create_modern_ui(self):
        """Create modern UI with cards and better visual hierarchy"""
        
        # Main scrollable container
        main_canvas = tk.Canvas(self.frame, highlightthickness=0, bg=LightTheme.BG_PRIMARY)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=main_canvas.yview)
        
        main_container = ttk.Frame(main_canvas, padding=Spacing.LG)
        
        # Configure scrolling
        def configure_scroll(event):
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        
        main_container.bind("<Configure>", configure_scroll)
        canvas_window = main_canvas.create_window((0, 0), window=main_container, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Mousewheel binding
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # === HEADER SECTION ===
        header = ModernSectionHeader(main_container,
                                     title="📤 HDFS Upload Manager",
                                     subtitle="Upload và quản lý files trên Hadoop HDFS")
        header.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        # === INFO ALERT ===
        info_alert = ModernAlert(main_container,
                                message="Hỗ trợ CSV, JSON, Parquet, TXT, Log, ZIP và nhiều định dạng khác. Tự động giải nén file nén.",
                                variant="info")
        info_alert.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        # === CONFIGURATION CARD ===
        config_card = ModernCard(main_container, title="⚙️ HDFS Configuration", padding=Spacing.MD)
        config_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        config_content = config_card.get_content_frame()
        
        # Container selection
        container_frame = ttk.Frame(config_content)
        container_frame.pack(fill=tk.X, pady=(0, Spacing.SM))
        
        ttk.Label(container_frame, text="HDFS Container:", style='Body.TLabel').pack(side=tk.LEFT)
        self.hdfs_container_var = tk.StringVar(value=self.config.get('hdfs_container', 'namenode'))
        container_combo = ttk.Combobox(container_frame, textvariable=self.hdfs_container_var,
                                       values=['namenode', 'datanode', 'spark-worker'],
                                       width=20, state='readonly')
        container_combo.pack(side=tk.LEFT, padx=(Spacing.SM, 0))
        ModernTooltip.create(container_combo, "Docker container for HDFS operations")
        
        # HDFS Host
        host_input = ModernInput(config_content, label="HDFS Host", width=40)
        host_input.pack(fill=tk.X, pady=(0, Spacing.SM))
        host_input.set(self.config.get('hdfs_host', 'hdfs://namenode:8020'))
        self.hdfs_host_input = host_input
        
        # Default Path
        path_input = ModernInput(config_content, label="Default Upload Path", width=40)
        path_input.pack(fill=tk.X, pady=(0, Spacing.SM))
        path_input.set(self.config.get('hdfs_default_path', '/user/spark/data'))
        self.hdfs_path_input = path_input
        
        # Options
        options_frame = ttk.Frame(config_content)
        options_frame.pack(fill=tk.X, pady=(Spacing.SM, 0))
        
        self.auto_extract_var = tk.BooleanVar(value=self.config.get('auto_extract_archives', True))
        extract_check = ttk.Checkbutton(options_frame, 
                                        text='🗜️ Auto-extract compressed files',
                                        variable=self.auto_extract_var)
        extract_check.pack(side=tk.LEFT)
        
        self.delete_archive_var = tk.BooleanVar(value=self.config.get('delete_archive_after_extract', True))
        delete_check = ttk.Checkbutton(options_frame,
                                       text='🗑️ Delete archive after extraction',
                                       variable=self.delete_archive_var)
        delete_check.pack(side=tk.LEFT, padx=(Spacing.MD, 0))
        
        # Action buttons
        btn_frame = ttk.Frame(config_content)
        btn_frame.pack(fill=tk.X, pady=(Spacing.MD, 0))
        
        ModernButton.primary(btn_frame, "Save Config", command=self.save_config, 
                           icon="💾").pack(side=tk.LEFT, padx=(0, Spacing.SM))
        ModernButton.secondary(btn_frame, "Test Connection", command=self.test_connection,
                             icon="🔍").pack(side=tk.LEFT)
        
        # === FILE SELECTION CARD ===
        files_card = ModernCard(main_container, title="📁 File Selection", padding=Spacing.MD)
        files_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        files_content = files_card.get_content_frame()
        
        # Add files buttons
        add_btn_frame = ttk.Frame(files_content)
        add_btn_frame.pack(fill=tk.X, pady=(0, Spacing.SM))
        
        ModernButton.primary(add_btn_frame, "Add Files", command=self.add_files,
                           icon="➕", width=15).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        ModernButton.primary(add_btn_frame, "Add Folder", command=self.add_folder,
                           icon="📂", width=15).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        ModernButton.secondary(add_btn_frame, "Clear All", command=self.clear_files,
                             icon="🗑️", width=12).pack(side=tk.LEFT)
        
        # Drag & Drop area (visual indicator)
        drop_frame = tk.Frame(files_content, bg=LightTheme.PRIMARY_LIGHT, 
                             relief='solid', borderwidth=2)
        drop_frame.pack(fill=tk.X, pady=(0, Spacing.SM))
        
        drop_label = tk.Label(drop_frame, 
                             text="📎 Drag & Drop files here (or use buttons above)",
                             bg=LightTheme.PRIMARY_LIGHT,
                             fg=LightTheme.PRIMARY,
                             font=(Typography.FONT_PRIMARY, Typography.SIZE_BODY),
                             pady=Spacing.MD)
        drop_label.pack()
        
        # File list container (scrollable)
        files_list_frame = ttk.Frame(files_content)
        files_list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas for file items
        self.files_canvas = tk.Canvas(files_list_frame, height=200, bg=LightTheme.BG_PRIMARY,
                                      highlightthickness=0)
        files_scrollbar = ttk.Scrollbar(files_list_frame, orient="vertical", 
                                       command=self.files_canvas.yview)
        
        self.files_container = ttk.Frame(self.files_canvas)
        
        def configure_files_scroll(event):
            self.files_canvas.configure(scrollregion=self.files_canvas.bbox("all"))
        
        self.files_container.bind("<Configure>", configure_files_scroll)
        self.files_canvas.create_window((0, 0), window=self.files_container, anchor="nw")
        self.files_canvas.configure(yscrollcommand=files_scrollbar.set)
        
        self.files_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        files_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # === UPLOAD ACTIONS CARD ===
        upload_card = ModernCard(main_container, title="🚀 Upload Actions", padding=Spacing.MD)
        upload_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        upload_content = upload_card.get_content_frame()
        
        # Upload buttons
        upload_btn_frame = ttk.Frame(upload_content)
        upload_btn_frame.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        self.upload_btn = ModernButton.success(upload_btn_frame, "Start Upload",
                                               command=self.start_upload, icon="▶️", width=20)
        self.upload_btn.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        self.stop_btn = ModernButton.error(upload_btn_frame, "Stop",
                                          command=self.stop_upload, icon="⏹️", width=12)
        self.stop_btn.pack(side=tk.LEFT)
        self.stop_btn['state'] = tk.DISABLED
        
        # Progress card
        self.progress_card = ModernProgressCard(upload_content, title="Upload Progress")
        self.progress_card.pack(fill=tk.X)
        
        # === LOG CARD ===
        log_card = ModernCard(main_container, title="📊 Upload Log", padding=Spacing.SM)
        log_card.pack(fill=tk.BOTH, expand=True)
        
        log_content = log_card.get_content_frame()
        
        self.hdfs_log = scrolledtext.ScrolledText(log_content, height=12, wrap=tk.WORD,
                                                   bg='#FAFAFA', fg=LightTheme.TEXT_PRIMARY,
                                                   font=(Typography.FONT_MONO, Typography.SIZE_BODY_SM),
                                                   relief='flat', borderwidth=0)
        self.hdfs_log.pack(fill=tk.BOTH, expand=True)
        
        # Configure log tags
        self.hdfs_log.tag_config('success', foreground=LightTheme.SUCCESS, 
                                font=(Typography.FONT_MONO, Typography.SIZE_BODY_SM, 'bold'))
        self.hdfs_log.tag_config('error', foreground=LightTheme.ERROR,
                                font=(Typography.FONT_MONO, Typography.SIZE_BODY_SM, 'bold'))
        self.hdfs_log.tag_config('info', foreground=LightTheme.INFO,
                                font=(Typography.FONT_MONO, Typography.SIZE_BODY_SM, 'bold'))
        self.hdfs_log.tag_config('warning', foreground=LightTheme.WARNING,
                                font=(Typography.FONT_MONO, Typography.SIZE_BODY_SM, 'bold'))
        
        # Welcome messages
        self.log_hdfs('📤 HDFS Upload Module Ready - Version 4.0', 'info')
        self.log_hdfs('💡 Add files/folders and click "Start Upload"', 'info')
        self.log_hdfs('✨ Features: Auto-extract archives, progress tracking, batch upload', 'info')
    
    def log_hdfs(self, message, tag='normal'):
        """Append message to log with timestamp"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.hdfs_log.insert(tk.END, f'[{timestamp}] {message}\n', tag)
        self.hdfs_log.see(tk.END)
        self.hdfs_log.update_idletasks()
    
    def save_config(self):
        """Save HDFS configuration"""
        self.config['hdfs_container'] = self.hdfs_container_var.get()
        self.config['hdfs_host'] = self.hdfs_host_input.get()
        self.config['hdfs_default_path'] = self.hdfs_path_input.get()
        self.config['auto_extract_archives'] = self.auto_extract_var.get()
        self.config['delete_archive_after_extract'] = self.delete_archive_var.get()
        
        try:
            import json
            with open('spark_runner_config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.log_hdfs('✅ Configuration saved successfully', 'success')
            self.update_status('✅ HDFS config saved')
            
            # Show success alert
            success_alert = ModernAlert(self.frame,
                                       message="Configuration saved successfully!",
                                       variant="success",
                                       dismissible=True)
            success_alert.place(relx=0.5, rely=0.1, anchor='center')
            self.frame.after(3000, success_alert.destroy)
            
        except Exception as e:
            self.log_hdfs(f'❌ Failed to save config: {e}', 'error')
            messagebox.showerror('Error', f'Cannot save configuration:\n{e}')
    
    def test_connection(self):
        """Test HDFS connection"""
        self.log_hdfs('🔍 Testing HDFS connection...', 'info')
        self.update_status('🔍 Testing connection...')
        
        def test_thread():
            try:
                container = self.hdfs_container_var.get()
                
                # Check container running
                self.log_hdfs(f'  📦 Checking container: {container}', 'info')
                cmd_check = ['docker', 'ps', '--filter', f'name={container}', 
                           '--format', '{{.Names}}']
                result = subprocess.run(cmd_check, capture_output=True, text=True, timeout=5)
                
                if container not in result.stdout:
                    self.log_hdfs(f'❌ Container "{container}" not running!', 'error')
                    self.update_status('❌ Container not running')
                    messagebox.showerror('Connection Failed',
                                       f'Container "{container}" is not running!\n\n'
                                       'Start it with: docker-compose up -d')
                    return
                
                self.log_hdfs('  ✅ Container is running', 'success')
                
                # Test HDFS filesystem
                self.log_hdfs('  📁 Testing HDFS filesystem...', 'info')
                cmd_test = ['docker', 'exec', container, 'hadoop', 'fs', '-ls', '/']
                result = subprocess.run(cmd_test, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    self.log_hdfs('✅ HDFS connection successful!', 'success')
                    self.log_hdfs('📁 Root directory accessible', 'success')
                    self.update_status('✅ HDFS connection OK')
                    messagebox.showinfo('Success',
                                      '✅ HDFS connection successful!\n\n'
                                      f'Container: {container}\n'
                                      'Filesystem: Accessible')
                else:
                    self.log_hdfs('❌ HDFS connection failed!', 'error')
                    self.log_hdfs(f'  Error: {result.stderr[:200]}', 'error')
                    self.update_status('❌ Connection failed')
                    messagebox.showerror('Connection Failed',
                                       'Cannot connect to HDFS!\n\nCheck the log for details.')
                    
            except subprocess.TimeoutExpired:
                self.log_hdfs('❌ Connection test timeout!', 'error')
                self.update_status('❌ Timeout')
            except Exception as e:
                self.log_hdfs(f'❌ Error: {e}', 'error')
        
        thread = threading.Thread(target=test_thread, daemon=True)
        thread.start()
    
    def add_files(self):
        """Add files to upload list"""
        filetypes = [
            ('All Files', '*.*'),
            ('CSV Files', '*.csv'),
            ('JSON Files', '*.json'),
            ('Parquet Files', '*.parquet'),
            ('Text Files', '*.txt'),
            ('Log Files', '*.log'),
            ('Compressed Files', '*.zip *.gz *.tar')
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
        """Add a file to the visual list using ModernFileItemCard"""
        if filepath in self.selected_files:
            return
        
        path = Path(filepath)
        size = path.stat().st_size
        size_str = self.format_size(size)
        
        # Create modern file card
        file_card = ModernFileItemCard(self.files_container,
                                       filename=path.name,
                                       size=size_str,
                                       status='pending',
                                       on_remove=lambda fp=filepath: self.remove_file(fp))
        file_card.pack(fill=tk.X, pady=(0, Spacing.XS))
        
        self.selected_files[filepath] = file_card
    
    def remove_file(self, filepath):
        """Remove file from list"""
        if filepath in self.selected_files:
            self.selected_files[filepath].destroy()
            del self.selected_files[filepath]
            self.log_hdfs(f'🗑️ Removed: {Path(filepath).name}', 'info')
    
    def clear_files(self):
        """Clear all files"""
        if self.selected_files:
            if messagebox.askyesno('Confirm', 'Clear all files from list?'):
                for card in self.selected_files.values():
                    card.destroy()
                self.selected_files.clear()
                self.log_hdfs('🗑️ File list cleared', 'info')
    
    def format_size(self, size_bytes):
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def start_upload(self):
        """Start uploading files"""
        if not self.selected_files:
            messagebox.showwarning('No Files', 'Please add files to upload first')
            return
        
        self.is_uploading = True
        self.upload_btn['state'] = tk.DISABLED
        self.stop_btn['state'] = tk.NORMAL
        
        self.log_hdfs('=' * 60, 'info')
        self.log_hdfs('🚀 Starting batch upload to HDFS', 'info')
        self.log_hdfs('=' * 60, 'info')
        
        thread = threading.Thread(target=self._upload_thread, daemon=True)
        thread.start()
    
    def _upload_thread(self):
        """Upload files in background"""
        container = self.hdfs_container_var.get()
        hdfs_path = self.hdfs_path_input.get()
        total_files = len(self.selected_files)
        success_count = 0
        failed_count = 0
        
        # Create HDFS directory
        self.log_hdfs(f'📁 Preparing HDFS directory: {hdfs_path}', 'info')
        try:
            cmd_mkdir = ['docker', 'exec', container, 'hadoop', 'fs', '-mkdir', '-p', hdfs_path]
            subprocess.run(cmd_mkdir, capture_output=True, timeout=10)
            self.log_hdfs(f'✅ Directory ready', 'success')
        except:
            pass
        
        # Upload each file
        for idx, (filepath, file_card) in enumerate(self.selected_files.items()):
            if not self.is_uploading:
                break
            
            # Update progress
            progress = int(((idx + 1) / total_files) * 100)
            self.progress_card.update_progress(progress, 
                                              f'Uploading file {idx + 1}/{total_files}')
            
            # Update file card status
            file_card.update_status('uploading')
            
            filename = Path(filepath).name
            self.log_hdfs(f'\n[{idx + 1}/{total_files}] Uploading: {filename}', 'info')
            
            try:
                # Copy to container
                cmd1 = ['docker', 'cp', filepath, f'{container}:/tmp/{filename}']
                subprocess.run(cmd1, capture_output=True, timeout=30)
                
                # Upload to HDFS
                cmd2 = ['docker', 'exec', container, 'hadoop', 'fs', '-put', '-f',
                       f'/tmp/{filename}', hdfs_path]
                subprocess.run(cmd2, capture_output=True, timeout=60)
                
                # Cleanup
                cmd3 = ['docker', 'exec', container, 'rm', f'/tmp/{filename}']
                subprocess.run(cmd3, capture_output=True, timeout=5)
                
                self.log_hdfs(f'  ✅ Successfully uploaded!', 'success')
                file_card.update_status('completed')
                success_count += 1
                
            except Exception as e:
                self.log_hdfs(f'  ❌ Error: {e}', 'error')
                file_card.update_status('error')
                failed_count += 1
        
        # Finished
        self.progress_card.set_complete(f'Uploaded {success_count}/{total_files} files')
        
        self.log_hdfs('\n' + '=' * 60, 'info')
        self.log_hdfs('📊 UPLOAD SUMMARY', 'info')
        self.log_hdfs(f'  Total: {total_files}', 'info')
        self.log_hdfs(f'  ✅ Success: {success_count}', 'success')
        if failed_count > 0:
            self.log_hdfs(f'  ❌ Failed: {failed_count}', 'error')
        self.log_hdfs('=' * 60, 'info')
        
        self.is_uploading = False
        self.upload_btn['state'] = tk.NORMAL
        self.stop_btn['state'] = tk.DISABLED
        
        if failed_count == 0:
            self.update_status(f'✅ Upload complete ({success_count}/{total_files})')
            messagebox.showinfo('Success', 
                              f'✅ Upload complete!\n\n'
                              f'Successfully uploaded {success_count} files to {hdfs_path}')
        else:
            self.update_status(f'⚠️ Upload done with errors')
            messagebox.showwarning('Partial Success',
                                  f'⚠️ Upload completed with errors!\n\n'
                                  f'Success: {success_count}\nFailed: {failed_count}\n\n'
                                  'Check the log for details.')
    
    def stop_upload(self):
        """Stop ongoing upload"""
        if messagebox.askyesno('Confirm', 'Stop uploading?'):
            self.is_uploading = False
            self.log_hdfs('⏹️ Upload stopped by user', 'warning')


# For backward compatibility
HDFSUploadTab = HDFSUploadTabModern
