"""
UI utility functions for Spark Runner GUI.
"""
import tkinter as tk
from theme import COLORS

def create_tooltip(widget, text):
    """Create a tooltip for a widget"""
    tooltip = None
    
    def on_enter(event):
        nonlocal tooltip
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 25
        
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.configure(bg=COLORS['tooltip_bg'])
        tooltip.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(
            tooltip,
            text=text,
            background=COLORS['tooltip_bg'],
            foreground=COLORS['tooltip_fg'],
            relief=tk.SOLID,
            borderwidth=1,
            font=("Segoe UI", 9),
            padx=8,
            pady=4
        )
        label.pack()
    
    def on_leave(event):
        nonlocal tooltip
        if tooltip:
            tooltip.destroy()
            tooltip = None
    
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)
