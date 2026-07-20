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
    
    # Find the font file using multiple fallback paths
    possible_font_paths = [
        FONT_PATH,
        BASE_DIR / "assets" / "Vazirmatn-Regular.ttf",
        Path(sys.argv[0]).parent / "assets" / "Vazirmatn-Regular.ttf",
        Path(sys.executable).parent / "assets" / "Vazirmatn-Regular.ttf" if getattr(sys, 'frozen', False) else None,
        Path(sys.executable).parent / "_internal" / "assets" / "Vazirmatn-Regular.ttf" if getattr(sys, 'frozen', False) else None,
    ]
    
    font_path = None
    for p in possible_font_paths:
        if p and p.exists():
            font_path = p
            break

    font_id = -1
    if font_path:
        font_id = QFontDatabase.addApplicationFont(str(font_path))

    if font_id != -1:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QFont(font_family, 12)
    else:
        # Fall back to high-quality system Persian fonts if the asset is missing
        print("Warning: Vazirmatn font not found, falling back to Segoe UI / Tahoma.")
        font = QFont("Segoe UI", 12)
        font.setFamilies(["Segoe UI", "Tahoma", "Arial"])

    # Force the OS rendering engine to antialias (smooth) the text (crucial for older Windows systems)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(font)
        
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
