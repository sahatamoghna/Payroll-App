import os, sys, datetime, configparser, tkinter as tk
from tkinter import messagebox

# Directories 
# Where bundled resources live (templates, fonts, config)
if getattr(sys, 'frozen', False):
    RESOURCE_DIR = sys._MEIPASS
else:
    RESOURCE_DIR = os.path.dirname(os.path.abspath(__file__))

if getattr(sys, 'frozen', False):
    APP_DATA_DIR = os.path.join(os.getenv('LOCALAPPDATA'), "PayrollApp")
else:
    APP_DATA_DIR = RESOURCE_DIR

os.makedirs(APP_DATA_DIR, exist_ok=True)

# Load Configuration 
CONFIG_FILE = os.path.join(RESOURCE_DIR, 'config.ini')
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

# DB file and reports folder name
DB_FILENAME    = config['DEFAULT'].get('DB_FILENAME', 'payroll.db')
REPORTS_FOLDER = config['DEFAULT'].get('REPORTS_FOLDER', 'reports')

USERNAME = config['DEFAULT'].get('USERNAME', 'admin')
PASSWORD = config['DEFAULT'].get('PASSWORD', 'password123')
ICON_PATH = config['DEFAULT'].get('ICON_PATH', None)

# Path Helpers
def get_db_path():
    """Return the full path to the SQLite database file in APP_DATA_DIR."""
    return os.path.join(APP_DATA_DIR, DB_FILENAME)

def get_reports_folder_path():
    """Ensure the reports folder exists in APP_DATA_DIR, then return it."""
    folder = os.path.join(APP_DATA_DIR, REPORTS_FOLDER)
    os.makedirs(folder, exist_ok=True)
    return folder

# Timestamp / Formatting
def format_timestamp():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Dialog Helpers
def show_error(message, title='Error'):
    root = tk.Tk(); root.withdraw()
    messagebox.showerror(title, message)
    root.destroy()

def show_info(message, title='Info'):
    root = tk.Tk(); root.withdraw()
    messagebox.showinfo(title, message)
    root.destroy()
