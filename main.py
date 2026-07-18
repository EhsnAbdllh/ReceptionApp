import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QFontDatabase
from models.database import init_db
from ui.main_window import MainWindow
from config.settings import FONT_PATH

def main():
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
