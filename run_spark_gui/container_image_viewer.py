"""
Container Image Viewer - Xem ảnh/biểu đồ trong Docker container (v2 - Modern UI)
Hỗ trợ xem và tải về ảnh từ container (PNG, JPG, etc.)
"""

import subprocess
import os
import tempfile
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import sys
import json
from typing import Optional, Callable, List, Tuple
from datetime import datetime


class ContainerImageViewer:
    """
    GUI hiện đại để xem và tải ảnh từ Docker container
    """
    
    # Recent paths storage
    RECENT_PATHS_FILE = "recent_paths.json"
    
    def __init__(self, parent=None, log_callback: Optional[Callable] = None):
        """
        Args:
            parent: Parent window (None = tạo window mới)
            log_callback: Callback(message, tag) để log
        """
        self.parent = parent
        self.log_callback = log_callback
        self.current_image_path = None
        self.current_container = None
        self.current_pil_image = None
        self.current_photo = None
        self.zoom_level = 1.0
        self.recent_paths = self.load_recent_paths()
        
        # Create window
        if parent is None:
            self.window = tk.Tk()
            self.window.title("📊 Container Image Viewer")
        else:
            self.window = tk.Toplevel(parent)
            self.window.title("📊 Container Image Viewer")
        
        self.window.geometry("1100x750")
        self.window.minsize(800, 600)
        self.setup_ui()
        
    def load_recent_paths(self) -> List[str]:
        """Load recent paths from file"""
        try:
            if os.path.exists(self.RECENT_PATHS_FILE):
                with open(self.RECENT_PATHS_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return ['/tmp/', '/opt/spark/work/', '/output/']
    
    def save_recent_path(self, path: str):
        """Save path to recent paths"""
        if path not in self.recent_paths:
            self.recent_paths.insert(0, path)
            self.recent_paths = self.recent_paths[:10]  # Keep last 10
            try:
                with open(self.RECENT_PATHS_FILE, 'w') as f:
                    json.dump(self.recent_paths, f)
            except:
                pass
    
    def setup_ui(self):
        """Setup UI components - Modern Layout"""
        
        # ========== TOP TOOLBAR ==========
        toolbar = ttk.Frame(self.window, padding=(10, 10, 10, 5))
        toolbar.pack(fill=tk.X, side=tk.TOP)
        
        # Row 1: Container + Path
        row1 = ttk.Frame(toolbar)
        row1.pack(fill=tk.X, pady=(0, 8))
        
        # Container selection
        ttk.Label(row1, text="🐳 Container:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 8))
        self.container_var = tk.StringVar(value="spark-worker")
        container_combo = ttk.Combobox(
            row1,
            textvariable=self.container_var,
            values=['spark-worker', 'spark-master', 'namenode', 'datanode', 'jupyter-notebook'],
            width=18,
            state='readonly',
            font=('Arial', 9)
        )
        container_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        # Path with recent dropdown
        ttk.Label(row1, text="📁 Path:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 8))
        self.path_var = tk.StringVar(value="/tmp/")
        path_combo = ttk.Combobox(
            row1,
            textvariable=self.path_var,
            values=self.recent_paths,
            width=35,
            font=('Arial', 9)
        )
        path_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Quick path buttons
        ttk.Button(
            row1,
            text="💡 /tmp/",
            command=lambda: self.path_var.set("/tmp/"),
            width=10
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            row1,
            text="⚡ /output/",
            command=lambda: self.path_var.set("/output/"),
            width=10
        ).pack(side=tk.LEFT, padx=2)
        
        # Row 2: Action buttons
        row2 = ttk.Frame(toolbar)
        row2.pack(fill=tk.X)
        
        # Large action buttons
        btn_frame = ttk.Frame(row2)
        btn_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(
            btn_frame,
            text="📂 Browse Files",
            command=self.browse_container,
            width=16
        ).pack(side=tk.LEFT, padx=3)
        
        ttk.Button(
            btn_frame,
            text="👁️ View Image",
            command=self.view_image,
            width=15
        ).pack(side=tk.LEFT, padx=3)
        
        ttk.Button(
            btn_frame,
            text="💾 Download",
            command=self.download_image,
            width=14
        ).pack(side=tk.LEFT, padx=3)
        
        ttk.Button(
            btn_frame,
            text="🔄 Refresh",
            command=self.refresh_view,
            width=12
        ).pack(side=tk.LEFT, padx=3)
        
        ttk.Button(
            btn_frame,
            text="🗑️ Clear",
            command=self.clear_view,
            width=10
        ).pack(side=tk.LEFT, padx=3)
        
        # ========== ZOOM CONTROLS (Right side) ==========
        zoom_frame = ttk.LabelFrame(row2, text="🔍 Zoom", padding=5)
        zoom_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(
            zoom_frame,
            text="➕",
            command=self.zoom_in,
            width=3
        ).pack(side=tk.LEFT, padx=2)
        
        self.zoom_label = ttk.Label(zoom_frame, text="100%", width=6, anchor=tk.CENTER)
        self.zoom_label.pack(side=tk.LEFT, padx=3)
        
        ttk.Button(
            zoom_frame,
            text="➖",
            command=self.zoom_out,
            width=3
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            zoom_frame,
            text="🔄",
            command=self.zoom_reset,
            width=3
        ).pack(side=tk.LEFT, padx=2)
        
        # ========== IMAGE DISPLAY AREA ==========
        display_frame = ttk.Frame(self.window)
        display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        # Canvas with scrollbars for image
        canvas_frame = ttk.Frame(display_frame, relief=tk.SUNKEN, borderwidth=2)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scroll = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Canvas with better styling
        self.canvas = tk.Canvas(
            canvas_frame,
            bg='#2b2b2b',
            highlightthickness=0,
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        v_scroll.config(command=self.canvas.yview)
        h_scroll.config(command=self.canvas.xview)
        
        # Bind mouse wheel for scrolling
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Control-MouseWheel>", self._on_ctrl_mousewheel)
        
        # Placeholder text
        self.placeholder_id = self.canvas.create_text(
            400, 300,
            text="📊 No image loaded\n\n💡 Click 'Browse Files' or enter path and click 'View Image'",
            fill='#888888',
            font=('Arial', 12),
            justify=tk.CENTER
        )
        
        # ========== STATUS BAR ==========
        status_frame = ttk.Frame(self.window, relief=tk.SUNKEN)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_var = tk.StringVar(value="✅ Ready - Select a container and browse images")
        status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            anchor=tk.W,
            font=('Arial', 9)
        )
        status_label.pack(fill=tk.X, side=tk.LEFT, padx=8, pady=4)
        
        # Image info label (right side)
        self.info_var = tk.StringVar(value="")
        info_label = ttk.Label(
            status_frame,
            textvariable=self.info_var,
            anchor=tk.E,
            font=('Arial', 8),
            foreground='#666666'
        )
        info_label.pack(fill=tk.X, side=tk.RIGHT, padx=8, pady=4)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel for scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _on_ctrl_mousewheel(self, event):
        """Handle Ctrl+MouseWheel for zooming"""
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def zoom_in(self):
        """Zoom in image"""
        if self.current_pil_image:
            self.zoom_level = min(self.zoom_level * 1.2, 5.0)
            self.update_zoom()
    
    def zoom_out(self):
        """Zoom out image"""
        if self.current_pil_image:
            self.zoom_level = max(self.zoom_level / 1.2, 0.1)
            self.update_zoom()
    
    def zoom_reset(self):
        """Reset zoom to 100%"""
        if self.current_pil_image:
            self.zoom_level = 1.0
            self.update_zoom()
    
    def update_zoom(self):
        """Update image display with current zoom level"""
        if not self.current_pil_image:
            return
        
        # Calculate new size
        orig_width, orig_height = self.current_pil_image.size
        new_width = int(orig_width * self.zoom_level)
        new_height = int(orig_height * self.zoom_level)
        
        # Resize image
        resized = self.current_pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.current_photo = ImageTk.PhotoImage(resized)
        
        # Update canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.current_photo)
        self.canvas.config(scrollregion=(0, 0, new_width, new_height))
        
        # Update zoom label
        self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")
        self.info_var.set(f"Size: {new_width}×{new_height} | Zoom: {int(self.zoom_level * 100)}%")
    
    def clear_view(self):
        """Clear the current view"""
        self.canvas.delete("all")
        self.placeholder_id = self.canvas.create_text(
            400, 300,
            text="📊 No image loaded\n\n💡 Click 'Browse Files' or enter path and click 'View Image'",
            fill='#888888',
            font=('Arial', 12),
            justify=tk.CENTER
        )
        self.current_pil_image = None
        self.current_photo = None
        self.zoom_level = 1.0
        self.zoom_label.config(text="100%")
        self.info_var.set("")
        self.status_var.set("✅ Ready")
    
    def log(self, msg: str, tag: str = 'info'):
        """Log message"""
        if self.log_callback:
            self.log_callback(msg, tag)
        else:
            print(f"[{tag}] {msg}")
    
    def get_subprocess_params(self):
        """Get subprocess params for hidden console"""
        params = {}
        if sys.platform == 'win32':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            params['startupinfo'] = startupinfo
            params['creationflags'] = subprocess.CREATE_NO_WINDOW
        return params
    
    def browse_container(self):
        """Browse files in container - Modern UI"""
        container = self.container_var.get()
        path = self.path_var.get()
        
        # Save to recent paths
        self.save_recent_path(path)
        
        try:
            self.status_var.set(f"🔍 Browsing {container}:{path}...")
            
            # List files in container
            cmd = ['docker', 'exec', container, 'ls', '-lh', path]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                **self.get_subprocess_params()
            )
            
            if result.returncode != 0:
                messagebox.showerror("❌ Error", f"Failed to list files:\n{result.stderr}")
                self.status_var.set("❌ Error browsing files")
                return
            
            # Parse files (skip directories)
            lines = result.stdout.strip().split('\n')
            files = []
            for line in lines[1:]:  # Skip "total" line
                parts = line.split()
                if len(parts) >= 9 and not line.startswith('d'):
                    filename = ' '.join(parts[8:])
                    size = parts[4]
                    files.append((filename, size))
            
            # Filter image files
            image_files = [
                (f, s) for f, s in files
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))
            ]
            
            if not image_files:
                messagebox.showinfo("ℹ️ Info", f"No image files found in {path}")
                self.status_var.set("ℹ️ No images found")
                return
            
            # Show modern selection dialog
            self._show_file_browser(container, path, image_files)
            
            self.status_var.set(f"✅ Found {len(image_files)} image(s)")
            
        except subprocess.TimeoutExpired:
            messagebox.showerror("❌ Timeout", "Command timed out")
            self.status_var.set("❌ Timeout")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Failed to browse:\n{str(e)}")
            self.log(f"Browse error: {e}", 'error')
            self.status_var.set("❌ Error")
    
    def _show_file_browser(self, container: str, path: str, image_files: List[Tuple[str, str]]):
        """Show modern file browser dialog"""
        select_window = tk.Toplevel(self.window)
        select_window.title(f"📂 Browse Images - {container}:{path}")
        select_window.geometry("600x500")
        select_window.transient(self.window)
        
        # Header
        header = ttk.Frame(select_window, padding=10)
        header.pack(fill=tk.X)
        
        ttk.Label(
            header,
            text=f"📁 Images in {container}:{path}",
            font=('Arial', 11, 'bold')
        ).pack(side=tk.LEFT)
        
        ttk.Label(
            header,
            text=f"({len(image_files)} files)",
            font=('Arial', 9),
            foreground='#666666'
        ).pack(side=tk.LEFT, padx=10)
        
        # Treeview with size info
        tree_frame = ttk.Frame(select_window, padding=(10, 0, 10, 10))
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree = ttk.Treeview(
            tree_frame,
            columns=('filename', 'size'),
            show='headings',
            yscrollcommand=scrollbar.set,
            height=15
        )
        tree.heading('filename', text='📄 Filename')
        tree.heading('size', text='📏 Size')
        tree.column('filename', width=400)
        tree.column('size', width=100)
        tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=tree.yview)
        
        # Populate tree
        for filename, size in image_files:
            tree.insert('', tk.END, values=(filename, size))
        
        # Button frame
        btn_frame = ttk.Frame(select_window, padding=10)
        btn_frame.pack(fill=tk.X)
        
        def on_view():
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                selected_file = item['values'][0]
                full_path = os.path.join(path, selected_file).replace('\\', '/')
                self.path_var.set(full_path)
                select_window.destroy()
                self.view_image()
            else:
                messagebox.showwarning("⚠️ Warning", "Please select an image first")
        
        ttk.Button(
            btn_frame,
            text="👁️ View Selected",
            command=on_view,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="❌ Cancel",
            command=select_window.destroy,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        # Double-click to view
        tree.bind('<Double-Button-1>', lambda e: on_view())
    
    def view_image(self):
        """View image from container - with modern features"""
        container = self.container_var.get()
        image_path = self.path_var.get()
        
        if not container or not image_path:
            messagebox.showwarning("⚠️ Warning", "Please enter container and image path")
            return
        
        try:
            self.status_var.set("⏳ Loading image...")
            self.log(f"Viewing {container}:{image_path}", 'info')
            
            # Create temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image_path)[1]) as tmp:
                temp_path = tmp.name
            
            # Copy image from container
            cmd = ['docker', 'cp', f'{container}:{image_path}', temp_path]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                **self.get_subprocess_params()
            )
            
            if result.returncode != 0:
                messagebox.showerror("❌ Error", f"Failed to copy image:\n{result.stderr}")
                self.status_var.set("❌ Error loading image")
                return
            
            # Load PIL image
            self.current_pil_image = Image.open(temp_path)
            img_width, img_height = self.current_pil_image.size
            
            # Store current image info
            self.current_container = container
            self.current_image_path = image_path
            
            # Reset zoom
            self.zoom_level = 1.0
            
            # Display image
            self.update_zoom()
            
            # Update status
            file_size = os.path.getsize(temp_path) / 1024  # KB
            self.status_var.set(f"✅ Loaded: {os.path.basename(image_path)}")
            self.info_var.set(f"Original: {img_width}×{img_height} | {file_size:.1f} KB | {self.current_pil_image.mode}")
            
            self.log(f"Displayed: {image_path} ({img_width}×{img_height})", 'success')
            
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass
            
        except FileNotFoundError:
            messagebox.showerror("❌ Error", f"Image not found: {image_path}")
            self.status_var.set("❌ Not found")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Failed to view image:\n{str(e)}")
            self.log(f"View error: {e}", 'error')
            self.status_var.set("❌ Error")
    
    def download_image(self):
        """Download image from container to local"""
        container = self.container_var.get()
        image_path = self.path_var.get()
        
        if not container or not image_path:
            messagebox.showwarning("⚠️ Warning", "Please enter container and image path")
            return
        
        try:
            # Ask save location
            filename = os.path.basename(image_path)
            save_path = filedialog.asksaveasfilename(
                title="💾 Save Image As",
                defaultextension=os.path.splitext(filename)[1],
                initialfile=filename,
                filetypes=[
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg;*.jpeg"),
                    ("GIF files", "*.gif"),
                    ("BMP files", "*.bmp"),
                    ("All files", "*.*")
                ]
            )
            
            if not save_path:
                return
            
            self.status_var.set("⏳ Downloading...")
            
            # Copy from container
            cmd = ['docker', 'cp', f'{container}:{image_path}', save_path]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                **self.get_subprocess_params()
            )
            
            if result.returncode != 0:
                messagebox.showerror("❌ Error", f"Failed to download:\n{result.stderr}")
                self.status_var.set("❌ Download failed")
                return
            
            file_size = os.path.getsize(save_path) / 1024  # KB
            messagebox.showinfo("✅ Success", f"Downloaded successfully!\n\nLocation: {save_path}\nSize: {file_size:.1f} KB")
            self.status_var.set(f"✅ Downloaded: {os.path.basename(save_path)}")
            self.log(f"✅ Downloaded: {save_path}", 'success')
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"Failed to download:\n{str(e)}")
            self.log(f"Download error: {e}", 'error')
            self.status_var.set("❌ Error")
    
    def refresh_view(self):
        """Refresh current view"""
        if self.current_image_path and self.current_pil_image:
            # Reload the current image
            self.view_image()
            self.log("🔄 Refreshed image", 'info')
        else:
            messagebox.showinfo("ℹ️ Info", "No image loaded to refresh")
    
    def show(self):
        """Show window"""
        if self.parent is None:
            self.window.mainloop()


def view_container_image(
    container: str,
    image_path: str,
    parent=None,
    log_callback: Optional[Callable] = None
):
    """
    Quick function to view an image from container
    
    Example:
        view_container_image(
            container='spark-worker',
            image_path='/tmp/chart.png'
        )
    """
    viewer = ContainerImageViewer(parent=parent, log_callback=log_callback)
    viewer.container_var.set(container)
    viewer.path_var.set(image_path)
    viewer.view_image()
    viewer.show()


# Example usage
if __name__ == "__main__":
    # Test viewer
    viewer = ContainerImageViewer()
    viewer.show()
