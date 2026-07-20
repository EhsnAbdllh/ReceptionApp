from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox)
from PyQt6.QtCore import Qt, QTimer
from controllers.session_manager import SessionManager
from controllers.registration_manager import RegistrationManager
from models.session import Session

class RegistrationTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        layout = QVBoxLayout()
        
        # Form Layout
        form_layout = QVBoxLayout()
        
        # Session selection
        form_layout.addWidget(QLabel("انتخاب سانس:"))
        self.session_combo = QComboBox()
        self.session_combo.setStyleSheet("padding: 6px; font-size: 14px;")
        self.session_combo.currentIndexChanged.connect(self.on_session_changed)
        form_layout.addWidget(self.session_combo)
        
        # Session remaining capacity info
        self.info_label = QLabel("درحال بررسی ظرفیت...")
        self.info_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 5px; margin-bottom: 15px;")
        form_layout.addWidget(self.info_label)
        
        # Language selection
        form_layout.addWidget(QLabel("زبان چاپ روی دستبند:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("فارسی", "fa")
        self.lang_combo.addItem("عربی", "ar")
        self.lang_combo.setStyleSheet("padding: 6px; font-size: 14px;")
        form_layout.addWidget(self.lang_combo)
        
        form_layout.addWidget(QLabel("نام و نام خانوادگی کودک:"))
        self.name_input = QLineEdit()
        self.name_input.setMaxLength(24)
        self.name_input.setPlaceholderText("نام و نام خانوادگی")
        self.name_input.setStyleSheet("padding: 6px; font-size: 14px;")
        form_layout.addWidget(self.name_input)
        
        form_layout.addWidget(QLabel("شماره موبایل والدین:"))
        self.phone_input = QLineEdit()
        self.phone_input.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.phone_input.setPlaceholderText("شماره موبایل (مثال: 09123456789 یا +964...)")
        self.phone_input.setStyleSheet("padding: 6px; font-size: 14px;")
        form_layout.addWidget(self.phone_input)
        
        submit_btn = QPushButton("ثبت نام و چاپ برچسب")
        submit_btn.setStyleSheet("""
            QPushButton {
                padding: 12px; 
                font-size: 15px; 
                font-weight: bold;
                background-color: #2196F3; 
                color: white;
                border: none;
                border-radius: 4px;
                margin-top: 15px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        submit_btn.clicked.connect(self.register_user)
        form_layout.addWidget(submit_btn)
        
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        form_layout.addWidget(self.status_label)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        
        self.current_session = None
        
        # Populate sessions list
        self.populate_sessions()
        
        # Periodic timer to update only the remaining capacity of the selected session
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_session_info)
        self.timer.start(5000)

    def showEvent(self, event):
        super().showEvent(event)
        # Refresh sessions list when user switches to this tab
        self.populate_sessions()

    def populate_sessions(self):
        # Temporarily block signals to avoid triggering on_session_changed repeatedly
        self.session_combo.blockSignals(True)
        
        # Save current selection if any
        current_selected_id = None
        if self.session_combo.currentIndex() != -1:
            current_selected_id = self.session_combo.currentData()
            
        self.session_combo.clear()
        
        try:
            sessions = list(Session.select().order_by(Session.session_number.asc()))
        except Exception:
            sessions = []
            
        current_time_session = SessionManager.get_current_session()
        default_index = 0
        
        for index, session in enumerate(sessions):
            try:
                start_time_only = session.start_time.split(' ')[1]
                end_time_only = session.end_time.split(' ')[1]
                display_text = f"سانس {session.session_number} ({start_time_only} تا {end_time_only})"
            except Exception:
                display_text = f"سانس {session.session_number}"
                
            self.session_combo.addItem(display_text, session.id)
            
            # Decide if this is the default selection
            if current_selected_id is not None:
                if session.id == current_selected_id:
                    default_index = index
            elif current_time_session and session.id == current_time_session.id:
                default_index = index
                
        self.session_combo.blockSignals(False)
        
        if self.session_combo.count() > 0:
            self.session_combo.setCurrentIndex(default_index)
            self.on_session_changed(default_index)
        else:
            self.current_session = None
            self.info_label.setText("هیچ سانسی در سیستم تعریف نشده است.")
            self.info_label.setStyleSheet("color: orange; font-size: 14px; font-weight: bold;")

    def on_session_changed(self, index):
        if index == -1:
            self.current_session = None
            return
            
        session_id = self.session_combo.itemData(index)
        try:
            self.current_session = Session.get_by_id(session_id)
            self.update_session_info()
        except Exception:
            self.current_session = None

    def update_session_info(self):
        if self.current_session:
            try:
                # Refresh from database
                session = Session.get_by_id(self.current_session.id)
                rem = SessionManager.get_remaining_capacity(session)
                self.info_label.setText(f"ظرفیت باقیمانده این سانس: {rem} نفر")
                if rem <= 0:
                    self.info_label.setStyleSheet("color: red; font-size: 14px; font-weight: bold;")
                else:
                    self.info_label.setStyleSheet("color: green; font-size: 14px; font-weight: bold;")
            except Exception:
                pass

    def register_user(self):
        if not self.current_session:
            QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک سانس انتخاب کنید.")
            return
            
        lang_code = self.lang_combo.currentData()
        
        success, msg = RegistrationManager.register(
            self.name_input.text(),
            self.phone_input.text(),
            self.current_session,
            print_lang=lang_code
        )
        
        if success:
            self.show_status_message(msg)
            self.name_input.clear()
            self.phone_input.clear()
            self.update_session_info()
        else:
            QMessageBox.warning(self, "خطا", msg)

    def show_status_message(self, message, is_success=True):
        color = "#2e7d32" if is_success else "#c62828"
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: bold; margin-top: 10px;")
        QTimer.singleShot(4000, lambda: self.status_label.setText(""))
