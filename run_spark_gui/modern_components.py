"""
Modern UI Components Library for Spark Runner GUI
Reusable, well-designed components following modern design principles

Components included:
- ModernCard: Card container with elevation
- ModernButton: Various button styles  
- ModernInput: Enhanced input fields
- ModernBadge: Status badges
- ModernAlert: Alert/notification boxes
- ModernModal: Modal dialogs
- ModernTooltip: Enhanced tooltips
- ModernProgressCard: Progress indicator with details
"""

import tkinter as tk
from tkinter import ttk
from modern_theme import ModernTheme, Typography, Spacing, LightTheme, ColorPalette


# ============================================================================
# MODERN CARD COMPONENT
# ============================================================================

class ModernCard(ttk.Frame):
    """
    Modern card container with optional header, footer, and elevation
    
    Usage:
        card = ModernCard(parent, title="Card Title")
        content = card.get_content_frame()
        # Add widgets to content frame
    """
    
    def __init__(self, parent, title=None, subtitle=None, padding=Spacing.PADDING_CARD, 
                 has_header=True, has_footer=False, theme=None, **kwargs):
        super().__init__(parent, style='Card.TFrame', padding=padding, **kwargs)
        
        self.theme = theme or ModernTheme('light')
        self._create_card(title, subtitle, has_header, has_footer)
    
    def _create_card(self, title, subtitle, has_header, has_footer):
        """Create card structure"""
        
        # Header
        if has_header and title:
            header_frame = ttk.Frame(self, style='Card.TFrame')
            header_frame.pack(fill=tk.X, pady=(0, Spacing.SM))
            
            title_label = ttk.Label(header_frame, text=title, style='H4.TLabel')
            title_label.pack(side=tk.LEFT)
            
            if subtitle:
                subtitle_label = ttk.Label(header_frame, text=subtitle, 
                                          style='BodySecondary.TLabel')
                subtitle_label.pack(side=tk.LEFT, padx=(Spacing.SM, 0))
            
            # Separator
            separator = ttk.Separator(self, orient='horizontal')
            separator.pack(fill=tk.X, pady=(0, Spacing.SM))
        
        # Content frame
        self.content_frame = ttk.Frame(self, style='Card.TFrame')
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Footer
        if has_footer:
            separator = ttk.Separator(self, orient='horizontal')
            separator.pack(fill=tk.X, pady=(Spacing.SM, 0))
            
            self.footer_frame = ttk.Frame(self, style='Card.TFrame')
            self.footer_frame.pack(fill=tk.X, pady=(Spacing.SM, 0))
    
    def get_content_frame(self):
        """Get the content frame to add widgets"""
        return self.content_frame
    
    def get_footer_frame(self):
        """Get the footer frame"""
        return getattr(self, 'footer_frame', None)


# ============================================================================
# MODERN BUTTON VARIANTS
# ============================================================================

class ModernButton:
    """Factory class for creating modern buttons"""
    
    @staticmethod
    def primary(parent, text, command=None, icon=None, width=None, **kwargs):
        """Create primary button"""
        full_text = f"{icon} {text}" if icon else text
        btn = ttk.Button(parent, text=full_text, command=command, 
                        style='Primary.TButton', width=width, **kwargs)
        return btn
    
    @staticmethod
    def secondary(parent, text, command=None, icon=None, width=None, **kwargs):
        """Create secondary button"""
        full_text = f"{icon} {text}" if icon else text
        btn = ttk.Button(parent, text=full_text, command=command,
                        style='Secondary.TButton', width=width, **kwargs)
        return btn
    
    @staticmethod
    def success(parent, text, command=None, icon=None, width=None, **kwargs):
        """Create success button"""
        full_text = f"{icon} {text}" if icon else text
        btn = ttk.Button(parent, text=full_text, command=command,
                        style='Success.TButton', width=width, **kwargs)
        return btn
    
    @staticmethod
    def error(parent, text, command=None, icon=None, width=None, **kwargs):
        """Create error/danger button"""
        full_text = f"{icon} {text}" if icon else text
        btn = ttk.Button(parent, text=full_text, command=command,
                        style='Error.TButton', width=width, **kwargs)
        return btn
    
    @staticmethod
    def icon(parent, icon, command=None, tooltip=None, **kwargs):
        """Create icon-only button"""
        btn = ttk.Button(parent, text=icon, command=command,
                        style='Icon.TButton', width=3, **kwargs)
        if tooltip:
            ModernTooltip.create(btn, tooltip)
        return btn
    
    @staticmethod
    def link(parent, text, command=None, **kwargs):
        """Create link-style button"""
        btn = tk.Label(parent, text=text, fg=LightTheme.PRIMARY,
                      cursor='hand2', font=(Typography.FONT_PRIMARY, Typography.SIZE_BODY),
                      bg=LightTheme.BG_PRIMARY, **kwargs)
        if command:
            btn.bind('<Button-1>', lambda e: command())
        
        # Hover effect
        def on_enter(e):
            btn.config(fg=LightTheme.PRIMARY_HOVER, font=(Typography.FONT_PRIMARY, 
                      Typography.SIZE_BODY, 'underline'))
        
        def on_leave(e):
            btn.config(fg=LightTheme.PRIMARY, font=(Typography.FONT_PRIMARY, 
                      Typography.SIZE_BODY))
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn


# ============================================================================
# MODERN INPUT FIELDS
# ============================================================================

class ModernInput(ttk.Frame):
    """
    Enhanced input field with label, placeholder, and validation
    
    Usage:
        input_field = ModernInput(parent, label="Name", placeholder="Enter name")
        value = input_field.get()
    """
    
    def __init__(self, parent, label=None, placeholder=None, input_type='text',
                 width=None, required=False, theme=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.theme = theme or ModernTheme('light')
        self.required = required
        self.input_type = input_type
        
        self._create_input(label, placeholder, width)
    
    def _create_input(self, label, placeholder, width):
        """Create input structure"""
        
        # Label
        if label:
            label_frame = ttk.Frame(self)
            label_frame.pack(fill=tk.X, pady=(0, Spacing.XS))
            
            label_text = f"{label} *" if self.required else label
            lbl = ttk.Label(label_frame, text=label_text, style='Body.TLabel')
            lbl.pack(side=tk.LEFT)
        
        # Input field
        if self.input_type == 'text':
            self.input_var = tk.StringVar()
            self.entry = ttk.Entry(self, textvariable=self.input_var, width=width)
            self.entry.pack(fill=tk.X)
            
            # Placeholder effect
            if placeholder:
                self._setup_placeholder(placeholder)
        
        elif self.input_type == 'textarea':
            self.entry = tk.Text(self, height=5, width=width or 40,
                                font=(Typography.FONT_PRIMARY, Typography.SIZE_BODY),
                                bg=LightTheme.INPUT_BG, fg=LightTheme.INPUT_TEXT,
                                relief='solid', borderwidth=1)
            self.entry.pack(fill=tk.BOTH, expand=True)
        
        elif self.input_type == 'password':
            self.input_var = tk.StringVar()
            self.entry = ttk.Entry(self, textvariable=self.input_var, 
                                  show='•', width=width)
            self.entry.pack(fill=tk.X)
    
    def _setup_placeholder(self, placeholder):
        """Setup placeholder text effect"""
        self.placeholder = placeholder
        
        def on_focus_in(event):
            if self.input_var.get() == self.placeholder:
                self.input_var.set('')
                self.entry.config(foreground=LightTheme.INPUT_TEXT)
        
        def on_focus_out(event):
            if not self.input_var.get():
                self.input_var.set(self.placeholder)
                self.entry.config(foreground=LightTheme.INPUT_PLACEHOLDER)
        
        self.input_var.set(self.placeholder)
        self.entry.config(foreground=LightTheme.INPUT_PLACEHOLDER)
        self.entry.bind('<FocusIn>', on_focus_in)
        self.entry.bind('<FocusOut>', on_focus_out)
    
    def get(self):
        """Get input value"""
        if self.input_type == 'textarea':
            return self.entry.get('1.0', tk.END).strip()
        else:
            value = self.input_var.get()
            return value if value != getattr(self, 'placeholder', '') else ''
    
    def set(self, value):
        """Set input value"""
        if self.input_type == 'textarea':
            self.entry.delete('1.0', tk.END)
            self.entry.insert('1.0', value)
        else:
            self.input_var.set(value)
    
    def clear(self):
        """Clear input"""
        if self.input_type == 'textarea':
            self.entry.delete('1.0', tk.END)
        else:
            self.input_var.set('')


# ============================================================================
# MODERN BADGE COMPONENT
# ============================================================================

class ModernBadge(tk.Label):
    """
    Status badge component
    
    Usage:
        badge = ModernBadge(parent, text="Active", variant="success")
    """
    
    VARIANTS = {
        'default': (LightTheme.TEXT_SECONDARY, ColorPalette.NEUTRAL['gray_200']),
        'primary': (LightTheme.TEXT_INVERSE, LightTheme.PRIMARY),
        'success': (LightTheme.TEXT_INVERSE, LightTheme.SUCCESS),
        'error': (LightTheme.TEXT_INVERSE, LightTheme.ERROR),
        'warning': (ColorPalette.TEXT['primary'], LightTheme.WARNING),
        'info': (LightTheme.TEXT_INVERSE, LightTheme.INFO),
    }
    
    def __init__(self, parent, text='', variant='default', **kwargs):
        fg, bg = self.VARIANTS.get(variant, self.VARIANTS['default'])
        
        super().__init__(parent, text=text, fg=fg, bg=bg,
                        font=(Typography.FONT_PRIMARY, Typography.SIZE_CAPTION, 'bold'),
                        padx=Spacing.SM, pady=Spacing.XS,
                        relief='flat', **kwargs)
    
    def set_variant(self, variant):
        """Change badge variant"""
        fg, bg = self.VARIANTS.get(variant, self.VARIANTS['default'])
        self.config(fg=fg, bg=bg)


# ============================================================================
# MODERN ALERT COMPONENT
# ============================================================================

class ModernAlert(ttk.Frame):
    """
    Alert/notification box
    
    Usage:
        alert = ModernAlert(parent, message="Success!", variant="success", dismissible=True)
    """
    
    VARIANTS = {
        'info': {
            'bg': ColorPalette.SEMANTIC['info_bg'],
            'fg': ColorPalette.SEMANTIC['info_dark'],
            'icon': 'ℹ️'
        },
        'success': {
            'bg': ColorPalette.SEMANTIC['success_bg'],
            'fg': ColorPalette.SEMANTIC['success_dark'],
            'icon': '✅'
        },
        'warning': {
            'bg': ColorPalette.SEMANTIC['warning_bg'],
            'fg': ColorPalette.SEMANTIC['warning_dark'],
            'icon': '⚠️'
        },
        'error': {
            'bg': ColorPalette.SEMANTIC['error_bg'],
            'fg': ColorPalette.SEMANTIC['error_dark'],
            'icon': '❌'
        }
    }
    
    def __init__(self, parent, message='', variant='info', dismissible=False, 
                 title=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.variant_config = self.VARIANTS.get(variant, self.VARIANTS['info'])
        self.configure(style='Card.TFrame')
        self.config(relief='solid', borderwidth=1)
        
        self._create_alert(message, title, dismissible)
    
    def _create_alert(self, message, title, dismissible):
        """Create alert structure"""
        
        # Background color
        inner_frame = tk.Frame(self, bg=self.variant_config['bg'], 
                              padx=Spacing.MD, pady=Spacing.SM)
        inner_frame.pack(fill=tk.BOTH, expand=True)
        
        # Icon
        icon_label = tk.Label(inner_frame, text=self.variant_config['icon'],
                             font=(Typography.FONT_PRIMARY, Typography.SIZE_H5),
                             bg=self.variant_config['bg'], fg=self.variant_config['fg'])
        icon_label.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        # Content
        content_frame = tk.Frame(inner_frame, bg=self.variant_config['bg'])
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        if title:
            title_label = tk.Label(content_frame, text=title,
                                  font=(Typography.FONT_PRIMARY, Typography.SIZE_BODY, 'bold'),
                                  bg=self.variant_config['bg'], fg=self.variant_config['fg'])
            title_label.pack(anchor='w')
        
        message_label = tk.Label(content_frame, text=message, wraplength=400,
                                font=(Typography.FONT_PRIMARY, Typography.SIZE_BODY),
                                bg=self.variant_config['bg'], fg=self.variant_config['fg'],
                                justify=tk.LEFT)
        message_label.pack(anchor='w')
        
        # Dismiss button
        if dismissible:
            dismiss_btn = tk.Label(inner_frame, text='✕', cursor='hand2',
                                  font=(Typography.FONT_PRIMARY, Typography.SIZE_BODY, 'bold'),
                                  bg=self.variant_config['bg'], fg=self.variant_config['fg'])
            dismiss_btn.pack(side=tk.RIGHT)
            dismiss_btn.bind('<Button-1>', lambda e: self.destroy())
    
    def dismiss(self):
        """Dismiss the alert"""
        self.destroy()


# ============================================================================
# MODERN TOOLTIP
# ============================================================================

class ModernTooltip:
    """
    Enhanced tooltip with modern styling
    
    Usage:
        ModernTooltip.create(widget, "Tooltip text")
    """
    
    @staticmethod
    def create(widget, text, delay=500):
        """Create tooltip for widget"""
        tooltip = None
        tooltip_after_id = None
        
        def show_tooltip(event):
            nonlocal tooltip, tooltip_after_id
            
            def _show():
                nonlocal tooltip
                x = widget.winfo_rootx() + 20
                y = widget.winfo_rooty() + widget.winfo_height() + 5
                
                tooltip = tk.Toplevel(widget)
                tooltip.wm_overrideredirect(True)
                tooltip.wm_geometry(f"+{x}+{y}")
                
                # Styling
                frame = tk.Frame(tooltip, bg=ColorPalette.NEUTRAL['gray_800'],
                               relief='solid', borderwidth=1)
                frame.pack()
                
                label = tk.Label(frame, text=text,
                               bg=ColorPalette.NEUTRAL['gray_800'],
                               fg=ColorPalette.NEUTRAL['white'],
                               font=(Typography.FONT_PRIMARY, Typography.SIZE_CAPTION),
                               padx=Spacing.SM, pady=Spacing.XS)
                label.pack()
            
            tooltip_after_id = widget.after(delay, _show)
        
        def hide_tooltip(event):
            nonlocal tooltip, tooltip_after_id
            
            if tooltip_after_id:
                widget.after_cancel(tooltip_after_id)
                tooltip_after_id = None
            
            if tooltip:
                tooltip.destroy()
                tooltip = None
        
        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)


# ============================================================================
# MODERN PROGRESS CARD
# ============================================================================

class ModernProgressCard(ttk.Frame):
    """
    Progress indicator with title, percentage, and status message
    
    Usage:
        progress = ModernProgressCard(parent, title="Uploading files")
        progress.update_progress(50, "Uploading file 5/10")
    """
    
    def __init__(self, parent, title='', theme=None, **kwargs):
        super().__init__(parent, style='Card.TFrame', padding=Spacing.MD, **kwargs)
        
        self.theme = theme or ModernTheme('light')
        self._create_progress_card(title)
    
    def _create_progress_card(self, title):
        """Create progress card structure"""
        
        # Title
        self.title_label = ttk.Label(self, text=title, style='Body.TLabel',
                                     font=(Typography.FONT_PRIMARY, Typography.SIZE_BODY, 'bold'))
        self.title_label.pack(fill=tk.X, pady=(0, Spacing.SM))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(self, mode='determinate', length=300)
        self.progress_bar.pack(fill=tk.X, pady=(0, Spacing.SM))
        
        # Status row (percentage + message)
        status_frame = ttk.Frame(self, style='Card.TFrame')
        status_frame.pack(fill=tk.X)
        
        self.percentage_label = ttk.Label(status_frame, text='0%', style='BodySecondary.TLabel',
                                         font=(Typography.FONT_PRIMARY, Typography.SIZE_BODY, 'bold'))
        self.percentage_label.pack(side=tk.LEFT)
        
        self.status_label = ttk.Label(status_frame, text='Ready', style='BodySecondary.TLabel')
        self.status_label.pack(side=tk.LEFT, padx=(Spacing.SM, 0))
    
    def update_progress(self, percentage, status_message=''):
        """Update progress"""
        self.progress_bar['value'] = percentage
        self.percentage_label.config(text=f'{int(percentage)}%')
        if status_message:
            self.status_label.config(text=status_message)
    
    def set_complete(self, message='Complete'):
        """Set to complete state"""
        self.progress_bar['value'] = 100
        self.percentage_label.config(text='100%')
        self.status_label.config(text=message)
        # Change to success color
        self.progress_bar.config(style='Success.TProgressbar')
    
    def set_error(self, message='Error'):
        """Set to error state"""
        self.status_label.config(text=message)
        # Change to error color
        self.progress_bar.config(style='Error.TProgressbar')


# ============================================================================
# MODERN SECTION HEADER
# ============================================================================

class ModernSectionHeader(ttk.Frame):
    """
    Section header with title, subtitle, and optional action button
    
    Usage:
        header = ModernSectionHeader(parent, title="Settings", subtitle="Configure your app")
    """
    
    def __init__(self, parent, title='', subtitle='', action_text=None, 
                 action_command=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self._create_header(title, subtitle, action_text, action_command)
    
    def _create_header(self, title, subtitle, action_text, action_command):
        """Create header structure"""
        
        # Left side: title + subtitle
        left_frame = ttk.Frame(self)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(left_frame, text=title, style='H3.TLabel')
        title_label.pack(anchor='w')
        
        if subtitle:
            subtitle_label = ttk.Label(left_frame, text=subtitle, style='BodySecondary.TLabel')
            subtitle_label.pack(anchor='w', pady=(Spacing.XS, 0))
        
        # Right side: action button
        if action_text and action_command:
            action_btn = ModernButton.secondary(self, action_text, command=action_command)
            action_btn.pack(side=tk.RIGHT)
        
        # Bottom divider
        divider = ttk.Separator(self, orient='horizontal')
        divider.pack(fill=tk.X, pady=(Spacing.SM, 0))


# ============================================================================
# MODERN FILE ITEM CARD
# ============================================================================

class ModernFileItemCard(ttk.Frame):
    """
    File item display card with icon, name, size, and actions
    
    Usage:
        file_card = ModernFileItemCard(parent, filename="data.csv", size="1.2 MB")
    """
    
    FILE_ICONS = {
        '.py': '🐍',
        '.csv': '📊',
        '.json': '📄',
        '.txt': '📝',
        '.zip': '📦',
        '.pdf': '📕',
        'default': '📁'
    }
    
    def __init__(self, parent, filename='', size='', status='pending', 
                 on_remove=None, **kwargs):
        super().__init__(parent, style='Card.TFrame', padding=Spacing.SM, **kwargs)
        
        self._create_file_card(filename, size, status, on_remove)
    
    def _create_file_card(self, filename, size, status, on_remove):
        """Create file card structure"""
        
        # Icon
        ext = '.' + filename.split('.')[-1] if '.' in filename else ''
        icon = self.FILE_ICONS.get(ext, self.FILE_ICONS['default'])
        
        icon_label = ttk.Label(self, text=icon, 
                              font=(Typography.FONT_PRIMARY, Typography.SIZE_H4))
        icon_label.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        
        # File info
        info_frame = ttk.Frame(self, style='Card.TFrame')
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        name_label = ttk.Label(info_frame, text=filename, style='Body.TLabel',
                              font=(Typography.FONT_PRIMARY, Typography.SIZE_BODY, 'bold'))
        name_label.pack(anchor='w')
        
        size_label = ttk.Label(info_frame, text=size, style='Caption.TLabel')
        size_label.pack(anchor='w')
        
        # Status badge
        status_variants = {
            'pending': 'default',
            'uploading': 'info',
            'completed': 'success',
            'error': 'error'
        }
        
        self.status_badge = ModernBadge(self, text=status.capitalize(),
                                       variant=status_variants.get(status, 'default'))
        self.status_badge.pack(side=tk.RIGHT, padx=(Spacing.SM, 0))
        
        # Remove button
        if on_remove:
            remove_btn = ModernButton.icon(self, '✕', command=on_remove, 
                                          tooltip='Remove file')
            remove_btn.pack(side=tk.RIGHT)
    
    def update_status(self, status):
        """Update file status"""
        status_variants = {
            'pending': 'default',
            'uploading': 'info',
            'completed': 'success',
            'error': 'error'
        }
        
        self.status_badge.config(text=status.capitalize())
        self.status_badge.set_variant(status_variants.get(status, 'default'))


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    'ModernCard',
    'ModernButton',
    'ModernInput',
    'ModernBadge',
    'ModernAlert',
    'ModernTooltip',
    'ModernProgressCard',
    'ModernSectionHeader',
    'ModernFileItemCard',
]
