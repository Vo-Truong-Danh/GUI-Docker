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
import time
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
        """Tạo giao diện tab - Layout 2 cột"""
        
        # Main container with horizontal split
        main_container = ttk.Frame(self.parent)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure grid weights for responsive layout
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=0, minsize=550)  # Left: fixed width
        main_container.grid_columnconfigure(1, weight=1)  # Right: expandable
        
        # ========== LEFT COLUMN: Installation Form + Package List ==========
        left_column = ttk.Frame(main_container)
        left_column.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
        
        # ========== TOP LEFT: Installation Form ==========
        form_frame = ttk.LabelFrame(left_column, text="📦 Cài đặt thư viện Python", padding=15)
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
        
        self.list_btn = ttk.Button(
            btn_frame,
            text="📋 Xem đã cài",
            command=self.list_installed,
            width=20
        )
        self.list_btn.pack(side=tk.LEFT, padx=5)
        
        self.uninstall_btn = ttk.Button(
            btn_frame,
            text="🗑️ Gỡ thư viện",
            command=self.uninstall_package,
            width=20
        )
        self.uninstall_btn.pack(side=tk.LEFT, padx=5)
        
        # Row 6: Progress bar (NEW)
        progress_frame = ttk.Frame(form_frame)
        progress_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(progress_frame, text="Tiến trình:", width=15).pack(side=tk.LEFT)
        
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.progress_label = ttk.Label(progress_frame, text="0%", width=8)
        self.progress_label.pack(side=tk.LEFT, padx=5)
        
        # ========== BOTTOM LEFT: Installed Packages List ==========
        packages_frame = ttk.LabelFrame(left_column, text="📚 Thư viện đã cài", padding=10)
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
            height=12
        )
        tree_scroll.config(command=self.packages_tree.yview)
        
        # Configure columns
        self.packages_tree.heading('package', text='Tên thư viện')
        self.packages_tree.heading('version', text='Phiên bản')
        self.packages_tree.heading('location', text='Đường dẫn')
        
        self.packages_tree.column('package', width=150)
        self.packages_tree.column('version', width=80)
        self.packages_tree.column('location', width=250)
        
        self.packages_tree.pack(fill=tk.BOTH, expand=True)
        
        # ========== RIGHT COLUMN: Output Console ==========
        right_column = ttk.Frame(main_container)
        right_column.grid(row=0, column=1, sticky='nsew', padx=(5, 0))
        
        output_frame = ttk.LabelFrame(right_column, text="📝 Kết quả cài đặt", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        # Output text with scrollbar - Full height cho right column
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            font=('Consolas', 9),
            bg='#1E1E1E',
            fg='#D4D4D4',
            insertbackground='white',
            wrap=tk.WORD
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
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
    
    def update_progress(self, percent, status_text=""):
        """Cập nhật progress bar"""
        self.progress_var.set(percent)
        self.progress_label.config(text=f"{int(percent)}%")
        if status_text:
            self.update_status(status_text)
    
    def reset_progress(self):
        """Reset progress bar về 0"""
        self.progress_var.set(0)
        self.progress_label.config(text="0%")
    
    def parse_progress(self, line):
        """Parse progress từ pip output"""
        import re
        
        # Pattern 1: "━━━━ 10.3/10.3 MB 1.2 MB/s"
        match = re.search(r'(\d+\.?\d*)/(\d+\.?\d*)\s*MB', line)
        if match:
            current = float(match.group(1))
            total = float(match.group(2))
            if total > 0:
                percent = (current / total) * 100
                return min(percent, 100)
        
        # Pattern 2: "100%" explicit
        match = re.search(r'(\d+)%', line)
        if match:
            return float(match.group(1))
        
        return None
    
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
                    encoding='utf-8',
                    errors='replace',
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
    
    def detect_os_type(self, container):
        """Phát hiện loại OS trong container"""
        try:
            result = subprocess.run(
                ['docker', 'exec', container, 'cat', '/etc/os-release'],
                capture_output=True,
                encoding='utf-8',
                errors='replace',
                timeout=10
            )
            
            os_info = result.stdout.lower()
            if 'alpine' in os_info:
                return 'alpine'
            elif 'debian' in os_info or 'ubuntu' in os_info:
                return 'debian'
            elif 'centos' in os_info or 'rhel' in os_info or 'fedora' in os_info:
                return 'redhat'
            else:
                return 'unknown'
                
        except Exception:
            return 'unknown'
    
    def install_dependencies_sync(self, container, os_type):
        """Cài đặt ĐỒNG BỘ build tools + dependencies (chạy trong thread)"""
        try:
            self.log_output("\n" + "="*80 + "\n")
            self.log_output("🔧 Đang cài đặt build tools + dependencies...\n")
            self.log_output("⏰ Quá trình này mất 1-3 phút, vui lòng đợi...\n")
            self.log_output("="*80 + "\n")
            
            if os_type == 'alpine':
                # Alpine Linux - sử dụng apk
                install_cmd = [
                    'docker', 'exec', container, 'apk', 'add', '--no-cache',
                    'build-base',           # gcc, g++, make
                    'python3-dev',          # Python.h headers
                    'freetype-dev',         # FreeType for matplotlib
                    'libpng-dev',           # PNG support
                    'libjpeg-turbo-dev',    # JPEG support for pillow ⭐
                    'zlib-dev',             # Zlib compression
                    'openblas-dev',         # BLAS for numpy
                    'gfortran',             # Fortran for scipy
                    'libffi-dev',           # FFI for cryptography
                    'openssl-dev',          # OpenSSL for cryptography
                    'libxml2-dev',          # XML for lxml
                    'libxslt-dev',          # XSLT for lxml
                    'postgresql-dev',       # PostgreSQL for psycopg2
                    'tiff-dev',             # TIFF for pillow
                    'lcms2-dev',            # Color management for pillow
                    'libwebp-dev',          # WebP for pillow
                    'tcl-dev',              # Tcl for pillow
                    'tk-dev'                # Tk for pillow
                ]
            elif os_type == 'debian':
                # Debian/Ubuntu - sử dụng apt-get
                install_cmd = [
                    'docker', 'exec', container, 'sh', '-c',
                    'apt-get update && apt-get install -y ' +
                    'build-essential python3-dev ' +
                    'libfreetype6-dev libpng-dev libjpeg-dev ' +
                    'zlib1g-dev libopenblas-dev gfortran ' +
                    'libffi-dev libssl-dev libxml2-dev libxslt1-dev ' +
                    'libpq-dev libtiff-dev liblcms2-dev libwebp-dev ' +
                    'tcl-dev tk-dev'
                ]
            elif os_type == 'redhat':
                # RedHat/CentOS - sử dụng yum
                install_cmd = [
                    'docker', 'exec', container, 'yum', 'install', '-y',
                    'gcc', 'gcc-c++', 'make', 'python3-devel',
                    'freetype-devel', 'libpng-devel', 'libjpeg-turbo-devel',
                    'zlib-devel', 'openblas-devel', 'gcc-gfortran',
                    'libffi-devel', 'openssl-devel', 'libxml2-devel', 'libxslt-devel',
                    'postgresql-devel', 'libtiff-devel', 'lcms2-devel', 'libwebp-devel'
                ]
            else:
                self.log_output("⚠️ Không nhận dạng được OS, thử cài bằng Alpine commands...\n")
                install_cmd = [
                    'docker', 'exec', container, 'apk', 'add', '--no-cache',
                    'build-base', 'python3-dev', 'freetype-dev', 'libpng-dev',
                    'libjpeg-turbo-dev', 'zlib-dev', 'openblas-dev', 'gfortran'
                ]
            
            result = subprocess.run(
                install_cmd,
                capture_output=True,
                encoding='utf-8',
                errors='replace',
                timeout=300
            )
            
            self.log_output(result.stdout)
            if result.stderr:
                self.log_output(result.stderr)
            
            if result.returncode == 0:
                self.log_output("\n✅ Dependencies đã được cài đặt thành công!\n")
                self.log_output("📦 Sẵn sàng cài matplotlib, pillow, numpy, scipy, etc.\n\n")
                return True
            else:
                self.log_output("\n⚠️ Không thể cài đặt một số dependencies, nhưng sẽ thử tiếp...\n")
                return False  # Vẫn thử cài package
                
        except Exception as e:
            self.log_output(f"\n⚠️ Lỗi khi cài dependencies: {str(e)}\n")
            return False
    
    def parse_missing_dependency(self, error_output):
        """Parse lỗi để tìm dependency bị thiếu"""
        import re
        
        # Pattern: "The headers or library files could not be found for jpeg"
        match = re.search(r'could not be found for (\w+)', error_output)
        if match:
            return match.group(1)
        
        # Pattern: "fatal error: Python.h: No such file or directory"
        if 'Python.h' in error_output:
            return 'python-dev'
        
        # Pattern: "error: command 'gcc' failed"
        if "command 'gcc' failed" in error_output or 'gcc: not found' in error_output:
            return 'gcc'
        
        return None
    
    def install_package(self):
        """Cài đặt thư viện - với auto dependency installation"""
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
        
        # Phát hiện OS và cài dependencies nếu cần
        compile_packages = ['matplotlib', 'numpy', 'scipy', 'pandas', 'pillow', 'lxml', 
                           'cryptography', 'psycopg2', 'opencv-python', 'scikit-learn']
        needs_compile = any(pkg in package.lower() for pkg in compile_packages)
        
        # Build command
        def build_pip_command():
            cmd = ['docker', 'exec', container, 'python3', '-m', 'pip', 'install']
            if self.no_cache_var.get():
                cmd.append('--no-cache-dir')
            if self.upgrade_var.get():
                cmd.append('--upgrade')
            cmd.extend(['--timeout', '300'])
            cmd.append(package)
            return cmd
        
        # Log command
        self.log_output(f"\n{'='*80}\n")
        self.log_output(f"🚀 Đang cài đặt: {package}\n")
        self.log_output(f"📦 Container: {container}\n")
        self.log_output(f"⏰ Bắt đầu lúc: {datetime.now().strftime('%H:%M:%S')}\n")
        self.log_output(f"{'='*80}\n\n")
        
        if needs_compile:
            self.log_output(f"📋 Thư viện '{package}' cần compile từ source code\n")
            self.log_output(f"🔧 Sẽ tự động cài đặt build tools nếu cần...\n\n")
        
        # Special warning for packages that take long to build
        long_build_packages = ['numpy', 'scipy', 'pandas', 'torch', 'tensorflow', 'opencv-python']
        if any(pkg in package.lower() for pkg in long_build_packages):
            self.log_output(f"⚠️ LƯU Ý: {package} có thể mất 5-15 phút để build!\n")
            self.log_output(f"💡 App vẫn đang chạy, vui lòng đợi... Theo dõi log bên dưới.\n\n")
        
        self.update_status(f"⏳ Đang cài đặt {package}... (có thể mất vài phút)")
        self.is_installing = True
        self.install_btn.config(state='disabled', text='⏳ Đang cài...')
        self.list_btn.config(state='disabled')
        self.uninstall_btn.config(state='disabled')
        self.reset_progress()
        
        # Run in thread - THÔNG MINH với auto-retry
        def run_install():
            start_time = time.time()
            last_update = start_time
            line_count = 0
            current_stage = "Đang chuẩn bị..."
            deps_installed = False
            
            try:
                # BƯỚC 1: Cài dependencies trước nếu cần compile
                if needs_compile:
                    os_type = self.detect_os_type(container)
                    self.parent.after(0, lambda: self.log_output(f"🖥️ Phát hiện OS: {os_type}\n"))
                    
                    if os_type != 'unknown':
                        deps_installed = self.install_dependencies_sync(container, os_type)
                    else:
                        self.parent.after(0, lambda: self.log_output(
                            "⚠️ Không nhận dạng được OS, sẽ thử cài trực tiếp...\n\n"))
                
                # BƯỚC 2: Thử cài package (lần đầu)
                cmd = build_pip_command()
                self.parent.after(0, lambda: self.log_output(f"💻 Lệnh: {' '.join(cmd)}\n\n"))
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    encoding='utf-8',
                    errors='replace'
                )
                
                # Collect all output to parse errors if needed
                all_output = []
                for line in iter(process.stdout.readline, ''):
                    if line:
                        all_output.append(line)
                        self.parent.after(0, lambda l=line: self.log_output(l))
                        line_count += 1
                        
                        # Parse and update progress bar
                        progress = self.parse_progress(line)
                        if progress is not None:
                            self.parent.after(0, lambda p=progress, s=current_stage: 
                                self.update_progress(p, f"{s} {int(p)}%"))
                        
                        # Detect important stages
                        line_lower = line.lower()
                        
                        if 'collecting' in line_lower:
                            current_stage = "📥 Đang tải"
                            self.parent.after(0, lambda: self.update_progress(5, "📥 Đang tải thông tin..."))
                        elif 'downloading' in line_lower:
                            current_stage = "⬇️ Đang download"
                        elif 'installing build dependencies' in line_lower and 'started' in line_lower:
                            current_stage = "🔧 Dependencies"
                            self.parent.after(0, lambda: self.update_progress(30, "🔧 Cài dependencies..."))
                        elif 'getting requirements' in line_lower and 'started' in line_lower:
                            current_stage = "📋 Requirements"
                            self.parent.after(0, lambda: self.update_progress(40, "📋 Lấy requirements..."))
                        elif 'preparing metadata' in line_lower and 'started' in line_lower:
                            current_stage = "📝 Metadata"
                            self.parent.after(0, lambda: self.update_progress(50, "📝 Chuẩn bị metadata..."))
                        elif 'building wheel' in line_lower and 'started' in line_lower:
                            current_stage = "⚙️ Build"
                            self.parent.after(0, lambda: self.log_output(
                                f"⚙️ ĐANG BUILD: Quá trình này có thể mất 5-15 phút...\n"))
                            self.parent.after(0, lambda: self.update_progress(60, "⚙️ Đang build wheel..."))
                        elif 'building wheel' in line_lower and 'still running' in line_lower:
                            elapsed = int(time.time() - start_time)
                            mins, secs = divmod(elapsed, 60)
                            build_progress = min(60 + (mins * 5), 90)
                            time_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"
                            self.parent.after(0, lambda p=build_progress, t=time_str: 
                                self.update_progress(p, f"⚙️ Build... {t}"))
                        elif 'building wheel' in line_lower and 'finished' in line_lower:
                            self.parent.after(0, lambda: self.update_progress(92, "✅ Build xong!"))
                        elif 'installing collected packages' in line_lower:
                            current_stage = "📦 Cài đặt"
                            self.parent.after(0, lambda: self.update_progress(95, "📦 Đang cài đặt..."))
                        elif 'successfully installed' in line_lower:
                            self.parent.after(0, lambda: self.update_progress(100, "✅ Hoàn thành!"))
                        
                        # Update elapsed time periodically
                        current_time = time.time()
                        if current_time - last_update >= 5:
                            elapsed = int(current_time - start_time)
                            mins, secs = divmod(elapsed, 60)
                            time_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"
                            self.parent.after(0, lambda t=time_str, c=current_stage: 
                                self.update_status(f"⏳ {c} {package}... ({t})"))
                            last_update = current_time
                
                process.wait()
                full_output = ''.join(all_output)
                
                # Calculate total time
                total_time = int(time.time() - start_time)
                mins, secs = divmod(total_time, 60)
                time_str = f"{mins} phút {secs} giây" if mins > 0 else f"{secs} giây"
                
                # BƯỚC 3: Xử lý kết quả
                if process.returncode == 0:
                    self.parent.after(0, lambda: self.update_progress(100, "✅ Hoàn thành!"))
                    self.parent.after(0, lambda: self.log_output(f"\n✅ Cài đặt thành công: {package}\n"))
                    self.parent.after(0, lambda t=time_str: self.log_output(f"⏰ Tổng thời gian: {t}\n"))
                    self.parent.after(0, lambda: self.update_status(f"✅ Đã cài {package}"))
                    self.parent.after(0, lambda: messagebox.showinfo("Thành công", 
                        f"Đã cài đặt {package} thành công!\n\nThời gian: {time_str}"))
                else:
                    # THẤT BẠI - Parse lỗi và thử fix
                    self.parent.after(0, lambda: self.log_output(f"\n❌ Cài đặt thất bại (lần 1)\n"))
                    
                    missing_dep = self.parse_missing_dependency(full_output)
                    
                    if missing_dep and not deps_installed:
                        # Phát hiện thiếu dependency - thử cài và retry
                        self.parent.after(0, lambda d=missing_dep: self.log_output(
                            f"\n🔍 Phát hiện thiếu dependency: {d}\n"))
                        self.parent.after(0, lambda: self.log_output(
                            f"🔧 Đang cài build tools và thử lại...\n"))
                        
                        os_type = self.detect_os_type(container)
                        if os_type != 'unknown':
                            deps_ok = self.install_dependencies_sync(container, os_type)
                            
                            if deps_ok:
                                # RETRY lần 2
                                self.parent.after(0, lambda: self.log_output(
                                    f"\n{'='*80}\n"))
                                self.parent.after(0, lambda: self.log_output(
                                    f"🔄 THỬ LẠI LẦN 2 sau khi cài dependencies...\n"))
                                self.parent.after(0, lambda: self.log_output(
                                    f"{'='*80}\n\n"))
                                
                                retry_process = subprocess.Popen(
                                    cmd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    text=True,
                                    encoding='utf-8',
                                    errors='replace'
                                )
                                
                                for line in iter(retry_process.stdout.readline, ''):
                                    if line:
                                        self.parent.after(0, lambda l=line: self.log_output(l))
                                
                                retry_process.wait()
                                
                                if retry_process.returncode == 0:
                                    total_time2 = int(time.time() - start_time)
                                    mins2, secs2 = divmod(total_time2, 60)
                                    time_str2 = f"{mins2} phút {secs2} giây" if mins2 > 0 else f"{secs2} giây"
                                    
                                    self.parent.after(0, lambda: self.update_progress(100, "✅ Hoàn thành!"))
                                    self.parent.after(0, lambda: self.log_output(
                                        f"\n✅ Cài đặt thành công sau retry!\n"))
                                    self.parent.after(0, lambda t=time_str2: self.log_output(
                                        f"⏰ Tổng thời gian: {t}\n"))
                                    self.parent.after(0, lambda: self.update_status(f"✅ Đã cài {package}"))
                                    self.parent.after(0, lambda: messagebox.showinfo("Thành công", 
                                        f"Đã cài đặt {package} thành công!\n\nThời gian: {time_str2}"))
                                    return  # SUCCESS!
                    
                    # Vẫn thất bại
                    self.parent.after(0, lambda: self.reset_progress())
                    self.parent.after(0, lambda: self.log_output(
                        f"\n❌ Cài đặt thất bại với mã lỗi: {process.returncode}\n"))
                    self.parent.after(0, lambda: self.log_output(
                        f"💡 Tip: Kiểm tra log ở trên để biết chi tiết lỗi\n"))
                    self.parent.after(0, lambda: self.update_status("❌ Cài đặt thất bại"))
                    self.parent.after(0, lambda: messagebox.showerror("Lỗi", 
                        f"Cài đặt {package} thất bại!\n\nKiểm tra log để biết chi tiết."))
                
            except Exception as e:
                error_msg = str(e)
                self.parent.after(0, lambda: self.reset_progress())
                self.parent.after(0, lambda: self.log_output(f"\n❌ Lỗi: {error_msg}\n"))
                self.parent.after(0, lambda: self.update_status("❌ Lỗi cài đặt"))
                self.parent.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi: {error_msg}"))
            
            finally:
                self.is_installing = False
                self.parent.after(0, lambda: self.install_btn.config(state='normal', text='✅ Cài đặt'))
                self.parent.after(0, lambda: self.list_btn.config(state='normal'))
                self.parent.after(0, lambda: self.uninstall_btn.config(state='normal'))
        
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
                    encoding='utf-8',
                    errors='replace',
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
                    encoding='utf-8',
                    errors='replace',
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
