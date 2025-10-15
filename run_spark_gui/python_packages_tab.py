"""
Python Packages Management Tab
Hỗ trợ cài đặt thư viện Python vào Spark Docker containers
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import json
import os
from datetime import datetime

class PythonPackagesTab:
    """Tab quản lý cài đặt thư viện Python cho Spark containers"""
    
    # Popular packages for Spark/Data Science
    POPULAR_PACKAGES = [
        "matplotlib",
        "pandas",
        "numpy",
        "scipy",
        "seaborn",
        "plotly",
        "scikit-learn",
        "xgboost",
        "lightgbm",
        "transformers",
        "torch",
        "tensorflow",
        "keras",
        "opencv-python",
        "pillow",
        "beautifulsoup4",
        "requests",
        "sqlalchemy",
        "psycopg2-binary",
        "pymongo",
        "redis",
        "celery",
        "fastapi",
        "uvicorn"
    ]
    
    def __init__(self, parent_frame, status_callback=None):
        self.parent = parent_frame
        self.status_callback = status_callback
        self.installed_packages = {}
        self.is_installing = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Tạo giao diện tab"""
        
        # Main container
        main_container = ttk.Frame(self.parent)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ========== TOP SECTION: Installation Form ==========
        form_frame = ttk.LabelFrame(main_container, text="📦 Cài đặt thư viện Python", padding=15)
        form_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Row 1: Container selection
        container_frame = ttk.Frame(form_frame)
        container_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(container_frame, text="Container:", width=15).pack(side=tk.LEFT)
        self.container_var = tk.StringVar(value="spark-worker")
        container_combo = ttk.Combobox(
            container_frame,
            textvariable=self.container_var,
            values=["spark-worker", "spark-master", "jupyter-notebook"],
            state="readonly",
            width=25
        )
        container_combo.pack(side=tk.LEFT, padx=(5, 10))
        
        # Refresh button
        refresh_btn = ttk.Button(
            container_frame,
            text="🔄 Làm mới",
            command=self.refresh_containers,
            width=15
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Row 2: Package name
        package_frame = ttk.Frame(form_frame)
        package_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(package_frame, text="Tên thư viện:", width=15).pack(side=tk.LEFT)
        self.package_var = tk.StringVar()
        package_entry = ttk.Entry(package_frame, textvariable=self.package_var, width=30)
        package_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(package_frame, text="VD: matplotlib, pandas==1.5.0").pack(side=tk.LEFT, padx=10)
        
        # Row 3: Popular packages dropdown
        popular_frame = ttk.Frame(form_frame)
        popular_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(popular_frame, text="Hoặc chọn:", width=15).pack(side=tk.LEFT)
        self.popular_var = tk.StringVar()
        popular_combo = ttk.Combobox(
            popular_frame,
            textvariable=self.popular_var,
            values=self.POPULAR_PACKAGES,
            width=30
        )
        popular_combo.pack(side=tk.LEFT, padx=5)
        popular_combo.bind('<<ComboboxSelected>>', self.on_popular_selected)
        
        # Row 4: Options
        options_frame = ttk.Frame(form_frame)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.no_cache_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Không dùng cache (--no-cache-dir)",
            variable=self.no_cache_var
        ).pack(side=tk.LEFT, padx=(15, 20))
        
        self.upgrade_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Nâng cấp nếu đã cài (--upgrade)",
            variable=self.upgrade_var
        ).pack(side=tk.LEFT, padx=20)
        
        # Row 5: Action buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.install_btn = ttk.Button(
            btn_frame,
            text="✅ Cài đặt",
            command=self.install_package,
            style='Accent.TButton',
            width=20
        )
        self.install_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="📋 Xem đã cài",
            command=self.list_installed,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="🗑️ Gỡ thư viện",
            command=self.uninstall_package,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        # ========== MIDDLE SECTION: Output Console ==========
        output_frame = ttk.LabelFrame(main_container, text="📝 Kết quả cài đặt", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Output text with scrollbar
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            height=15,
            font=('Consolas', 9),
            bg='#1E1E1E',
            fg='#D4D4D4',
            insertbackground='white',
            wrap=tk.WORD
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # ========== BOTTOM SECTION: Installed Packages List ==========
        packages_frame = ttk.LabelFrame(main_container, text="📚 Thư viện đã cài trong container", padding=10)
        packages_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for packages
        tree_frame = ttk.Frame(packages_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.packages_tree = ttk.Treeview(
            tree_frame,
            columns=('package', 'version', 'location'),
            show='headings',
            yscrollcommand=tree_scroll.set,
            height=8
        )
        tree_scroll.config(command=self.packages_tree.yview)
        
        # Configure columns
        self.packages_tree.heading('package', text='Tên thư viện')
        self.packages_tree.heading('version', text='Phiên bản')
        self.packages_tree.heading('location', text='Đường dẫn')
        
        self.packages_tree.column('package', width=200)
        self.packages_tree.column('version', width=100)
        self.packages_tree.column('location', width=400)
        
        self.packages_tree.pack(fill=tk.BOTH, expand=True)
        
        # Log initial message
        self.log_output("✅ Tab quản lý thư viện Python đã sẵn sàng\n")
        self.log_output("💡 Tip: Chọn container, nhập tên thư viện và nhấn 'Cài đặt'\n")
        self.log_output(f"📝 Lệnh mẫu: docker exec spark-worker python3 -m pip install --no-cache-dir matplotlib\n\n")
    
    def on_popular_selected(self, event=None):
        """Khi chọn thư viện phổ biến"""
        selected = self.popular_var.get()
        if selected:
            self.package_var.set(selected)
    
    def log_output(self, message, tag=None):
        """Ghi log ra console"""
        self.output_text.insert(tk.END, message)
        if tag:
            # Apply color tags if needed
            pass
        self.output_text.see(tk.END)
        self.output_text.update_idletasks()
    
    def update_status(self, message):
        """Cập nhật status bar"""
        if self.status_callback:
            self.status_callback(message)
    
    def refresh_containers(self):
        """Làm mới danh sách containers"""
        self.log_output("🔄 Đang kiểm tra Docker containers...\n")
        
        def check_containers():
            try:
                result = subprocess.run(
                    ['docker', 'ps', '--format', '{{.Names}}'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    containers = result.stdout.strip().split('\n')
                    containers = [c for c in containers if c]
                    
                    self.log_output(f"✅ Tìm thấy {len(containers)} container(s) đang chạy:\n")
                    for container in containers:
                        self.log_output(f"   • {container}\n")
                    
                    # Update combobox
                    self.parent.after(0, lambda: self.update_container_list(containers))
                else:
                    self.log_output(f"❌ Lỗi: {result.stderr}\n")
            except Exception as e:
                self.log_output(f"❌ Lỗi khi kiểm tra containers: {str(e)}\n")
        
        threading.Thread(target=check_containers, daemon=True).start()
    
    def update_container_list(self, containers):
        """Cập nhật danh sách containers trong combobox"""
        current = self.container_var.get()
        
        # Find combobox widget
        for widget in self.parent.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.LabelFrame):
                        for subchild in child.winfo_children():
                            if isinstance(subchild, ttk.Frame):
                                for item in subchild.winfo_children():
                                    if isinstance(item, ttk.Combobox):
                                        item['values'] = containers
                                        if current not in containers and containers:
                                            self.container_var.set(containers[0])
                                        return
    
    def install_package(self):
        """Cài đặt thư viện"""
        container = self.container_var.get()
        package = self.package_var.get().strip()
        
        if not container:
            messagebox.showerror("Lỗi", "Vui lòng chọn container!")
            return
        
        if not package:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên thư viện!")
            return
        
        if self.is_installing:
            messagebox.showwarning("Cảnh báo", "Đang cài đặt thư viện khác, vui lòng đợi!")
            return
        
        # Build command
        cmd = ['docker', 'exec', container, 'python3', '-m', 'pip', 'install']
        
        if self.no_cache_var.get():
            cmd.append('--no-cache-dir')
        
        if self.upgrade_var.get():
            cmd.append('--upgrade')
        
        cmd.append(package)
        
        # Log command
        self.log_output(f"\n{'='*80}\n")
        self.log_output(f"🚀 Đang cài đặt: {package}\n")
        self.log_output(f"📦 Container: {container}\n")
        self.log_output(f"💻 Lệnh: {' '.join(cmd)}\n")
        self.log_output(f"{'='*80}\n\n")
        
        self.update_status(f"⏳ Đang cài đặt {package}...")
        self.is_installing = True
        self.install_btn.config(state='disabled', text='⏳ Đang cài...')
        
        # Run in thread
        def run_install():
            try:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                # Read output line by line
                for line in iter(process.stdout.readline, ''):
                    if line:
                        self.parent.after(0, lambda l=line: self.log_output(l))
                
                process.wait()
                
                if process.returncode == 0:
                    self.parent.after(0, lambda: self.log_output(f"\n✅ Cài đặt thành công: {package}\n"))
                    self.parent.after(0, lambda: self.update_status(f"✅ Đã cài {package}"))
                    self.parent.after(0, lambda: messagebox.showinfo("Thành công", f"Đã cài đặt {package} thành công!"))
                else:
                    self.parent.after(0, lambda: self.log_output(f"\n❌ Cài đặt thất bại với mã lỗi: {process.returncode}\n"))
                    self.parent.after(0, lambda: self.update_status("❌ Cài đặt thất bại"))
                    self.parent.after(0, lambda: messagebox.showerror("Lỗi", f"Cài đặt {package} thất bại!"))
                
            except Exception as e:
                error_msg = str(e)
                self.parent.after(0, lambda: self.log_output(f"\n❌ Lỗi: {error_msg}\n"))
                self.parent.after(0, lambda: self.update_status("❌ Lỗi cài đặt"))
                self.parent.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi: {error_msg}"))
            
            finally:
                self.is_installing = False
                self.parent.after(0, lambda: self.install_btn.config(state='normal', text='✅ Cài đặt'))
        
        threading.Thread(target=run_install, daemon=True).start()
    
    def list_installed(self):
        """Liệt kê thư viện đã cài"""
        container = self.container_var.get()
        
        if not container:
            messagebox.showerror("Lỗi", "Vui lòng chọn container!")
            return
        
        self.log_output(f"\n🔍 Đang kiểm tra thư viện trong {container}...\n")
        self.update_status(f"⏳ Đang tải danh sách thư viện...")
        
        # Clear tree
        for item in self.packages_tree.get_children():
            self.packages_tree.delete(item)
        
        def get_packages():
            try:
                # Get pip list in JSON format
                result = subprocess.run(
                    ['docker', 'exec', container, 'python3', '-m', 'pip', 'list', '--format=json'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    packages = json.loads(result.stdout)
                    
                    self.parent.after(0, lambda: self.log_output(f"✅ Tìm thấy {len(packages)} thư viện\n\n"))
                    
                    # Populate tree
                    for pkg in packages:
                        name = pkg.get('name', '')
                        version = pkg.get('version', '')
                        location = pkg.get('location', 'N/A')
                        
                        self.parent.after(0, lambda n=name, v=version, l=location: 
                                        self.packages_tree.insert('', 'end', values=(n, v, l)))
                    
                    self.parent.after(0, lambda: self.update_status(f"✅ Đã tải {len(packages)} thư viện"))
                else:
                    self.parent.after(0, lambda: self.log_output(f"❌ Lỗi: {result.stderr}\n"))
                    self.parent.after(0, lambda: self.update_status("❌ Không thể tải danh sách"))
                    
            except Exception as e:
                self.parent.after(0, lambda: self.log_output(f"❌ Lỗi: {str(e)}\n"))
                self.parent.after(0, lambda: self.update_status("❌ Lỗi"))
        
        threading.Thread(target=get_packages, daemon=True).start()
    
    def uninstall_package(self):
        """Gỡ cài đặt thư viện"""
        # Get selected package from tree
        selected = self.packages_tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn thư viện cần gỡ từ danh sách bên dưới!")
            return
        
        item = self.packages_tree.item(selected[0])
        package_name = item['values'][0]
        
        # Confirm
        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn gỡ thư viện '{package_name}'?"):
            return
        
        container = self.container_var.get()
        
        self.log_output(f"\n🗑️ Đang gỡ thư viện: {package_name}\n")
        self.update_status(f"⏳ Đang gỡ {package_name}...")
        
        def run_uninstall():
            try:
                result = subprocess.run(
                    ['docker', 'exec', container, 'python3', '-m', 'pip', 'uninstall', '-y', package_name],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    self.parent.after(0, lambda: self.log_output(f"✅ Đã gỡ thành công: {package_name}\n"))
                    self.parent.after(0, lambda: self.update_status(f"✅ Đã gỡ {package_name}"))
                    self.parent.after(0, lambda: messagebox.showinfo("Thành công", f"Đã gỡ {package_name}!"))
                    # Refresh list
                    self.parent.after(0, self.list_installed)
                else:
                    self.parent.after(0, lambda: self.log_output(f"❌ Lỗi: {result.stderr}\n"))
                    self.parent.after(0, lambda: messagebox.showerror("Lỗi", "Gỡ thư viện thất bại!"))
                    
            except Exception as e:
                self.parent.after(0, lambda: self.log_output(f"❌ Lỗi: {str(e)}\n"))
                self.parent.after(0, lambda: messagebox.showerror("Lỗi", str(e)))
        
        threading.Thread(target=run_uninstall, daemon=True).start()


def create_packages_tab(parent_frame, status_callback=None):
    """Factory function để tạo tab"""
    return PythonPackagesTab(parent_frame, status_callback)
