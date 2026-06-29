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
DEFAULT_THEME = "dark"  # Can be "dark" or "light"
COLOR_THEME = "blue"    # Options: "blue", "green", "dark-blue"
WINDOW_TITLE = "Food Waste Redistribution Planner"
WINDOW_SIZE = "1100x680"

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
