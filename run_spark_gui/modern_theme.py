"""
Modern Design System for Spark Runner GUI
Inspired by Fluent Design (Microsoft), Notion, and Material Design
Version: 4.0.0

This module provides a comprehensive design system including:
- Professional color palette with semantic meanings
- Typography hierarchy system  
- Spacing and layout system
- Modern component styles
- Light and Dark mode support
"""

import tkinter as tk
from tkinter import ttk

# ============================================================================
# COLOR SYSTEM - Fluent Design Inspired
# ============================================================================

class ColorPalette:
    """Modern color palette with semantic meanings"""
    
    # === NEUTRAL COLORS (Base) ===
    NEUTRAL = {
        'white': '#FFFFFF',
        'gray_50': '#FAFAFA',
        'gray_100': '#F5F5F5',
        'gray_200': '#EEEEEE',
        'gray_300': '#E0E0E0',
        'gray_400': '#BDBDBD',
        'gray_500': '#9E9E9E',
        'gray_600': '#757575',
        'gray_700': '#616161',
        'gray_800': '#424242',
        'gray_900': '#212121',
        'black': '#000000',
    }
    
    # === PRIMARY COLORS (Brand - Indigo) ===
    PRIMARY = {
        'lightest': '#E8EAF6',
        'lighter': '#C5CAE9',
        'light': '#9FA8DA',
        'base': '#5C6BC0',      # Main brand color
        'dark': '#3949AB',
        'darker': '#283593',
        'darkest': '#1A237E',
    }
    
    # === ACCENT COLORS ===
    ACCENT = {
        'blue': '#2196F3',      # Information
        'purple': '#9C27B0',    # Creative
        'teal': '#009688',      # Success alternative
        'cyan': '#00BCD4',      # Highlight
        'pink': '#E91E63',      # Warning alternative
    }
    
    # === SEMANTIC COLORS ===
    SEMANTIC = {
        'success': '#4CAF50',
        'success_light': '#81C784',
        'success_dark': '#388E3C',
        'success_bg': '#E8F5E9',
        
        'error': '#F44336',
        'error_light': '#E57373',
        'error_dark': '#D32F2F',
        'error_bg': '#FFEBEE',
        
        'warning': '#FF9800',
        'warning_light': '#FFB74D',
        'warning_dark': '#F57C00',
        'warning_bg': '#FFF3E0',
        
        'info': '#2196F3',
        'info_light': '#64B5F6',
        'info_dark': '#1976D2',
        'info_bg': '#E3F2FD',
    }
    
    # === SURFACE & ELEVATION ===
    SURFACE = {
        'background': '#FAFAFA',        # Main app background
        'surface_0': '#FFFFFF',          # Base surface (cards)
        'surface_1': '#FFFFFF',          # Elevated surface
        'surface_2': '#FFFFFF',          # Higher elevated
        'overlay': 'rgba(0, 0, 0, 0.5)', # Modal overlay
        'border': '#E0E0E0',            # Default borders
        'border_focus': '#5C6BC0',      # Focus state
        'divider': '#E0E0E0',           # Section dividers
    }
    
    # === TEXT COLORS ===
    TEXT = {
        'primary': '#212121',           # Main text
        'secondary': '#757575',         # Secondary text
        'tertiary': '#9E9E9E',         # Tertiary/disabled text
        'inverse': '#FFFFFF',           # Text on dark backgrounds
        'link': '#2196F3',             # Hyperlinks
        'link_hover': '#1976D2',        # Link hover state
    }
    
    # === DARK MODE ===
    DARK = {
        'background': '#121212',
        'surface_0': '#1E1E1E',
        'surface_1': '#2D2D2D',
        'surface_2': '#3D3D3D',
        'border': '#3D3D3D',
        'divider': '#3D3D3D',
        'text_primary': '#FFFFFF',
        'text_secondary': '#B3B3B3',
        'text_tertiary': '#808080',
    }


class LightTheme:
    """Light mode theme configuration"""
    
    # Background colors
    BG_PRIMARY = ColorPalette.NEUTRAL['gray_50']
    BG_SECONDARY = ColorPalette.NEUTRAL['white']
    BG_TERTIARY = ColorPalette.NEUTRAL['gray_100']
    
    # Surface colors
    SURFACE = ColorPalette.NEUTRAL['white']
    SURFACE_ELEVATED = ColorPalette.NEUTRAL['white']
    
    # Text colors
    TEXT_PRIMARY = ColorPalette.TEXT['primary']
    TEXT_SECONDARY = ColorPalette.TEXT['secondary']
    TEXT_TERTIARY = ColorPalette.TEXT['tertiary']
    TEXT_INVERSE = ColorPalette.TEXT['inverse']
    
    # Border colors
    BORDER = ColorPalette.SURFACE['border']
    BORDER_FOCUS = ColorPalette.SURFACE['border_focus']
    DIVIDER = ColorPalette.SURFACE['divider']
    
    # Brand colors
    PRIMARY = ColorPalette.PRIMARY['base']
    PRIMARY_HOVER = ColorPalette.PRIMARY['dark']
    PRIMARY_ACTIVE = ColorPalette.PRIMARY['darker']
    PRIMARY_LIGHT = ColorPalette.PRIMARY['lightest']
    
    # Semantic colors
    SUCCESS = ColorPalette.SEMANTIC['success']
    ERROR = ColorPalette.SEMANTIC['error']
    WARNING = ColorPalette.SEMANTIC['warning']
    INFO = ColorPalette.SEMANTIC['info']
    
    # Component specific
    BUTTON_PRIMARY = ColorPalette.PRIMARY['base']
    BUTTON_PRIMARY_HOVER = ColorPalette.PRIMARY['dark']
    BUTTON_PRIMARY_TEXT = ColorPalette.TEXT['inverse']
    
    BUTTON_SECONDARY = ColorPalette.NEUTRAL['gray_200']
    BUTTON_SECONDARY_HOVER = ColorPalette.NEUTRAL['gray_300']
    BUTTON_SECONDARY_TEXT = ColorPalette.TEXT['primary']
    
    INPUT_BG = ColorPalette.NEUTRAL['white']
    INPUT_BORDER = ColorPalette.NEUTRAL['gray_300']
    INPUT_BORDER_FOCUS = ColorPalette.PRIMARY['base']
    INPUT_TEXT = ColorPalette.TEXT['primary']
    INPUT_PLACEHOLDER = ColorPalette.TEXT['tertiary']
    
    # Shadows (for elevation effect)
    SHADOW_SM = '#00000015'
    SHADOW_MD = '#00000025'
    SHADOW_LG = '#00000035'


class DarkTheme:
    """Dark mode theme configuration"""
    
    # Background colors
    BG_PRIMARY = ColorPalette.DARK['background']
    BG_SECONDARY = ColorPalette.DARK['surface_0']
    BG_TERTIARY = ColorPalette.DARK['surface_1']
    
    # Surface colors
    SURFACE = ColorPalette.DARK['surface_0']
    SURFACE_ELEVATED = ColorPalette.DARK['surface_1']
    
    # Text colors
    TEXT_PRIMARY = ColorPalette.DARK['text_primary']
    TEXT_SECONDARY = ColorPalette.DARK['text_secondary']
    TEXT_TERTIARY = ColorPalette.DARK['text_tertiary']
    TEXT_INVERSE = ColorPalette.TEXT['primary']
    
    # Border colors
    BORDER = ColorPalette.DARK['border']
    BORDER_FOCUS = ColorPalette.PRIMARY['light']
    DIVIDER = ColorPalette.DARK['divider']
    
    # Brand colors (slightly adjusted for dark mode)
    PRIMARY = ColorPalette.PRIMARY['light']
    PRIMARY_HOVER = ColorPalette.PRIMARY['base']
    PRIMARY_ACTIVE = ColorPalette.PRIMARY['dark']
    PRIMARY_LIGHT = ColorPalette.PRIMARY['darkest']
    
    # Semantic colors
    SUCCESS = ColorPalette.SEMANTIC['success_light']
    ERROR = ColorPalette.SEMANTIC['error_light']
    WARNING = ColorPalette.SEMANTIC['warning_light']
    INFO = ColorPalette.SEMANTIC['info_light']


# ============================================================================
# TYPOGRAPHY SYSTEM
# ============================================================================

class Typography:
    """Modern typography hierarchy"""
    
    # Font families
    FONT_PRIMARY = 'Segoe UI'
    FONT_SECONDARY = 'Inter, -apple-system, system-ui'
    FONT_MONO = 'Consolas, Monaco, monospace'
    FONT_CODE = 'Fira Code, Consolas, monospace'
    
    # Font sizes (in points for Tkinter)
    SIZE_H1 = 28
    SIZE_H2 = 24
    SIZE_H3 = 20
    SIZE_H4 = 18
    SIZE_H5 = 16
    SIZE_H6 = 14
    SIZE_BODY = 12
    SIZE_BODY_SM = 11
    SIZE_BODY_XS = 10
    SIZE_CAPTION = 10
    SIZE_OVERLINE = 9
    
    # Font weights
    WEIGHT_LIGHT = 'normal'
    WEIGHT_REGULAR = 'normal'
    WEIGHT_MEDIUM = 'normal'
    WEIGHT_BOLD = 'bold'
    
    # Line heights (approximate for Tkinter)
    LINE_HEIGHT_TIGHT = 1.2
    LINE_HEIGHT_NORMAL = 1.5
    LINE_HEIGHT_RELAXED = 1.8
    
    # Letter spacing
    LETTER_SPACING_TIGHT = -0.5
    LETTER_SPACING_NORMAL = 0
    LETTER_SPACING_WIDE = 0.5


# ============================================================================
# SPACING SYSTEM
# ============================================================================

class Spacing:
    """Consistent spacing scale (8px base)"""
    
    XS = 4      # 4px
    SM = 8      # 8px
    MD = 16     # 16px
    LG = 24     # 24px
    XL = 32     # 32px
    XXL = 48    # 48px
    XXXL = 64   # 64px
    
    # Padding presets
    PADDING_CARD = 16
    PADDING_SECTION = 24
    PADDING_CONTAINER = 32
    
    # Margins
    MARGIN_COMPONENT = 12
    MARGIN_SECTION = 20
    
    # Border radius
    RADIUS_SM = 4
    RADIUS_MD = 8
    RADIUS_LG = 12
    RADIUS_XL = 16
    RADIUS_FULL = 9999


# ============================================================================
# MODERN THEME SETUP
# ============================================================================

class ModernTheme:
    """Main theme controller with light/dark mode support"""
    
    def __init__(self, mode='light'):
        self.mode = mode
        self.colors = LightTheme if mode == 'light' else DarkTheme
        self.typography = Typography
        self.spacing = Spacing
        
    def toggle_mode(self):
        """Toggle between light and dark mode"""
        self.mode = 'dark' if self.mode == 'light' else 'light'
        self.colors = LightTheme if self.mode == 'light' else DarkTheme
    
    def get_color(self, color_name):
        """Get color value by name"""
        return getattr(self.colors, color_name.upper(), '#000000')


def setup_modern_theme(root, mode='light'):
    """
    Setup modern theme for Tkinter application
    
    Args:
        root: Tkinter root window
        mode: 'light' or 'dark'
    
    Returns:
        ModernTheme: Theme instance
    """
    theme = ModernTheme(mode)
    style = ttk.Style()
    
    # Try to use 'clam' theme as base for better customization
    try:
        style.theme_use('clam')
    except tk.TclError:
        pass
    
    # Configure root
    root.configure(bg=theme.colors.BG_PRIMARY)
    root.option_add('*Font', (Typography.FONT_PRIMARY, Typography.SIZE_BODY))
    root.option_add('*Foreground', theme.colors.TEXT_PRIMARY)
    root.option_add('*Background', theme.colors.BG_SECONDARY)
    
    # Selection colors
    root.option_add('*selectBackground', theme.colors.PRIMARY)
    root.option_add('*selectForeground', theme.colors.TEXT_INVERSE)
    
    # ========== FRAME STYLES ==========
    style.configure('TFrame',
                   background=theme.colors.BG_PRIMARY,
                   borderwidth=0)
    
    style.configure('Card.TFrame',
                   background=theme.colors.SURFACE,
                   relief='flat',
                   borderwidth=1)
    
    style.configure('Elevated.TFrame',
                   background=theme.colors.SURFACE_ELEVATED,
                   relief='solid',
                   borderwidth=1)
    
    # ========== LABEL STYLES ==========
    style.configure('TLabel',
                   background=theme.colors.BG_PRIMARY,
                   foreground=theme.colors.TEXT_PRIMARY,
                   font=(Typography.FONT_PRIMARY, Typography.SIZE_BODY))
    
    style.configure('H1.TLabel',
                   foreground=theme.colors.TEXT_PRIMARY,
                   font=(Typography.FONT_PRIMARY, Typography.SIZE_H1, Typography.WEIGHT_BOLD))
    
    style.configure('H2.TLabel',
                   foreground=theme.colors.TEXT_PRIMARY,
                   font=(Typography.FONT_PRIMARY, Typography.SIZE_H2, Typography.WEIGHT_BOLD))
    
    style.configure('H3.TLabel',
                   foreground=theme.colors.TEXT_PRIMARY,
                   font=(Typography.FONT_PRIMARY, Typography.SIZE_H3, Typography.WEIGHT_BOLD))
    
    style.configure('H4.TLabel',
                   foreground=theme.colors.TEXT_PRIMARY,
                   font=(Typography.FONT_PRIMARY, Typography.SIZE_H4, Typography.WEIGHT_BOLD))
    
    style.configure('Body.TLabel',
                   foreground=theme.colors.TEXT_PRIMARY,
                   font=(Typography.FONT_PRIMARY, Typography.SIZE_BODY))
    
    style.configure('BodySecondary.TLabel',
                   foreground=theme.colors.TEXT_SECONDARY,
                   font=(Typography.FONT_PRIMARY, Typography.SIZE_BODY))
    
    style.configure('Caption.TLabel',
                   foreground=theme.colors.TEXT_TERTIARY,
                   font=(Typography.FONT_PRIMARY, Typography.SIZE_CAPTION))
    
    style.configure('Code.TLabel',
                   foreground=theme.colors.TEXT_PRIMARY,
                   font=(Typography.FONT_MONO, Typography.SIZE_BODY),
                   background=theme.colors.BG_TERTIARY)
    
    # ========== BUTTON STYLES ==========
    
    # Primary Button
    style.configure('Primary.TButton',
                   background=theme.colors.BUTTON_PRIMARY,
                   foreground=theme.colors.BUTTON_PRIMARY_TEXT,
                   borderwidth=0,
                   relief='flat',
                   padding=(Spacing.MD, Spacing.SM),
                   font=(Typography.FONT_PRIMARY, Typography.SIZE_BODY, Typography.WEIGHT_MEDIUM))
    
    style.map('Primary.TButton',
             background=[('active', theme.colors.BUTTON_PRIMARY_HOVER),
                        ('pressed', theme.colors.PRIMARY_ACTIVE),
                        ('disabled', theme.colors.BORDER)])
    
    # Secondary Button
    style.configure('Secondary.TButton',
                   background=theme.colors.BUTTON_SECONDARY,
                   foreground=theme.colors.BUTTON_SECONDARY_TEXT,
                   borderwidth=1,
                   relief='flat',
                   padding=(Spacing.MD, Spacing.SM),
                   font=(Typography.FONT_PRIMARY, Typography.SIZE_BODY))
    
    style.map('Secondary.TButton',
             background=[('active', theme.colors.BUTTON_SECONDARY_HOVER),
                        ('disabled', theme.colors.BG_TERTIARY)])
    
    # Success Button
    style.configure('Success.TButton',
                   background=theme.colors.SUCCESS,
                   foreground=theme.colors.TEXT_INVERSE,
                   borderwidth=0,
                   relief='flat',
                   padding=(Spacing.MD, Spacing.SM),
                   font=(Typography.FONT_PRIMARY, Typography.SIZE_BODY, Typography.WEIGHT_MEDIUM))
    
    # Error Button
    style.configure('Error.TButton',
                   background=theme.colors.ERROR,
                   foreground=theme.colors.TEXT_INVERSE,
                   borderwidth=0,
                   relief='flat',
                   padding=(Spacing.MD, Spacing.SM),
                   font=(Typography.FONT_PRIMARY, Typography.SIZE_BODY, Typography.WEIGHT_MEDIUM))
    
    # Icon Button (small)
    style.configure('Icon.TButton',
                   background=theme.colors.BG_SECONDARY,
                   foreground=theme.colors.TEXT_PRIMARY,
                   borderwidth=1,
                   relief='flat',
                   padding=(Spacing.SM, Spacing.SM),
                   font=(Typography.FONT_PRIMARY, Typography.SIZE_BODY))
    
    # ========== ENTRY STYLES ==========
    style.configure('TEntry',
                   fieldbackground=theme.colors.INPUT_BG,
                   foreground=theme.colors.INPUT_TEXT,
                   borderwidth=1,
                   relief='solid',
                   insertcolor=theme.colors.TEXT_PRIMARY,
                   padding=Spacing.SM)
    
    style.map('TEntry',
             fieldbackground=[('disabled', theme.colors.BG_TERTIARY)],
             bordercolor=[('focus', theme.colors.INPUT_BORDER_FOCUS),
                         ('!focus', theme.colors.INPUT_BORDER)])
    
    # ========== COMBOBOX STYLES ==========
    style.configure('TCombobox',
                   fieldbackground=theme.colors.INPUT_BG,
                   background=theme.colors.INPUT_BG,
                   foreground=theme.colors.INPUT_TEXT,
                   borderwidth=1,
                   arrowcolor=theme.colors.TEXT_SECONDARY,
                   padding=Spacing.SM)
    
    # ========== LABELFRAME STYLES ==========
    style.configure('TLabelframe',
                   background=theme.colors.SURFACE,
                   foreground=theme.colors.TEXT_PRIMARY,
                   borderwidth=1,
                   relief='solid',
                   padding=Spacing.MD)
    
    style.configure('TLabelframe.Label',
                   background=theme.colors.SURFACE,
                   foreground=theme.colors.PRIMARY,
                   font=(Typography.FONT_PRIMARY, Typography.SIZE_BODY, Typography.WEIGHT_BOLD))
    
    # ========== NOTEBOOK STYLES ==========
    style.configure('TNotebook',
                   background=theme.colors.BG_PRIMARY,
                   borderwidth=0,
                   tabmargins=[0, 0, 0, 0])
    
    style.configure('TNotebook.Tab',
                   background=theme.colors.BG_TERTIARY,
                   foreground=theme.colors.TEXT_SECONDARY,
                   padding=(Spacing.MD, Spacing.SM),
                   borderwidth=0,
                   font=(Typography.FONT_PRIMARY, Typography.SIZE_BODY))
    
    style.map('TNotebook.Tab',
             background=[('selected', theme.colors.SURFACE),
                        ('active', theme.colors.BG_SECONDARY)],
             foreground=[('selected', theme.colors.PRIMARY),
                        ('active', theme.colors.TEXT_PRIMARY)])
    
    # ========== PROGRESSBAR STYLES ==========
    style.configure('TProgressbar',
                   background=theme.colors.PRIMARY,
                   troughcolor=theme.colors.BG_TERTIARY,
                   borderwidth=0,
                   thickness=8)
    
    style.configure('Success.TProgressbar',
                   background=theme.colors.SUCCESS)
    
    style.configure('Error.TProgressbar',
                   background=theme.colors.ERROR)
    
    # ========== TREEVIEW STYLES ==========
    style.configure('Treeview',
                   background=theme.colors.SURFACE,
                   foreground=theme.colors.TEXT_PRIMARY,
                   fieldbackground=theme.colors.SURFACE,
                   borderwidth=1,
                   relief='solid',
                   rowheight=28,
                   font=(Typography.FONT_PRIMARY, Typography.SIZE_BODY))
    
    style.configure('Treeview.Heading',
                   background=theme.colors.BG_TERTIARY,
                   foreground=theme.colors.TEXT_PRIMARY,
                   borderwidth=0,
                   font=(Typography.FONT_PRIMARY, Typography.SIZE_BODY, Typography.WEIGHT_BOLD))
    
    style.map('Treeview',
             background=[('selected', theme.colors.PRIMARY_LIGHT)],
             foreground=[('selected', theme.colors.TEXT_PRIMARY)])
    
    # ========== SEPARATOR STYLES ==========
    style.configure('TSeparator',
                   background=theme.colors.DIVIDER)
    
    # ========== SCROLLBAR STYLES ==========
    style.configure('TScrollbar',
                   background=theme.colors.BG_TERTIARY,
                   troughcolor=theme.colors.BG_PRIMARY,
                   borderwidth=0,
                   arrowcolor=theme.colors.TEXT_SECONDARY)
    
    return theme


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_card_frame(parent, theme, padding=None):
    """Create a modern card-style frame"""
    if padding is None:
        padding = Spacing.PADDING_CARD
    
    frame = ttk.Frame(parent, style='Card.TFrame', padding=padding)
    return frame


def create_section_header(parent, text, theme):
    """Create a section header label"""
    label = ttk.Label(parent, text=text, style='H4.TLabel')
    return label


def create_divider(parent, theme, orient='horizontal'):
    """Create a visual divider"""
    separator = ttk.Separator(parent, orient=orient)
    return separator


# ============================================================================
# EXPORT DEFAULT THEME
# ============================================================================

# Default theme instance for backward compatibility
DEFAULT_THEME = ModernTheme('light')

# Export commonly used values
COLORS = {
    'primary': LightTheme.PRIMARY,
    'success': LightTheme.SUCCESS,
    'error': LightTheme.ERROR,
    'warning': LightTheme.WARNING,
    'info': LightTheme.INFO,
    'bg': LightTheme.BG_PRIMARY,
    'surface': LightTheme.SURFACE,
    'text': LightTheme.TEXT_PRIMARY,
    'text_secondary': LightTheme.TEXT_SECONDARY,
    'border': LightTheme.BORDER,
}

__all__ = [
    'ColorPalette',
    'LightTheme',
    'DarkTheme',
    'Typography',
    'Spacing',
    'ModernTheme',
    'setup_modern_theme',
    'create_card_frame',
    'create_section_header',
    'create_divider',
    'COLORS',
    'DEFAULT_THEME',
]
