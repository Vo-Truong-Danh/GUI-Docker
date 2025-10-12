"""
Theme configuration for Spark Runner GUI - Modern Bright Design
Màu sắc tươi sáng, bo góc hiện đại
"""
import tkinter as tk
from tkinter import ttk

# Modern bright color scheme - Bảng màu tươi sáng hiện đại
COLORS = {
    'bg': '#f8f9fa',           # Nền chính - xám nhạt
    'bg_light': '#ffffff',     # Nền sáng - trắng
    'surface': '#ffffff',      # Bề mặt card - trắng
    'border': '#e9ecef',       # Viền nhẹ
    'shadow': '#dee2e6',       # Bóng
    
    # Primary colors - Màu chính
    'primary': '#4f46e5',      # Indigo sáng
    'primary_hover': '#6366f1', # Indigo hover
    'primary_active': '#4338ca', # Indigo active
    
    # Button colors - Màu nút
    'button': '#6366f1',       # Nút chính - indigo
    'button_hover': '#7c3aed', # Hover - tím
    'button_active': '#5b21b6', # Active - tím đậm
    'button_text': '#ffffff',  # Chữ trên nút
    
    # Semantic colors - Màu ý nghĩa
    'success': '#10b981',      # Xanh lá sáng
    'error': '#ef4444',        # Đỏ sáng
    'warning': '#f59e0b',      # Vàng cam
    'info': '#3b82f6',         # Xanh dương sáng
    
    # Text colors - Màu chữ
    'text': '#1f2937',         # Chữ đen
    'text_muted': '#6b7280',   # Chữ nhạt
    'text_light': '#9ca3af',   # Chữ rất nhạt
    
    # Special backgrounds - Nền đặc biệt
    'bg_log': '#1e293b',       # Nền log - tối để dễ đọc
    'bg_cmd': '#f1f5f9',       # Nền command - xám nhạt
    'input_bg': '#ffffff',     # Nền input
    'input_border': '#d1d5db', # Viền input
    
    # Tooltip colors - Màu tooltip
    'tooltip_bg': '#1f2937',   # Nền tooltip tối
    'tooltip_fg': '#f9fafb',   # Chữ tooltip sáng
    
    # Accent colors - Màu nhấn
    'accent_blue': '#60a5fa',  # Xanh dương nhạt
    'accent_green': '#34d399', # Xanh lá nhạt
    'accent_purple': '#a78bfa', # Tím nhạt
    'accent_pink': '#f472b6',  # Hồng
    'accent_yellow': '#fbbf24', # Vàng
}

def setup_theme(root):
    """
    Thiết lập theme hiện đại với màu sắc tươi sáng và bo góc
    Configure modern theme with bright colors and rounded corners
    """
    style = ttk.Style()
    try:
        style.theme_use('clam')
    except tk.TclError:
        pass

    # === Global Configuration ===
    root.configure(bg=COLORS['bg'])
    root.option_add('*Font', ('Segoe UI', 10))
    root.option_add('*Foreground', COLORS['text'])
    root.option_add('*Background', COLORS['bg_light'])
    
    # Selection colors
    root.option_add('*selectBackground', COLORS['primary'])
    root.option_add('*selectForeground', COLORS['button_text'])

    # === Frames - Bo góc hiện đại ===
    style.configure('TFrame', 
                   background=COLORS['bg'])
    
    style.configure('Card.TFrame', 
                   background=COLORS['surface'],
                   relief='flat',
                   borderwidth=0)
    
    style.configure('Left.TFrame',
                   background=COLORS['bg_light'])
    
    style.configure('Right.TFrame',
                   background=COLORS['bg_log'])

    # === Labels - Nhãn ===
    style.configure('TLabel', 
                   background=COLORS['bg'],
                   foreground=COLORS['text'],
                   font=('Segoe UI', 10))
    
    style.configure('Title.TLabel',
                   background=COLORS['bg_light'],
                   foreground=COLORS['primary'],
                   font=('Segoe UI', 14, 'bold'))
    
    style.configure('Section.TLabel',
                   background=COLORS['bg_light'],
                   foreground=COLORS['text'],
                   font=('Segoe UI', 11, 'bold'))
    
    style.configure('Info.TLabel',
                   background=COLORS['bg_light'],
                   foreground=COLORS['text_muted'],
                   font=('Segoe UI', 9))
    
    style.configure('Status.TLabel',
                   background=COLORS['bg_light'],
                   foreground=COLORS['text_muted'],
                   font=('Segoe UI', 9),
                   padding=(10, 6))

    # === LabelFrame - Khung có nhãn (bo góc) ===
    style.configure('TLabelframe',
                   background=COLORS['surface'],
                   bordercolor=COLORS['border'],
                   relief='solid',
                   borderwidth=1,
                   padding=10)
    
    style.configure('TLabelframe.Label',
                   background=COLORS['surface'],
                   foreground=COLORS['primary'],
                   font=('Segoe UI', 10, 'bold'),
                   padding=(10, 4))
    
    style.configure('Card.TLabelframe',
                   background=COLORS['surface'],
                   bordercolor=COLORS['primary'],
                   relief='solid',
                   borderwidth=2)

    # === Notebook Tabs - Tab hiện đại ===
    style.configure('TNotebook',
                   background=COLORS['bg'],
                   borderwidth=0)
    
    style.configure('TNotebook.Tab',
                   background=COLORS['bg'],
                   foreground=COLORS['text_muted'],
                   padding=(20, 12),
                   font=('Segoe UI', 11, 'bold'),
                   borderwidth=0)
    
    style.map('TNotebook.Tab',
             background=[('selected', COLORS['primary']), 
                        ('active', COLORS['primary_hover'])],
             foreground=[('selected', COLORS['button_text']), 
                        ('active', COLORS['button_text'])])

    # === Buttons - Nút bấm hiện đại với bo góc ===
    style.configure('TButton',
                   background=COLORS['button'],
                   foreground=COLORS['button_text'],
                   font=('Segoe UI', 9, 'bold'),
                   padding=(12, 8),
                   borderwidth=0,
                   relief='flat',
                   focuscolor='none')
    
    style.map('TButton',
             background=[('active', COLORS['button_hover']),
                        ('pressed', COLORS['button_active']),
                        ('disabled', COLORS['border'])],
             foreground=[('disabled', COLORS['text_muted'])],
             relief=[('pressed', 'flat')])
    
    # Success button - Nút thành công (xanh lá)
    style.configure('Success.TButton',
                   background=COLORS['success'],
                   foreground=COLORS['button_text'],
                   font=('Segoe UI', 9, 'bold'),
                   padding=(12, 8),
                   borderwidth=0,
                   focuscolor='none')
    
    style.map('Success.TButton',
             background=[('active', '#059669'),
                        ('pressed', '#047857')],
             relief=[('pressed', 'flat')])
    
    # Action button - Nút hành động (xanh dương)
    style.configure('Action.TButton',
                   background=COLORS['info'],
                   foreground=COLORS['button_text'],
                   font=('Segoe UI', 9, 'bold'),
                   padding=(12, 8),
                   borderwidth=0,
                   focuscolor='none')
    
    style.map('Action.TButton',
             background=[('active', '#2563eb'),
                        ('pressed', '#1d4ed8')],
             relief=[('pressed', 'flat')])
    
    # Secondary button - Nút phụ (xám)
    style.configure('Secondary.TButton',
                   background=COLORS['border'],
                   foreground=COLORS['text'],
                   font=('Segoe UI', 9),
                   padding=(12, 8),
                   borderwidth=0,
                   focuscolor='none')
    
    style.map('Secondary.TButton',
             background=[('active', COLORS['shadow'])],
             relief=[('pressed', 'flat')])

    # === Entry Fields - Ô nhập liệu (bo góc) ===
    style.configure('TEntry',
                   fieldbackground=COLORS['input_bg'],
                   foreground=COLORS['text'],
                   bordercolor=COLORS['input_border'],
                   insertcolor=COLORS['primary'],
                   padding=8,
                   relief='solid',
                   borderwidth=1)
    
    style.map('TEntry',
             bordercolor=[('focus', COLORS['primary']),
                         ('!focus', COLORS['input_border'])],
             lightcolor=[('focus', COLORS['primary'])],
             darkcolor=[('focus', COLORS['primary'])])

    # === Combobox - Hộp chọn (bo góc) ===
    style.configure('TCombobox',
                   fieldbackground=COLORS['input_bg'],
                   background=COLORS['input_bg'],
                   foreground=COLORS['text'],
                   bordercolor=COLORS['input_border'],
                   arrowsize=14,
                   padding=8,
                   relief='solid',
                   borderwidth=1)
    
    style.map('TCombobox',
             bordercolor=[('focus', COLORS['primary']),
                         ('!focus', COLORS['input_border'])],
             fieldbackground=[('readonly', COLORS['input_bg']),
                             ('disabled', COLORS['bg'])],
             lightcolor=[('focus', COLORS['primary'])],
             darkcolor=[('focus', COLORS['primary'])])

    # === Checkbuttons - Ô chọn ===
    style.configure('TCheckbutton',
                   background=COLORS['bg_light'],
                   foreground=COLORS['text'],
                   font=('Segoe UI', 10))

    # === Progressbar - Thanh tiến trình (bo góc) ===
    style.configure('Horizontal.TProgressbar',
                   background=COLORS['primary'],
                   troughcolor=COLORS['border'],
                   borderwidth=0,
                   thickness=6,
                   relief='flat')
    
    style.configure('Success.Horizontal.TProgressbar',
                   background=COLORS['success'],
                   troughcolor=COLORS['border'],
                   borderwidth=0,
                   thickness=6)
    
    style.configure('Accent.Horizontal.TProgressbar',
                   background=COLORS['accent_blue'],
                   troughcolor=COLORS['border'],
                   borderwidth=0,
                   thickness=6)

    # === Treeview - Bảng dữ liệu ===
    style.configure('Treeview',
                   background=COLORS['input_bg'],
                   fieldbackground=COLORS['input_bg'],
                   foreground=COLORS['text'],
                   borderwidth=1,
                   relief='solid',
                   bordercolor=COLORS['border'],
                   rowheight=28)
    
    style.map('Treeview',
             background=[('selected', COLORS['primary'])],
             foreground=[('selected', COLORS['button_text'])])
    
    style.configure('Treeview.Heading',
                   background=COLORS['bg'],
                   foreground=COLORS['text'],
                   font=('Segoe UI', 10, 'bold'),
                   borderwidth=1,
                   relief='flat')
    
    style.map('Treeview.Heading',
             background=[('active', COLORS['primary'])],
             foreground=[('active', COLORS['button_text'])])

    # === Scrollbars - Thanh cuộn hiện đại ===
    style.configure('Vertical.TScrollbar',
                   background=COLORS['border'],
                   troughcolor=COLORS['bg'],
                   borderwidth=0,
                   arrowcolor=COLORS['text'])
    
    style.map('Vertical.TScrollbar',
             background=[('active', COLORS['shadow']),
                        ('pressed', COLORS['primary'])])
    
    style.configure('Horizontal.TScrollbar',
                   background=COLORS['border'],
                   troughcolor=COLORS['bg'],
                   borderwidth=0,
                   arrowcolor=COLORS['text'])
    
    style.map('Horizontal.TScrollbar',
             background=[('active', COLORS['shadow']),
                        ('pressed', COLORS['primary'])])

    return style
