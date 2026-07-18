import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "reception.db"

# Printer Settings
PRINTER_NAME = "BIXOLON SLP-T403" # Update with the actual printer name in Windows
LABEL_WIDTH = 3180
LABEL_HEIGHT = 300
# Shift offset in pixels to adjust the position of the 8 cm printed area.
# Default was -378. Set to -250 to shift the print area slightly "upper" (towards the top of the wristband tape).
WRISTBAND_SHIFT_OFFSET = -200

# Mokeb Details
MOKEB_NAME = "موكب جزیره امید"
AMOOD_NUMBER = "عمود 309"
CONTACT_PHONE = "۰۹۱۲۳۴۵۶۷۸۹"

# Font Settings
FONT_PATH = BASE_DIR / "assets" / "Vazirmatn-Regular.ttf"
FONT_SIZE_TITLE = 70
FONT_SIZE_BODY = 50
