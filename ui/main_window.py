from PyQt6.QtWidgets import QMainWindow, QTabWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import sys
from pathlib import Path
from config.settings import BASE_DIR
from ui.tabs.session_tab import SessionTab
from ui.tabs.registration_tab import RegistrationTab
from ui.tabs.data_tab import DataTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نرم‌افزار مدیریت پذیرش و ثبت‌نام")
        self.setMinimumSize(1000, 700)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # Load and set application window icon
        possible_logo_paths = [
            BASE_DIR / "assets" / "لوگوی جزیره امید.jpg",
            Path(sys.executable).parent / "لوگوی جزیره امید.jpg" if getattr(sys, 'frozen', False) else None,
            BASE_DIR.parent / "لوگوی جزیره امید.jpg",
        ]
        logo_path = None
        for path in possible_logo_paths:
            if path and path.exists():
                logo_path = path
                break
        if logo_path:
            self.setWindowIcon(QIcon(str(logo_path)))
        
        self.tabs = QTabWidget()
        
        self.registration_tab = RegistrationTab()
        self.session_tab = SessionTab()
        self.data_tab = DataTab()
        
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        self.tabs.addTab(self.registration_tab, "ثبت نام")
        self.tabs.addTab(self.session_tab, "مدیریت سانس‌ها")
        self.tabs.addTab(self.data_tab, "گزارشات و اطلاعات")
        
        self.setCentralWidget(self.tabs)
        
    def on_tab_changed(self, index):
        if index == 1:
            self.session_tab.load_data()
        elif index == 2:
            self.data_tab.refresh_filters()
