"""
Settings Tab V4 - Port Configuration & System Settings
Professional Material Design 3 UI
"""
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
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
    
    def __init__(self, parent, config_file="spark_runner_config.json", append_log=None):
        self.frame = parent
        self.config_file = config_file
        self.append_log = append_log
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
        """Save configuration to JSON file"""
        try:
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
        
        # Docker Network Section
        self.create_network_settings(scrollable_frame)
        
        # Action buttons
        self.create_action_buttons(scrollable_frame)
        
        # Pack canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_port_settings(self, parent):
        """Create port configuration section"""
        port_card = SectionCard(parent, title="🔌 Port Configuration")
        port_card.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        content = port_card.get_content()
        
        # Get ports from config
        ports = self.config.get('ports', {})
        
        port_configs = [
            ("spark_master_ui", "Spark Master UI", "9090"),
            ("spark_worker_ui", "Spark Worker UI", "8081"),
            ("hdfs_namenode_ui", "HDFS NameNode UI", "9870"),
            ("hdfs_datanode_ui", "HDFS DataNode UI", "9864"),
            ("history_server", "Spark History Server", "18080"),
            ("jupyter", "Jupyter Notebook", "8888")
        ]
        
        self.port_entries = {}
        
        for i, (key, label, default) in enumerate(port_configs):
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
                width=10
            )
            entry.insert(0, ports.get(key, default))
            entry.pack(side=tk.LEFT, padx=(0, Spacing.SM))
            
            self.port_entries[key] = entry
            
            # Open button
            open_btn = CleanButton(
                row,
                f"🌐 Open",
                lambda k=key: self.open_in_browser(k),
                'secondary'
            )
            open_btn.pack(side=tk.LEFT)
    
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
            
            for key, entry in self.port_entries.items():
                self.config['ports'][key] = entry.get()
            
            # Update resource limits
            if 'resource_limits' not in self.config:
                self.config['resource_limits'] = {}
            
            for key, entry in self.resource_entries.items():
                self.config['resource_limits'][key] = entry.get()
            
            # Update network
            self.config['docker_network'] = self.network_entry.get()
            
            # Save to file
            if self.save_config():
                messagebox.showinfo("Success", "✅ Configuration saved successfully!\n\n⚠️ Please restart Docker containers for changes to take effect.")
                if self.append_log:
                    self.append_log("✅ Settings saved successfully")
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
            
            for key, entry in self.port_entries.items():
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
        
        for key, entry in self.port_entries.items():
            port = entry.get()
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
        
        port = self.port_entries[port_key].get()
        url = f"http://localhost:{port}"
        
        try:
            webbrowser.open(url)
            if self.append_log:
                self.append_log(f"🌐 Opened {port_key} at {url}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open browser: {e}")
