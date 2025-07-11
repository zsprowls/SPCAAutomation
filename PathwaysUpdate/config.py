"""
Configuration settings for the Pathways for Care Viewer application.
"""

# PetPoint Login Credentials
PETPOINT_CONFIG = {
    'shelter_id': 'USNY9',
    'username': 'zaks',
    'password': 'Gillian666!'
}

# Application Settings
APP_CONFIG = {
    'host': '0.0.0.0',
    'port': 8050,
    'debug': False,
    'title': 'Pathways for Care Viewer'
}

# Image Settings
IMAGE_CONFIG = {
    'max_images_per_animal': 3,
    'image_cache_size': 100,
    'image_timeout': 30,  # seconds
    'headless_browser': True  # Set to True for faster processing, False to see browser
}

# Data Settings
DATA_CONFIG = {
    'csv_path': '../__Load Files Go Here__/Pathways for Care.csv',
    'page_size': 20,  # Number of records per page in spreadsheet view
    'max_display_length': 100  # Maximum characters to display in table cells
}

# UI Settings
UI_CONFIG = {
    'table_height': '70vh',
    'row_height': '80px',
    'max_row_height': '120px',
    'welfare_notes_width': '400px',
    'image_size': '200px'
} 