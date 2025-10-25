"""
Docker Compose Editor - V4 Clean Professional Design
Edit docker-compose.yml with syntax highlighting and validation
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import os
import yaml
from pathlib import Path
from datetime import datetime


class CleanButton:
    """Modern flat button"""
    STYLES = {
        'primary': {'bg': '#0969DA', 'hover': '#0860CA', 'fg': '#FFFFFF'},
        'success': {'bg': '#1A7F37', 'hover': '#1A7F37', 'fg': '#FFFFFF'},
        'danger': {'bg': '#CF222E', 'hover': '#A40E26', 'fg': '#FFFFFF'},
        'secondary': {'bg': '#F6F8FA', 'hover': '#F3F4F6', 'fg': '#24292F'},
    }
    
    def __init__(self, parent, text, style='primary', command=None, width=100):
        self.frame = tk.Frame(parent, bg=parent.cget('bg'))
        self.style_config = self.STYLES[style]
        self.command = command
        self.default_bg = self.style_config['bg']
        self.hover_bg = self.style_config['hover']
        
        self.label = tk.Label(
            self.frame, text=text,
            bg=self.default_bg, fg=self.style_config['fg'],
            font=('Segoe UI', 9), padx=16, pady=6,
            cursor='hand2', relief=tk.FLAT
        )
        self.label.pack(fill=tk.BOTH, expand=True)
        
        self.label.bind('<Button-1>', self._on_click)
        self.label.bind('<Enter>', lambda e: self.label.config(bg=self.hover_bg))
        self.label.bind('<Leave>', lambda e: self.label.config(bg=self.default_bg))
    
    def _on_click(self, event):
        if self.command:
            self.command()
    
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        self.frame.grid(**kwargs)


class SectionCard(tk.Frame):
    """Clean section card"""
    def __init__(self, parent, title="", **kwargs):
        super().__init__(parent, bg='#FFFFFF', relief=tk.FLAT,
                        borderwidth=1, highlightthickness=1,
                        highlightbackground='#D0D7DE', **kwargs)
        
        if title:
            title_frame = tk.Frame(self, bg='#F6F8FA', height=32)
            title_frame.pack(fill=tk.X, side=tk.TOP)
            title_frame.pack_propagate(False)
            
            title_label = tk.Label(
                title_frame, text=title,
                font=('Segoe UI', 9, 'bold'),
                bg='#F6F8FA', fg='#24292F', anchor='w'
            )
            title_label.pack(side=tk.LEFT, padx=12, pady=6)
        
        self.content = tk.Frame(self, bg='#FFFFFF')
        self.content.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
    
    def get_content(self):
        return self.content


class DockerComposeEditorV4:
    """Docker Compose YAML Editor with validation"""
    
    def __init__(self, parent_frame, config, status_callback, log_callback):
        self.frame = parent_frame
        self.config = config
        self.update_status = status_callback
        self.append_log = log_callback
        
        self.current_file = config.get('compose_file', 'docker-compose.yml')
        self.modified = False
        
        self.create_ui()
        self.load_file()
    
    def create_ui(self):
        """Create Clean Professional UI"""
        # Main container
        main_bg = tk.Frame(self.frame, bg='#F6F8FA')
        main_bg.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Top toolbar
        toolbar = tk.Frame(main_bg, bg='#F6F8FA', height=48)
        toolbar.pack(fill=tk.X, side=tk.TOP, pady=(0, 12))
        
        # File path
        path_frame = tk.Frame(toolbar, bg='#F6F8FA')
        path_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(path_frame, text='📄 File:', font=('Segoe UI', 9, 'bold'),
                bg='#F6F8FA', fg='#24292F').pack(side=tk.LEFT, padx=(0, 8))
        
        self.file_var = tk.StringVar(value=self.current_file)
        file_entry = tk.Entry(
            path_frame, textvariable=self.file_var,
            font=('Segoe UI', 9), bg='#FFFFFF',
            relief=tk.SOLID, borderwidth=1,
            highlightthickness=1, highlightbackground='#D0D7DE'
        )
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
        
        # Action buttons
        btn_frame = tk.Frame(toolbar, bg='#F6F8FA')
        btn_frame.pack(side=tk.RIGHT, padx=(12, 0))
        
        CleanButton(btn_frame, '📂 Browse', 'secondary', self.browse_file).pack(side=tk.LEFT, padx=3)
        CleanButton(btn_frame, '💾 Save', 'success', self.save_file).pack(side=tk.LEFT, padx=3)
        CleanButton(btn_frame, '🔄 Reload', 'secondary', self.reload_file).pack(side=tk.LEFT, padx=3)
        CleanButton(btn_frame, '✓ Validate', 'primary', self.validate_yaml).pack(side=tk.LEFT, padx=3)
        
        # Two column layout - Editor (60%) | Preview/Info (40%)
        content_frame = tk.Frame(main_bg, bg='#F6F8FA')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        content_frame.grid_columnconfigure(0, weight=60)
        content_frame.grid_columnconfigure(1, weight=40)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Left: Editor
        editor_card = SectionCard(content_frame, '✏️ Docker Compose Editor')
        editor_card.grid(row=0, column=0, sticky='nsew', padx=(0, 8))
        editor_content = editor_card.get_content()
        
        # Line numbers frame
        editor_frame = tk.Frame(editor_content, bg='#FFFFFF')
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Line numbers
        self.line_numbers = tk.Text(
            editor_frame, width=4,
            font=('Consolas', 9),
            bg='#F6F8FA', fg='#57606A',
            relief=tk.FLAT, borderwidth=0,
            state='disabled', takefocus=0,
            padx=5, pady=8
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Editor with scrollbar
        editor_scroll = tk.Scrollbar(editor_frame)
        editor_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.editor = tk.Text(
            editor_frame,
            wrap=tk.NONE,
            font=('Consolas', 9),
            bg='#FFFFFF', fg='#24292F',
            relief=tk.FLAT, borderwidth=0,
            padx=8, pady=8,
            undo=True, maxundo=-1,
            yscrollcommand=editor_scroll.set
        )
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        editor_scroll.config(command=self.editor.yview)
        
        # Syntax highlighting tags
        self.editor.tag_config('key', foreground='#0550AE', font=('Consolas', 9, 'bold'))
        self.editor.tag_config('string', foreground='#0A3069')
        self.editor.tag_config('number', foreground='#8250DF')
        self.editor.tag_config('comment', foreground='#6E7781', font=('Consolas', 9, 'italic'))
        self.editor.tag_config('bool', foreground='#CF222E', font=('Consolas', 9, 'bold'))
        
        # Track modifications
        self.editor.bind('<<Modified>>', self.on_modified)
        self.editor.bind('<KeyRelease>', self.update_line_numbers)
        
        # Right: Info panel
        info_card = SectionCard(content_frame, 'ℹ️ Information & Validation')
        info_card.grid(row=0, column=1, sticky='nsew', padx=(8, 0))
        info_content = info_card.get_content()
        
        # Status indicators
        status_frame = tk.Frame(info_content, bg='#FFFFFF')
        status_frame.pack(fill=tk.X, pady=(0, 12))
        
        # Modified indicator
        self.modified_label = tk.Label(
            status_frame, text='● Saved',
            font=('Segoe UI', 9),
            bg='#DFF6DD', fg='#1A7F37',
            padx=8, pady=4
        )
        self.modified_label.pack(side=tk.LEFT, padx=(0, 8))
        
        # Line count
        self.line_count_label = tk.Label(
            status_frame, text='Lines: 0',
            font=('Segoe UI', 9),
            bg='#F6F8FA', fg='#57606A',
            padx=8, pady=4
        )
        self.line_count_label.pack(side=tk.LEFT)
        
        # Validation output
        tk.Label(info_content, text='Validation Results:',
                font=('Segoe UI', 9, 'bold'),
                bg='#FFFFFF', fg='#24292F', anchor='w').pack(fill=tk.X, pady=(0, 8))
        
        self.validation_text = scrolledtext.ScrolledText(
            info_content,
            height=10,
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg='#F6F8FA', fg='#24292F',
            relief=tk.SOLID, borderwidth=1,
            highlightthickness=1, highlightbackground='#D0D7DE',
            padx=8, pady=8
        )
        self.validation_text.pack(fill=tk.BOTH, expand=True, pady=(0, 12))
        
        # Quick actions
        tk.Label(info_content, text='Quick Actions:',
                font=('Segoe UI', 9, 'bold'),
                bg='#FFFFFF', fg='#24292F', anchor='w').pack(fill=tk.X, pady=(0, 8))
        
        actions_frame = tk.Frame(info_content, bg='#FFFFFF')
        actions_frame.pack(fill=tk.X)
        
        CleanButton(actions_frame, '🚀 Start Compose', 'success',
                   self.start_compose).pack(fill=tk.X, pady=2)
        CleanButton(actions_frame, '⏹️ Stop Compose', 'danger',
                   self.stop_compose).pack(fill=tk.X, pady=2)
        CleanButton(actions_frame, '📊 View Services', 'primary',
                   self.view_services).pack(fill=tk.X, pady=2)
        CleanButton(actions_frame, '💾 Backup File', 'secondary',
                   self.backup_file).pack(fill=tk.X, pady=2)
        
        # Keyboard shortcuts
        self.editor.bind('<Control-s>', lambda e: self.save_file())
        self.editor.bind('<Control-S>', lambda e: self.save_file())
        self.editor.bind('<Control-r>', lambda e: self.reload_file())
        self.editor.bind('<Control-R>', lambda e: self.reload_file())
        self.editor.bind('<F5>', lambda e: self.validate_yaml())
    
    def load_file(self):
        """Load docker-compose.yml file or create template if not exists"""
        filepath = self.file_var.get()
        
        # Check if file exists
        if not os.path.exists(filepath):
            self.append_log(f'⚠️ File not found: {filepath}', 'warning')
            self.validation_text.delete('1.0', tk.END)
            self.validation_text.insert('1.0', f'⚠️ File not found: {filepath}\n\n')
            self.validation_text.insert(tk.END, 'Would you like to:\n')
            self.validation_text.insert(tk.END, '  1. Create a new docker-compose.yml template\n')
            self.validation_text.insert(tk.END, '  2. Browse for existing file\n\n')
            self.validation_text.insert(tk.END, 'Click "Browse" to select existing file or\n')
            self.validation_text.insert(tk.END, 'Click "Save" to create new file with template.')
            
            # Load default template
            template = """version: '3.8'

services:
  # Example service
  spark-master:
    image: bitnami/spark:latest
    container_name: spark-master
    environment:
      - SPARK_MODE=master
    ports:
      - "8080:8080"
      - "7077:7077"
    networks:
      - spark-network

  spark-worker:
    image: bitnami/spark:latest
    container_name: spark-worker
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://spark-master:7077
    depends_on:
      - spark-master
    networks:
      - spark-network

networks:
  spark-network:
    driver: bridge

volumes:
  spark-data:
"""
            self.editor.delete('1.0', tk.END)
            self.editor.insert('1.0', template)
            self.apply_syntax_highlighting()
            self.update_line_numbers()
            self.modified = True
            self.update_modified_indicator()
            return
        
        # File exists - load it
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.editor.delete('1.0', tk.END)
            self.editor.insert('1.0', content)
            self.apply_syntax_highlighting()
            self.update_line_numbers()
            
            self.modified = False
            self.update_modified_indicator()
            
            self.append_log(f'✅ Loaded: {os.path.basename(filepath)}', 'success')
            self.validation_text.delete('1.0', tk.END)
            self.validation_text.insert('1.0', f'✅ File loaded successfully\n\n')
            self.validation_text.insert(tk.END, f'Path: {filepath}\n')
            self.validation_text.insert(tk.END, f'Size: {len(content)} bytes\n')
            self.validation_text.insert(tk.END, f'Lines: {content.count(chr(10)) + 1}\n\n')
            self.validation_text.insert(tk.END, 'Ready to edit...\n\n')
            self.validation_text.insert(tk.END, 'Press F5 to validate YAML\n')
            self.validation_text.insert(tk.END, 'Press Ctrl+S to save')
            
        except Exception as e:
            self.append_log(f'❌ Error loading file: {e}', 'error')
            messagebox.showerror('Load Error', f'Failed to load file:\n{e}')
            import traceback
            traceback.print_exc()
    
    def save_file(self):
        """Save docker-compose.yml file and update config"""
        filepath = self.file_var.get()
        
        try:
            content = self.editor.get('1.0', tk.END)
            
            # Validate before saving
            try:
                yaml.safe_load(content)
            except yaml.YAMLError as e:
                if not messagebox.askyesno('Invalid YAML',
                                          f'YAML validation failed:\n{e}\n\nSave anyway?'):
                    return
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.modified = False
            self.update_modified_indicator()
            
            # Update config to use this file
            self.config['compose_file'] = filepath
            self.current_file = filepath
            
            self.append_log(f'💾 Saved: {os.path.basename(filepath)}', 'success')
            self.append_log(f'📄 Path: {filepath}', 'info')
            self.update_status(f'💾 File saved: {os.path.basename(filepath)}')
            
            messagebox.showinfo('Success', f'File saved successfully!\n\n{filepath}')
            
        except Exception as e:
            self.append_log(f'❌ Error saving file: {e}', 'error')
            messagebox.showerror('Save Error', f'Failed to save file:\n{e}')
    
    def reload_file(self):
        """Reload file from disk"""
        if self.modified:
            if not messagebox.askyesno('Unsaved Changes',
                                      'You have unsaved changes. Reload anyway?'):
                return
        self.load_file()
    
    def browse_file(self):
        """Browse for docker-compose.yml file"""
        filepath = filedialog.askopenfilename(
            title='Select docker-compose.yml',
            filetypes=[('YAML files', '*.yml *.yaml'), ('All files', '*.*')],
            initialdir=os.path.dirname(self.current_file)
        )
        
        if filepath:
            self.file_var.set(filepath)
            self.current_file = filepath
            self.config['compose_file'] = filepath
            self.load_file()
    
    def validate_yaml(self):
        """Validate YAML syntax"""
        content = self.editor.get('1.0', tk.END)
        self.validation_text.delete('1.0', tk.END)
        
        try:
            data = yaml.safe_load(content)
            
            self.validation_text.insert('1.0', '✅ YAML Syntax: VALID\n\n')
            self.validation_text.insert(tk.END, '📊 Structure Analysis:\n\n')
            
            if 'version' in data:
                self.validation_text.insert(tk.END, f"  • Version: {data['version']}\n")
            
            if 'services' in data:
                services = data['services']
                self.validation_text.insert(tk.END, f"  • Services: {len(services)}\n")
                for service_name in services.keys():
                    self.validation_text.insert(tk.END, f"    - {service_name}\n")
            
            if 'networks' in data:
                self.validation_text.insert(tk.END, f"  • Networks: {len(data['networks'])}\n")
            
            if 'volumes' in data:
                self.validation_text.insert(tk.END, f"  • Volumes: {len(data['volumes'])}\n")
            
            self.validation_text.insert(tk.END, '\n✅ All checks passed!')
            self.append_log('✅ YAML validation passed', 'success')
            
        except yaml.YAMLError as e:
            self.validation_text.insert('1.0', f'❌ YAML Syntax Error:\n\n{str(e)}\n\n')
            self.validation_text.insert(tk.END, 'Please fix the syntax errors and try again.')
            self.append_log('❌ YAML validation failed', 'error')
        except Exception as e:
            self.validation_text.insert('1.0', f'❌ Validation Error:\n\n{str(e)}')
            self.append_log(f'❌ Validation error: {e}', 'error')
    
    def apply_syntax_highlighting(self):
        """Apply basic YAML syntax highlighting"""
        content = self.editor.get('1.0', tk.END)
        lines = content.split('\n')
        
        self.editor.tag_remove('key', '1.0', tk.END)
        self.editor.tag_remove('string', '1.0', tk.END)
        self.editor.tag_remove('number', '1.0', tk.END)
        self.editor.tag_remove('comment', '1.0', tk.END)
        self.editor.tag_remove('bool', '1.0', tk.END)
        
        for i, line in enumerate(lines, 1):
            # Comments
            if '#' in line:
                idx = line.index('#')
                self.editor.tag_add('comment', f'{i}.{idx}', f'{i}.end')
            
            # Keys (before colon)
            if ':' in line and not line.strip().startswith('#'):
                idx = line.index(':')
                start = len(line) - len(line.lstrip())
                self.editor.tag_add('key', f'{i}.{start}', f'{i}.{idx}')
            
            # Booleans
            for word in ['true', 'false', 'yes', 'no', 'on', 'off']:
                start_idx = 0
                while True:
                    pos = line.lower().find(word, start_idx)
                    if pos == -1:
                        break
                    self.editor.tag_add('bool', f'{i}.{pos}', f'{i}.{pos+len(word)}')
                    start_idx = pos + len(word)
    
    def update_line_numbers(self, event=None):
        """Update line numbers"""
        line_count = int(self.editor.index('end-1c').split('.')[0])
        
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        
        for i in range(1, line_count):
            self.line_numbers.insert(tk.END, f'{i}\n')
        
        self.line_numbers.config(state='disabled')
        self.line_count_label.config(text=f'Lines: {line_count-1}')
    
    def on_modified(self, event=None):
        """Track modifications"""
        if self.editor.edit_modified():
            self.modified = True
            self.update_modified_indicator()
            self.editor.edit_modified(False)
    
    def update_modified_indicator(self):
        """Update modified status indicator"""
        if self.modified:
            self.modified_label.config(
                text='● Modified',
                bg='#FFF8C5', fg='#9A6700'
            )
        else:
            self.modified_label.config(
                text='● Saved',
                bg='#DFF6DD', fg='#1A7F37'
            )
    
    def start_compose(self):
        """Start docker-compose services with proactive cleanup"""
        filepath = self.file_var.get()
        
        if not os.path.exists(filepath):
            messagebox.showerror('File Not Found', f'File does not exist:\n{filepath}')
            return
        
        self.append_log('🚀 Starting docker-compose...', 'info')
        self.append_log(f'📄 Using: {os.path.basename(filepath)}', 'info')
        
        # Import backend functions
        from spark_backend import docker_compose_command
        import subprocess
        
        # Start compose directly (do not remove unrelated containers or volumes)
        self.append_log('ℹ️ Starting docker-compose (preserving volumes). If you need a full cleanup, use Clean.', 'info')
        returncode, stdout, stderr = docker_compose_command('up', filepath, self.append_log)
        
        if returncode == 0:
            self.append_log('✅ Docker Compose started successfully', 'success')
            messagebox.showinfo('Success', 'Docker Compose services started!')
            self.update_status('✅ Services running')
        else:
            self.append_log(f'❌ Failed to start: {stderr}', 'error')
            messagebox.showerror('Error', f'Failed to start services:\n{stderr}')
            self.update_status('❌ Start failed')
    
    def stop_compose(self):
        """Stop docker-compose services"""
        filepath = self.file_var.get()
        
        if not os.path.exists(filepath):
            messagebox.showerror('File Not Found', f'File does not exist:\n{filepath}')
            return
        
        if not messagebox.askyesno('Confirm', 'Stop all Docker Compose services?'):
            return
        
        self.append_log('⏹️ Stopping docker-compose...', 'warning')
        self.append_log(f'📄 Using: {os.path.basename(filepath)}', 'info')
        
        from spark_backend import docker_compose_command
        
        returncode, stdout, stderr = docker_compose_command('stop', filepath, self.append_log)
        
        if returncode == 0:
            self.append_log('✅ Docker Compose stopped', 'success')
            messagebox.showinfo('Success', 'Docker Compose services stopped!')
            self.update_status('⏹️ Services stopped')
        else:
            self.append_log(f'❌ Failed to stop: {stderr}', 'error')
            messagebox.showerror('Error', f'Failed to stop services:\n{stderr}')
            self.update_status('❌ Stop failed')
    
    def view_services(self):
        """View running services"""
        filepath = self.file_var.get()
        
        if not os.path.exists(filepath):
            messagebox.showwarning('File Not Found', f'File does not exist:\n{filepath}')
            return
        
        self.append_log('📊 Checking services status...', 'info')
        self.append_log(f'📄 Using: {os.path.basename(filepath)}', 'info')
        
        import subprocess
        
        # Get running containers
        try:
            cmd = f'docker-compose -f "{filepath}" ps'
            self.append_log(f'💻 $ {cmd}', 'normal')
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            self.validation_text.delete('1.0', tk.END)
            self.validation_text.insert('1.0', '📊 Docker Compose Services Status:\n\n')
            
            if result.returncode == 0 and result.stdout.strip():
                self.validation_text.insert(tk.END, result.stdout)
                self.append_log('✅ Services status retrieved', 'success')
            else:
                self.validation_text.insert(tk.END, '  No services running or compose file not started.\n')
                self.validation_text.insert(tk.END, f'\n  Run "Start Compose" first.')
                self.append_log('ℹ️ No running services found', 'info')
                
        except Exception as e:
            self.validation_text.delete('1.0', tk.END)
            self.validation_text.insert('1.0', f'❌ Error: {e}')
            self.append_log(f'❌ Failed to get status: {e}', 'error')
        
        self.update_status('📊 Status checked')
    
    def backup_file(self):
        """Create backup of current file"""
        filepath = self.file_var.get()
        
        if not os.path.exists(filepath):
            messagebox.showwarning('No File', 'File does not exist yet.')
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f'{filepath}.backup_{timestamp}'
        
        try:
            import shutil
            shutil.copy2(filepath, backup_path)
            
            self.append_log(f'💾 Backup created: {os.path.basename(backup_path)}', 'success')
            messagebox.showinfo('Backup Created', f'Backup saved to:\n{backup_path}')
            
        except Exception as e:
            self.append_log(f'❌ Backup failed: {e}', 'error')
            messagebox.showerror('Backup Error', f'Failed to create backup:\n{e}')
