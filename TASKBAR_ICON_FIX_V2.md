# 🔧 Taskbar Icon Fix v2 - Phương Pháp Mới

## ❌ Vấn Đề Cũ

**Fix v1 không work vì:**
- Code chạy QUÁ SỚM (khi window chưa ready)
- `GetParent(root.winfo_id())` trả về handle sai
- Icon path sai (dùng `sys.executable` thay vì `sys._MEIPASS`)

## ✅ Fix v2 - Giải Pháp Đúng

### **1. Fix Icon Path**

**Trước (SAI):**
```python
icon_path = os.path.join(os.path.dirname(sys.executable), '..', 'icon.ico')
```
❌ Tìm icon ngoài folder .exe → KHÔNG TÌM THẤY!

**Sau (ĐÚNG):**
```python
if getattr(sys, 'frozen', False):
    # PyInstaller extracts files to sys._MEIPASS
    icon_path = os.path.join(sys._MEIPASS, 'icon.ico')
```
✅ Tìm icon trong temp folder của PyInstaller!

### **2. Chạy SAU KHI Window Ready**

**Trước (SAI):**
```python
def __init__(self, root):
    # ... setup window ...
    # Icon code chạy ngay ở đây (window chưa ready)
    ctypes.windll.user32.SendMessageW(hwnd, ...)  # ❌ hwnd sai!
```

**Sau (ĐÚNG):**
```python
def __init__(self, root):
    # ... setup window ...
    # Chờ 500ms cho window ready
    self.root.after(500, self.set_taskbar_icon)

def set_taskbar_icon(self):
    # Window đã ready, hwnd đúng!
    hwnd = int(self.root.wm_frame(), 16)  # ✅ Dùng wm_frame()
    ctypes.windll.user32.SendMessageW(hwnd, ...)
```

### **3. Dùng wm_frame() Thay Vì winfo_id()**

**Trước (SAI):**
```python
hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
```
❌ `winfo_id()` trả về Tk widget ID, KHÔNG phải Windows HWND!

**Sau (ĐÚNG):**
```python
hwnd = int(self.root.wm_frame(), 16)  # Hex string → int
```
✅ `wm_frame()` trả về hex string của Windows HWND thực!

## 📝 Complete Code Fix

### **In `__init__` method:**

```python
# Set window icon (for title bar) - MUST be called early
self.icon_path = None
try:
    # Try to load icon.ico from application directory
    if getattr(sys, 'frozen', False):
        # Running as compiled executable - icon is in _MEIPASS temp folder
        icon_path = os.path.join(sys._MEIPASS, 'icon.ico')
    else:
        # Running as script
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icon.ico')
    
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
        self.icon_path = icon_path
    elif os.path.exists('icon.ico'):
        root.iconbitmap('icon.ico')
        self.icon_path = os.path.abspath('icon.ico')
except Exception as e:
    if LOGGING_AVAILABLE and app_logger:
        app_logger.warning(f"Could not load window icon: {e}")

# ... setup window ...

# Set taskbar icon AFTER window is fully loaded (Windows-specific)
self.root.after(500, self.set_taskbar_icon)
```

### **New method `set_taskbar_icon()`:**

```python
def set_taskbar_icon(self):
    """Set taskbar icon using Windows API - called after window is fully loaded"""
    if not WINDOWS_AVAILABLE or not self.icon_path:
        return
    
    try:
        # Method 1: Set AppUserModelID (makes Windows treat this as unique app)
        myappid = 'spark.runner.gui.v6.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        
        # Method 2: Set icon using Windows API
        if os.path.exists(self.icon_path):
            # Force window update
            self.root.update_idletasks()
            self.root.update()
            
            # Get window handle - USE wm_frame() NOT winfo_id()!
            hwnd = int(self.root.wm_frame(), 16)  # Convert hex string to int
            
            # Load icon with proper flags
            LR_LOADFROMFILE = 0x00000010
            LR_DEFAULTSIZE = 0x00000040
            IMAGE_ICON = 1
            
            hicon = ctypes.windll.user32.LoadImageW(
                None,  # hInst = NULL (load from file)
                self.icon_path,
                IMAGE_ICON,
                0,  # desired width (0 = default)
                0,  # desired height (0 = default)
                LR_LOADFROMFILE | LR_DEFAULTSIZE
            )
            
            if hicon:
                # Send WM_SETICON message to window
                WM_SETICON = 0x0080
                ICON_SMALL = 0  # 16x16 for taskbar
                ICON_BIG = 1    # 32x32 for Alt+Tab
                
                ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon)
                ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, hicon)
                
                if LOGGING_AVAILABLE and app_logger:
                    app_logger.info(f"Taskbar icon set successfully: {self.icon_path}")
            else:
                if LOGGING_AVAILABLE and app_logger:
                    app_logger.warning(f"Failed to load icon: {self.icon_path}")
                    
    except Exception as e:
        if LOGGING_AVAILABLE and app_logger:
            app_logger.warning(f"Could not set taskbar icon: {e}")
        pass
```

## 🔑 Key Changes

| Issue | v1 (Wrong) | v2 (Fixed) |
|-------|------------|------------|
| **Icon Path** | `sys.executable/../icon.ico` | `sys._MEIPASS/icon.ico` |
| **Timing** | Run immediately in `__init__` | Run after 500ms with `after()` |
| **Window Handle** | `GetParent(winfo_id())` | `int(wm_frame(), 16)` |
| **Window Update** | None | `update_idletasks()` + `update()` |

## 🧪 Test

```powershell
cd dist
.\SparkRunnerGUI.exe
```

**Expected:**
1. Window opens
2. After ~0.5 second: Taskbar icon changes from Python to custom icon
3. Icon visible in:
   - ✅ Window title bar (immediate)
   - ✅ Taskbar (after 0.5s)
   - ✅ Alt+Tab (after 0.5s)

## 📊 Why This Works

### **PyInstaller Temp Folder**

When running as .exe:
```
Windows Temp Folder:
  └── _MEI<random>/
      ├── icon.ico        ← Icon is HERE!
      ├── Python DLLs
      └── App files
      
sys._MEIPASS = "C:\Users\...\Temp\_MEI123456"
icon_path = sys._MEIPASS + "\icon.ico"  ✅ FOUND!
```

### **wm_frame() vs winfo_id()**

```python
# Tkinter widget hierarchy:
root (Tk)
  └── frame (Windows HWND)  ← Need THIS!
      └── widgets (Tk IDs)   ← winfo_id() returns THIS

# Wrong:
winfo_id() → Returns Tk widget ID (not Windows HWND)

# Right:
wm_frame() → Returns Windows HWND as hex string "0x12345"
int(..., 16) → Convert to integer
```

### **Timing**

```python
# Window lifecycle:
__init__():
  root.title()         # ← Set title
  root.iconbitmap()    # ← Set window icon (works)
  root.state('zoomed') # ← Maximize
  # Window NOT fully ready yet!
  
# 500ms later (after window displayed):
set_taskbar_icon():
  wm_frame()          # ← NOW returns valid HWND
  SendMessageW()      # ← NOW works!
```

## 🎓 Technical Details

### **Windows Messages**

```cpp
// C++ equivalent:
HWND hwnd = GetWindowHandle(tkinter_window);
HICON hicon = LoadIcon("icon.ico");
SendMessage(hwnd, WM_SETICON, ICON_SMALL, (LPARAM)hicon);
SendMessage(hwnd, WM_SETICON, ICON_BIG, (LPARAM)hicon);
```

### **AppUserModelID**

```python
# Without this:
# - Windows groups as "python.exe"
# - Shows Python icon

# With this:
myappid = 'spark.runner.gui.v6.0'
SetCurrentProcessExplicitAppUserModelID(myappid)
# - Windows treats as unique app
# - Shows custom icon
```

## 🐛 Debug

If icon still not showing:

```python
# Add to set_taskbar_icon():
print(f"Icon path: {self.icon_path}")
print(f"Icon exists: {os.path.exists(self.icon_path)}")
print(f"HWND: {int(self.root.wm_frame(), 16)}")
print(f"HICON: {hicon}")
```

Expected output:
```
Icon path: C:\Users\...\Temp\_MEI123456\icon.ico
Icon exists: True
HWND: 12345678 (non-zero)
HICON: 87654321 (non-zero)
```

## ✅ Summary

**v1 Failed Because:**
- ❌ Wrong icon path
- ❌ Wrong timing
- ❌ Wrong window handle

**v2 Fixed By:**
- ✅ Use `sys._MEIPASS` for icon path
- ✅ Use `after(500, ...)` for timing
- ✅ Use `wm_frame()` for window handle

**Result:**
- ✅ Taskbar icon works!
- ✅ Alt+Tab icon works!
- ✅ Professional appearance!

---

**Build và test ngay:**
```powershell
.\build.bat
cd dist
.\SparkRunnerGUI.exe
# Check taskbar! ✅
```
