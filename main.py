import sys
import shutil
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QFontDatabase
from models.database import init_db
from ui.main_window import MainWindow
from config.settings import FONT_PATH, BASE_DIR

def main():
    # Ensure the logo file is copied to the assets folder in dev mode for packaging
    try:
        src_logo = BASE_DIR.parent / "لوگوی جزیره امید.jpg"
        dst_logo = BASE_DIR / "assets" / "لوگوی جزیره امید.jpg"
        if src_logo.exists() and not dst_logo.exists():
            shutil.copy(src_logo, dst_logo)
    except Exception as e:
        print(f"Warning: Could not auto-copy logo to assets: {e}")

    init_db()
    
    app = QApplication(sys.argv)
    
    font_id = QFontDatabase.addApplicationFont(str(FONT_PATH))
    if font_id != -1:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        app.setFont(QFont(font_family, 12))
    else:
        print("Warning: Vazirmatn font not found, falling back to default.")
        
    app.setStyleSheet("""
        QLabel, QHeaderView::section {
            font-weight: bold;
        }
        QLineEdit, QComboBox, QSpinBox, QTableWidget {
            font-size: 14px;
        }
        QPushButton {
            padding: 10px 20px;
            font-size: 15px;
            font-weight: bold;
        }
    """)
        
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
