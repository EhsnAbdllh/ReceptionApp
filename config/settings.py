import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "reception.db"

# Printer Settings
PRINTER_NAME = "BIXOLON SLP-T403" # Update with the actual printer name in Windows
LABEL_WIDTH = 3195
LABEL_HEIGHT = 300

# Mokeb Details
MOKEB_NAME = "موكب جزیره امید"
AMOOD_NUMBER = "عمود 309"
CONTACT_PHONE = "۰۹۱۲۳۴۵۶۷۸۹"

# Font Settings
FONT_PATH = BASE_DIR / "assets" / "Vazirmatn-Regular.ttf"
FONT_SIZE_TITLE = 70
FONT_SIZE_BODY = 50
