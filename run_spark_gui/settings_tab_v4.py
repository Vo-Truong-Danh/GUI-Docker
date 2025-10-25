"""
Settings Tab V4 - Port Configuration & System Settings
Professional Material Design 3 UI
Enhanced with YAML support and dynamic port management
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import yaml
from modern_theme import LightTheme, Spacing


# ============================================================================
# UI COMPONENTS (Local definitions)
# ============================================================================

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


class CleanButton(tk.Label):
    """Clean modern button with hover effect"""
    
    STYLES = {
        'primary': {'bg': '#1F6FEB', 'fg': '#FFFFFF', 'hover_bg': '#1557D2'},
        'secondary': {'bg': '#F6F8FA', 'fg': '#24292F', 'hover_bg': '#E8EBED'},
        'danger': {'bg': '#CF222E', 'fg': '#FFFFFF', 'hover_bg': '#A40E26'},
        'success': {'bg': '#1A7F37', 'fg': '#FFFFFF', 'hover_bg': '#116E2F'}
    }
    
    def __init__(self, parent, text, command, style='primary'):
        colors = self.STYLES.get(style, self.STYLES['primary'])
        self.command = command
        self.normal_bg = colors['bg']
        self.hover_bg = colors['hover_bg']
        
        super().__init__(
            parent,
            text=text,
            bg=self.normal_bg,
            fg=colors['fg'],
            font=('Segoe UI', 9),
            padx=16,
            pady=6,
            relief=tk.FLAT,
            cursor='hand2'
        )
        
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_click)
    
    def _on_enter(self, e):
        self.config(bg=self.hover_bg)
    
    def _on_leave(self, e):
        self.config(bg=self.normal_bg)
    
    def _on_click(self, e):
        if self.command:
            self.command()


class InfoCard(tk.Frame):
    """Info card with icon and message"""
    
    def __init__(self, parent, message, type='info'):
        colors = {
            'info': {'bg': '#DDF4FF', 'fg': '#0969DA'},
            'warning': {'bg': '#FFF8C5', 'fg': '#9A6700'},
            'error': {'bg': '#FFE4E6', 'fg': '#CF222E'},
            'success': {'bg': '#DDF4E6', 'fg': '#1A7F37'}
        }
        
        color = colors.get(type, colors['info'])
        
        super().__init__(parent, bg=color['bg'], relief=tk.FLAT, 
                        borderwidth=1, highlightthickness=1,
                        highlightbackground=color['fg'])
        
        label = tk.Label(
            self,
            text=message,
            bg=color['bg'],
            fg=color['fg'],
            font=('Segoe UI', 9),
            justify=tk.LEFT,
            padx=12,
            pady=8,
            wraplength=500
        )
        label.pack(fill=tk.BOTH, expand=True)


# ============================================================================
# SETTINGS TAB
# ============================================================================

class SettingsTabV4:
    """Settings tab for port configuration and system preferences"""
    
    def __init__(self, parent, config_file="spark_runner_config.json", append_log=None, global_save_config=None):
        self.frame = parent
        self.config_file = config_file
        self.append_log = append_log
        self.global_save_config = global_save_config  # Reference to global save_config function
        self.config = self.load_config()
        
        self.create_ui()
    
    def load_config(self):
        """Load configuration from JSON file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def save_config(self):
        """Save configuration to JSON file using global save_config if available"""
        try:
            # Use global save_config if provided (has backup and validation logic)
            if self.global_save_config:
                self.global_save_config(self.config)
            else:
                # Fallback to local save if global not available
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save config: {e}")
            return False
    
    def create_ui(self):
        """Create settings UI"""
        # Main container with padding
        main_container = tk.Frame(self.frame, bg='#F6F8FA')
        main_container.pack(fill=tk.BOTH, expand=True, padx=Spacing.XL, pady=Spacing.XL)
        
        # Title section
        title_frame = tk.Frame(main_container, bg='#F6F8FA')
        title_frame.pack(fill=tk.X, pady=(0, Spacing.LG))
        
        title_label = tk.Label(
            title_frame,
            text="⚙️ System Settings",
            bg='#F6F8FA',
            fg=LightTheme.TEXT_PRIMARY,
            font=('Segoe UI', 14, 'bold'),
            anchor='w'
        )
        title_label.pack(side=tk.LEFT, fill=tk.X)
        
        subtitle = tk.Label(
            title_frame,
            text="Configure ports, resources, and system preferences",
            bg='#F6F8FA',
            fg=LightTheme.TEXT_SECONDARY,
            font=('Segoe UI', 10),
            anchor='w'
        )
        subtitle.pack(side=tk.LEFT, fill=tk.X, padx=(Spacing.MD, 0))
        
        # Create scrollable content
        canvas = tk.Canvas(main_container, bg='#F6F8FA', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#F6F8FA')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Port Configuration Section
        self.create_port_settings(scrollable_frame)
        
        # Resource Limits Section
        self.create_resource_settings(scrollable_frame)
        
        # Timeout Configuration Section
        self.create_timeout_settings(scrollable_frame)
        
        # Docker Network Section
        self.create_network_settings(scrollable_frame)
        
        # Action buttons
        self.create_action_buttons(scrollable_frame)
        
        # Pack canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_port_settings(self, parent):
        """Create port configuration section with YAML support"""
        port_card = SectionCard(parent, title="Port Configuration")
        port_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        content = port_card.get_content()
        
        # Toolbar for YAML operations
        toolbar = tk.Frame(content, bg='#FFFFFF')
        toolbar.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        CleanButton(
            toolbar,
            "Load from Docker Compose",
            self.load_from_docker_compose,
            'primary'
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        CleanButton(
            toolbar,
            "Load from YAML",
            self.load_ports_from_yaml,
            'secondary'
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        CleanButton(
            toolbar,
            "Save to YAML",
            self.save_ports_to_yaml,
            'secondary'
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        CleanButton(
            toolbar,
            "Add Port",
            self.add_new_port,
            'success'
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        # Container for port entries (scrollable if many ports)
        self.ports_container = tk.Frame(content, bg='#FFFFFF')
        self.ports_container.pack(fill=tk.BOTH, expand=True)
        
        # Get ports from config
        ports = self.config.get('ports', {})
        
        # Default port configurations
        default_port_configs = [
            ("spark_master_ui", "Spark Master UI", "9090"),
            ("spark_worker_ui", "Spark Worker UI", "8081"),
            ("hdfs_namenode_ui", "HDFS NameNode UI", "9870"),
            ("hdfs_datanode_ui", "HDFS DataNode UI", "9864"),
            ("history_server", "Spark History Server", "18080"),
            ("jupyter", "Jupyter Notebook", "8888")
        ]
        
        self.port_entries = {}
        
        # Load existing ports or defaults
        if ports:
            for key, port_value in ports.items():
                # Find label from defaults or use key
                label = key.replace('_', ' ').title()
                for def_key, def_label, _ in default_port_configs:
                    if def_key == key:
                        label = def_label
                        break
                self._create_port_row(key, label, port_value)
        else:
            # Use defaults
            for key, label, default in default_port_configs:
                self._create_port_row(key, label, default)
    
    def _create_port_row(self, key, label, value):
        """Create a single port configuration row"""
        row = tk.Frame(self.ports_container, bg='#FFFFFF')
        row.pack(fill=tk.X, pady=Spacing.SM)
        
        # Label
        lbl = tk.Label(
            row,
            text=label,
            bg='#FFFFFF',
            fg=LightTheme.TEXT_PRIMARY,
            font=('Segoe UI', 10),
            width=25,
            anchor='w'
        )
        lbl.pack(side=tk.LEFT, padx=(0, Spacing.MD))
        
        # Entry
        entry = tk.Entry(
            row,
            font=('Segoe UI', 10),
            bg='#F6F8FA',
            fg=LightTheme.TEXT_PRIMARY,
            relief=tk.FLAT,
            width=10
        )
        entry.insert(0, value)
        entry.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        # Store reference
        self.port_entries[key] = {
            'entry': entry,
            'label': label,
            'row': row
        }
        
        # Open button (no emoji)
        open_btn = CleanButton(
            row,
            "Open",
            lambda k=key: self.open_in_browser(k),
            'secondary'
        )
        open_btn.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        # Delete button (no emoji)
        delete_btn = CleanButton(
            row,
            "Delete",
            lambda k=key: self.delete_port(k),
            'danger'
        )
        delete_btn.pack(side=tk.LEFT)
    
    def load_from_docker_compose(self):
        """Auto-load ports from docker-compose.yml in project root"""
        try:
            # Find docker-compose.yml in project root
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            docker_compose_path = os.path.join(project_root, 'docker-compose.yml')
            
            if not os.path.exists(docker_compose_path):
                messagebox.showwarning(
                    "File Not Found",
                    f"docker-compose.yml not found at:\n{docker_compose_path}\n\n"
                    "Please ensure docker-compose.yml exists in the project root."
                )
                return
            
            with open(docker_compose_path, 'r', encoding='utf-8') as f:
                yaml_config = yaml.safe_load(f)
            
            # Parse Docker Compose services
            ports = {}
            service_mapping = {
                'spark-master': 'spark_master_ui',
                'spark-worker': 'spark_worker_ui',
                'namenode': 'hdfs_namenode_ui',
                'datanode': 'hdfs_datanode_ui',
                'history-server': 'history_server',
                'jupyter': 'jupyter'
            }
            
            if 'services' in yaml_config:
                for service_name, service_config in yaml_config['services'].items():
                    if 'ports' in service_config:
                        port_list = service_config['ports']
                        if port_list and len(port_list) > 0:
                            # Get first port mapping
                            port_mapping = port_list[0]
                            
                            # Parse "host:container" format
                            if isinstance(port_mapping, str):
                                # Remove quotes and split
                                port_mapping = port_mapping.strip('"').strip("'")
                                parts = port_mapping.split(':')
                                if len(parts) >= 2:
                                    # HOST:CONTAINER - we want HOST port
                                    host_port = parts[0].strip()
                                    
                                    # Map to our port names
                                    if service_name in service_mapping:
                                        port_key = service_mapping[service_name]
                                        ports[port_key] = host_port
                                        
                                        # Add additional ports for some services
                                        if len(port_list) > 1:
                                            # Process additional ports
                                            for idx, extra_port in enumerate(port_list[1:], 1):
                                                if isinstance(extra_port, str):
                                                    extra_parts = extra_port.strip('"').strip("'").split(':')
                                                    if len(extra_parts) >= 2:
                                                        extra_host = extra_parts[0].strip()
                                                        # For additional ports, use service_port_{idx}
                                                        ports[f"{service_name}_port_{idx}"] = extra_host
                            elif isinstance(port_mapping, dict):
                                if 'published' in port_mapping:
                                    host_port = str(port_mapping['published'])
                                    if service_name in service_mapping:
                                        port_key = service_mapping[service_name]
                                        ports[port_key] = host_port
            
            if not ports:
                messagebox.showwarning(
                    "No Ports Found",
                    "No port configuration found in docker-compose.yml"
                )
                return
            
            # Update existing port entries or create new ones
            for key, value in ports.items():
                if key in self.port_entries:
                    # Update existing entry
                    entry = self.port_entries[key]['entry']
                    entry.delete(0, tk.END)
                    entry.insert(0, str(value))
                else:
                    # Create new entry
                    label = key.replace('_', ' ').title()
                    self._create_port_row(key, label, str(value))
            
            messagebox.showinfo(
                "Success",
                f"✅ Loaded {len(ports)} ports from docker-compose.yml\n\n"
                f"Services detected:\n" + 
                "\n".join([f"  • {k}: {v}" for k, v in ports.items()])
            )
            
            if self.append_log:
                self.append_log(f"🐳 Loaded {len(ports)} ports from docker-compose.yml")
        
        except yaml.YAMLError as e:
            messagebox.showerror(
                "YAML Error",
                f"Failed to parse docker-compose.yml:\n{e}"
            )
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to load docker-compose.yml:\n{e}"
            )
    
    def load_ports_from_yaml(self):
        """Load port configuration from YAML file"""
        file_path = filedialog.askopenfilename(
            title="Select YAML Configuration File",
            filetypes=[
                ("YAML files", "*.yaml *.yml"),
                ("All files", "*.*")
            ],
            initialdir=os.path.dirname(self.config_file)
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml_config = yaml.safe_load(f)
            
            # Extract ports from YAML
            ports = {}
            
            # Try different YAML structures
            if 'ports' in yaml_config:
                ports = yaml_config['ports']
            elif 'services' in yaml_config:
                # Docker Compose format
                for service_name, service_config in yaml_config['services'].items():
                    if 'ports' in service_config:
                        for port_mapping in service_config['ports']:
                            # Parse "host:container" format
                            if isinstance(port_mapping, str):
                                parts = port_mapping.split(':')
                                if len(parts) >= 2:
                                    host_port = parts[0]
                                    ports[f"{service_name}_port"] = host_port
                            elif isinstance(port_mapping, dict):
                                if 'published' in port_mapping:
                                    ports[f"{service_name}_port"] = str(port_mapping['published'])
            
            if not ports:
                messagebox.showwarning(
                    "No Ports Found",
                    "No port configuration found in YAML file.\n\n"
                    "Expected format:\n"
                    "ports:\n"
                    "  spark_master_ui: 9090\n"
                    "  hdfs_namenode_ui: 9870"
                )
                return
            
            # Clear existing ports
            for port_data in list(self.port_entries.values()):
                port_data['row'].destroy()
            self.port_entries.clear()
            
            # Create rows for loaded ports
            for key, value in ports.items():
                label = key.replace('_', ' ').title()
                self._create_port_row(key, label, str(value))
            
            messagebox.showinfo(
                "Success",
                f"✅ Loaded {len(ports)} ports from YAML file:\n{os.path.basename(file_path)}"
            )
            
            if self.append_log:
                self.append_log(f"📁 Loaded {len(ports)} ports from {file_path}")
        
        except yaml.YAMLError as e:
            messagebox.showerror(
                "YAML Error",
                f"Failed to parse YAML file:\n{e}"
            )
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to load YAML file:\n{e}"
            )
    
    def save_ports_to_yaml(self):
        """Save current port configuration to YAML file"""
        file_path = filedialog.asksaveasfilename(
            title="Save Port Configuration",
            defaultextension=".yaml",
            filetypes=[
                ("YAML files", "*.yaml"),
                ("YML files", "*.yml"),
                ("All files", "*.*")
            ],
            initialdir=os.path.dirname(self.config_file),
            initialfile="ports_config.yaml"
        )
        
        if not file_path:
            return
        
        try:
            # Gather current ports
            ports = {}
            for key, port_data in self.port_entries.items():
                ports[key] = port_data['entry'].get()
            
            # Create YAML structure
            yaml_config = {
                'ports': ports,
                'metadata': {
                    'created_by': 'Spark Runner GUI',
                    'version': '4.0',
                    'description': 'Port configuration for Spark and HDFS services'
                }
            }
            
            # Save to YAML
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(yaml_config, f, default_flow_style=False, allow_unicode=True)
            
            messagebox.showinfo(
                "Success",
                f"✅ Saved {len(ports)} ports to:\n{os.path.basename(file_path)}"
            )
            
            if self.append_log:
                self.append_log(f"💾 Saved {len(ports)} ports to {file_path}")
        
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to save YAML file:\n{e}"
            )
    
    def add_new_port(self):
        """Add a new custom port configuration"""
        # Create dialog
        dialog = tk.Toplevel(self.master)
        dialog.title("Add New Port")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.transient(self.master)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = tk.Frame(dialog, bg='#FFFFFF', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(
            main_frame,
            text="➕ Add New Port Configuration",
            font=('Segoe UI', 12, 'bold'),
            bg='#FFFFFF',
            fg='#24292F'
        ).pack(pady=(0, 20))
        
        # Port Key
        key_frame = tk.Frame(main_frame, bg='#FFFFFF')
        key_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            key_frame,
            text="Port Key (ID):",
            font=('Segoe UI', 10),
            bg='#FFFFFF',
            fg='#24292F',
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        key_entry = tk.Entry(
            key_frame,
            font=('Segoe UI', 10),
            bg='#F6F8FA',
            relief=tk.FLAT
        )
        key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Port Label
        label_frame = tk.Frame(main_frame, bg='#FFFFFF')
        label_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            label_frame,
            text="Display Label:",
            font=('Segoe UI', 10),
            bg='#FFFFFF',
            fg='#24292F',
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        label_entry = tk.Entry(
            label_frame,
            font=('Segoe UI', 10),
            bg='#F6F8FA',
            relief=tk.FLAT
        )
        label_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Port Number
        port_frame = tk.Frame(main_frame, bg='#FFFFFF')
        port_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            port_frame,
            text="Port Number:",
            font=('Segoe UI', 10),
            bg='#FFFFFF',
            fg='#24292F',
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        port_entry = tk.Entry(
            port_frame,
            font=('Segoe UI', 10),
            bg='#F6F8FA',
            relief=tk.FLAT
        )
        port_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Buttons
        btn_frame = tk.Frame(main_frame, bg='#FFFFFF')
        btn_frame.pack(fill=tk.X)
        
        def on_add():
            key = key_entry.get().strip()
            label = label_entry.get().strip()
            port = port_entry.get().strip()
            
            # Validation
            if not key:
                messagebox.showwarning("Validation Error", "Port Key is required!", parent=dialog)
                return
            
            if not label:
                messagebox.showwarning("Validation Error", "Display Label is required!", parent=dialog)
                return
            
            if not port:
                messagebox.showwarning("Validation Error", "Port Number is required!", parent=dialog)
                return
            
            # Check if key already exists
            if key in self.port_entries:
                messagebox.showwarning("Duplicate Key", f"Port key '{key}' already exists!", parent=dialog)
                return
            
            # Validate port number
            try:
                port_num = int(port)
                if port_num < 1 or port_num > 65535:
                    raise ValueError()
            except ValueError:
                messagebox.showwarning("Invalid Port", "Port must be a number between 1 and 65535!", parent=dialog)
                return
            
            # Add the new port
            self._create_port_row(key, label, port)
            
            if self.append_log:
                self.append_log(f"➕ Added new port: {label} ({key}) = {port}")
            
            dialog.destroy()
        
        CleanButton(
            btn_frame,
            "✅ Add Port",
            on_add,
            'success'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        CleanButton(
            btn_frame,
            "❌ Cancel",
            dialog.destroy,
            'secondary'
        ).pack(side=tk.LEFT)
    
    def delete_port(self, key):
        """Delete a port configuration"""
        if key not in self.port_entries:
            return
        
        port_data = self.port_entries[key]
        label = port_data['label']
        
        if messagebox.askyesno(
            "Confirm Delete",
            f"Delete port configuration:\n\n{label} ({key})?",
            icon='warning'
        ):
            port_data['row'].destroy()
            del self.port_entries[key]
            
            if self.append_log:
                self.append_log(f"🗑️ Deleted port: {label} ({key})")
    
    def create_resource_settings(self, parent):
        """Create resource limits section"""
        resource_card = SectionCard(parent, title="💾 Resource Limits")
        resource_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        content = resource_card.get_content()
        
        # Get resource limits from config
        resources = self.config.get('resource_limits', {})
        
        resource_configs = [
            ("spark_worker_memory", "Spark Worker Memory", "4g"),
            ("spark_worker_cores", "Spark Worker Cores", "2"),
            ("hdfs_namenode_memory", "HDFS NameNode Memory", "2g"),
            ("hdfs_datanode_memory", "HDFS DataNode Memory", "2g")
        ]
        
        self.resource_entries = {}
        
        for key, label, default in resource_configs:
            row = tk.Frame(content, bg='#FFFFFF')
            row.pack(fill=tk.X, pady=Spacing.SM)
            
            # Label
            lbl = tk.Label(
                row,
                text=label,
                bg='#FFFFFF',
                fg=LightTheme.TEXT_PRIMARY,
                font=('Segoe UI', 10),
                width=25,
                anchor='w'
            )
            lbl.pack(side=tk.LEFT, padx=(0, Spacing.MD))
            
            # Entry
            entry = tk.Entry(
                row,
                font=('Segoe UI', 10),
                bg='#F6F8FA',
                fg=LightTheme.TEXT_PRIMARY,
                relief=tk.FLAT,
                width=15
            )
            entry.insert(0, resources.get(key, default))
            entry.pack(side=tk.LEFT)
            
            self.resource_entries[key] = entry
    
    def create_timeout_settings(self, parent):
        """Create timeout configuration section"""
        timeout_card = SectionCard(parent, title="⏱️ Timeout Settings")
        timeout_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        content = timeout_card.get_content()
        
        # Get timeout values from config
        spark_timeout = self.config.get('spark_job_timeout', 300)
        hdfs_timeout = self.config.get('hdfs_upload_timeout', 300)
        docker_timeout = self.config.get('docker_command_timeout', 60)
        
        timeout_configs = [
            ("spark_job_timeout", "Spark Job Timeout (seconds)", spark_timeout),
            ("hdfs_upload_timeout", "HDFS Upload Timeout (seconds)", hdfs_timeout),
            ("docker_command_timeout", "Docker Command Timeout (seconds)", docker_timeout)
        ]
        
        self.timeout_entries = {}
        
        for key, label, default in timeout_configs:
            row = tk.Frame(content, bg='#FFFFFF')
            row.pack(fill=tk.X, pady=Spacing.SM)
            
            # Label
            lbl = tk.Label(
                row,
                text=label,
                bg='#FFFFFF',
                fg=LightTheme.TEXT_PRIMARY,
                font=('Segoe UI', 10),
                width=30,
                anchor='w'
            )
            lbl.pack(side=tk.LEFT, padx=(0, Spacing.MD))
            
            # Entry with spinbox for easier adjustment
            entry = tk.Spinbox(
                row,
                from_=30,
                to=1800,
                font=('Segoe UI', 10),
                bg='#F6F8FA',
                fg=LightTheme.TEXT_PRIMARY,
                relief=tk.FLAT,
                width=10
            )
            entry.delete(0, tk.END)
            entry.insert(0, str(default))
            entry.pack(side=tk.LEFT, padx=(0, Spacing.SM))
            
            # Hint label
            hint = tk.Label(
                row,
                text="(30-1800s)",
                bg='#FFFFFF',
                fg='#6E7781',
                font=('Segoe UI', 9)
            )
            hint.pack(side=tk.LEFT)
            
            self.timeout_entries[key] = entry
        
        # Info label
        info_frame = tk.Frame(content, bg='#FFFFFF')
        info_frame.pack(fill=tk.X, pady=(Spacing.MD, 0))
        
        info_text = tk.Label(
            info_frame,
            text="💡 Tip: Increase timeout for slow networks or large operations",
            bg='#FFFFFF',
            fg='#57606A',
            font=('Segoe UI', 9),
            wraplength=400,
            justify=tk.LEFT
        )
        info_text.pack(fill=tk.X)
    
    def create_network_settings(self, parent):
        """Create network settings section"""
        network_card = SectionCard(parent, title="🌐 Docker Network")
        network_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        content = network_card.get_content()
        
        row = tk.Frame(content, bg='#FFFFFF')
        row.pack(fill=tk.X, pady=Spacing.SM)
        
        # Label
        lbl = tk.Label(
            row,
            text="Docker Network Name",
            bg='#FFFFFF',
            fg=LightTheme.TEXT_PRIMARY,
            font=('Segoe UI', 10),
            width=25,
            anchor='w'
        )
        lbl.pack(side=tk.LEFT, padx=(0, Spacing.MD))
        
        # Entry
        self.network_entry = tk.Entry(
            row,
            font=('Segoe UI', 10),
            bg='#F6F8FA',
            fg=LightTheme.TEXT_PRIMARY,
            relief=tk.FLAT,
            width=20
        )
        self.network_entry.insert(0, self.config.get('docker_network', 'hadoop'))
        self.network_entry.pack(side=tk.LEFT)
    
    def create_action_buttons(self, parent):
        """Create action buttons"""
        button_frame = tk.Frame(parent, bg='#F6F8FA')
        button_frame.pack(fill=tk.X, pady=(Spacing.LG, 0))
        
        # Save button
        save_btn = CleanButton(
            button_frame,
            "💾 Save Configuration",
            self.save_settings,
            'primary'
        )
        save_btn.pack(side=tk.LEFT, padx=(0, Spacing.MD))
        
        # Reset button
        reset_btn = CleanButton(
            button_frame,
            "🔄 Reset to Default",
            self.reset_to_default,
            'secondary'
        )
        reset_btn.pack(side=tk.LEFT, padx=(0, Spacing.MD))
        
        # Test connections button
        test_btn = CleanButton(
            button_frame,
            "🔍 Test Connections",
            self.test_connections,
            'secondary'
        )
        test_btn.pack(side=tk.LEFT)
    
    def save_settings(self):
        """Save all settings to config file"""
        try:
            # Update ports
            if 'ports' not in self.config:
                self.config['ports'] = {}
            
            for key, port_data in self.port_entries.items():
                self.config['ports'][key] = port_data['entry'].get()
            
            # Update resource limits
            if 'resource_limits' not in self.config:
                self.config['resource_limits'] = {}
            
            for key, entry in self.resource_entries.items():
                self.config['resource_limits'][key] = entry.get()
            
            # Update timeout settings
            try:
                for key, entry in self.timeout_entries.items():
                    value = int(entry.get())
                    # Validate timeout range
                    if value < 30:
                        value = 30
                    elif value > 1800:
                        value = 1800
                    self.config[key] = value
            except ValueError:
                messagebox.showwarning("Invalid Input", "⏱️ Timeout values must be numbers!\n\nUsing default values...")
                # Use defaults
                self.config['spark_job_timeout'] = 300
                self.config['hdfs_upload_timeout'] = 300
                self.config['docker_command_timeout'] = 60
            
            # Update network
            self.config['docker_network'] = self.network_entry.get()
            
            # Save to file
            if self.save_config():
                messagebox.showinfo("Success", "✅ Configuration saved successfully!\n\n⚠️ Please restart Docker containers for changes to take effect.")
                if self.append_log:
                    self.append_log("✅ Settings saved successfully (timeouts updated)")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def reset_to_default(self):
        """Reset all settings to default values"""
        if messagebox.askyesno("Confirm Reset", "Reset all settings to default values?"):
            # Reset port entries
            defaults = {
                "spark_master_ui": "9090",
                "spark_worker_ui": "8081",
                "hdfs_namenode_ui": "9870",
                "hdfs_datanode_ui": "9864",
                "history_server": "18080",
                "jupyter": "8888"
            }
            
            for key, port_data in self.port_entries.items():
                entry = port_data['entry']
                entry.delete(0, tk.END)
                entry.insert(0, defaults.get(key, ""))
            
            # Reset resource entries
            resource_defaults = {
                "spark_worker_memory": "4g",
                "spark_worker_cores": "2",
                "hdfs_namenode_memory": "2g",
                "hdfs_datanode_memory": "2g"
            }
            
            for key, entry in self.resource_entries.items():
                entry.delete(0, tk.END)
                entry.insert(0, resource_defaults.get(key, ""))
            
            # Reset timeout entries
            timeout_defaults = {
                "spark_job_timeout": "300",
                "hdfs_upload_timeout": "300",
                "docker_command_timeout": "60"
            }
            
            for key, entry in self.timeout_entries.items():
                entry.delete(0, tk.END)
                entry.insert(0, timeout_defaults.get(key, ""))
            
            # Reset network
            self.network_entry.delete(0, tk.END)
            self.network_entry.insert(0, "hadoop")
            
            if self.append_log:
                self.append_log("🔄 Settings reset to default")
    
    def test_connections(self):
        """Test all configured port connections"""
        import webbrowser
        from urllib.request import urlopen
        from urllib.error import URLError
        
        results = []
        
        for key, port_data in self.port_entries.items():
            port = port_data['entry'].get()
            url = f"http://localhost:{port}"
            
            try:
                urlopen(url, timeout=2)
                results.append(f"✅ {key}: {port} - OK")
            except URLError:
                results.append(f"❌ {key}: {port} - Not accessible")
            except Exception as e:
                results.append(f"⚠️ {key}: {port} - Error: {e}")
        
        messagebox.showinfo("Connection Test Results", "\n".join(results))
        
        if self.append_log:
            for result in results:
                self.append_log(result)
    
    def open_in_browser(self, port_key):
        """Open service in web browser"""
        import webbrowser
        
        port = self.port_entries[port_key]['entry'].get()
        url = f"http://localhost:{port}"
        
        try:
            webbrowser.open(url)
            if self.append_log:
                self.append_log(f"🌐 Opened {port_key} at {url}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open browser: {e}")
