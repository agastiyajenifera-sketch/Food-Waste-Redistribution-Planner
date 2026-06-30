import os

# Base directory of the application
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Database configuration
DB_PATH = os.path.join(BASE_DIR, 'database.db')

# Assets directories
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
ICONS_DIR = os.path.join(ASSETS_DIR, 'icons')
IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')

# Ensure assets directories exist
os.makedirs(ICONS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

# UI Theme Config
DEFAULT_THEME = "dark"
COLOR_THEME = "blue"
WINDOW_TITLE = "Food Waste Redistribution Planner"
WINDOW_SIZE = "1100x680"

# --- Premium Design Tokens ---
# Font Family (Century Gothic provides a modern, geometric appearance)
FONT_FAMILY = "Century Gothic"

# Unique Colorful Palette
# (light_mode_color, dark_mode_color) or single values
THEME_COLORS = {
    # Buttons & Accents
    "primary": ("#ff6b6b", "#ee5253"),      # Vibrant Coral/Rose
    "secondary": ("#10b981", "#059669"),    # Vibrant Emerald Green
    "accent": ("#8b5cf6", "#7c3aed"),       # Vibrant Purple/Violet
    "info": ("#3b82f6", "#2563eb"),         # Vibrant Blue
    "warning": ("#f59e0b", "#d97706"),      # Vibrant Amber/Orange
    
    # Backgrounds
    "bg_light": "#f1f5f9",                  # Light Slate
    "bg_dark": "#0a0f1d",                   # Deep Dark Space Blue
    
    # Sidebars
    "sidebar_light": "#e2e8f0",             # Soft gray-blue
    "sidebar_dark": "#111827",              # Sleek dark gray
    
    # Stats Cards (Light Bg, Dark Bg, Accent Border)
    "card_donors": ("#e0f2fe", "#075985", "#0284c7"),    # Sky Blue Card
    "card_ngos": ("#faf5ff", "#581c87", "#7c3aed"),      # Purple Card
    "card_active": ("#d1fae5", "#064e3b", "#059669"),    # Emerald Card
    "card_rescued": ("#ffe4e6", "#9f1239", "#e11d48"),   # Coral/Pink Card
}

# Category list for donations
FOOD_CATEGORIES = [
    "Cooked Food",
    "Packaged Food",
    "Fresh Produce",
    "Bakery Items",
    "Dairy Products",
    "Beverages",
    "Canned Goods"
]

# Standard food units
FOOD_UNITS = ["kg", "g", "pieces", "packets", "liters", "servings"]
