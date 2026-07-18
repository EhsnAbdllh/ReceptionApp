from PyQt6.QtWidgets import (QWidget, QVBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from controllers.session_manager import SessionManager
from controllers.registration_manager import RegistrationManager

class RegistrationTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        layout = QVBoxLayout()
        
        self.info_label = QLabel("درحال بررسی سانس فعال...")
        self.info_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(self.info_label)
        
        form_layout = QVBoxLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("نام و نام خانوادگی")
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("شماره موبایل (مثال: 09123456789)")
        
        submit_btn = QPushButton("ثبت نام و چاپ برچسب")
        submit_btn.setStyleSheet("padding: 10px; font-size: 14px; background-color: #2196F3; color: white;")
        submit_btn.clicked.connect(self.register_user)
        
        form_layout.addWidget(QLabel("نام و نام خانوادگی:"))
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(QLabel("شماره موبایل:"))
        form_layout.addWidget(self.phone_input)
        form_layout.addWidget(submit_btn)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        
        self.current_session = None
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_session_info)
        self.timer.start(5000)
        self.update_session_info()

    def update_session_info(self):
        self.current_session = SessionManager.get_current_session()
        if self.current_session:
            rem = SessionManager.get_remaining_capacity(self.current_session)
            self.info_label.setText(f"سانس فعال: {self.current_session.session_number} | ظرفیت باقیمانده: {rem}")
            if rem <= 0:
                self.info_label.setStyleSheet("color: red; font-size: 16px; font-weight: bold; margin-bottom: 20px;")
            else:
                self.info_label.setStyleSheet("color: green; font-size: 16px; font-weight: bold; margin-bottom: 20px;")
        else:
            self.info_label.setText("هیچ سانس فعالی در این زمان وجود ندارد.")
            self.info_label.setStyleSheet("color: orange; font-size: 16px; font-weight: bold; margin-bottom: 20px;")

    def register_user(self):
        if not self.current_session:
            QMessageBox.warning(self, "خطا", "سانس فعالی وجود ندارد.")
            return
            
        success, msg = RegistrationManager.register(
            self.name_input.text(),
            self.phone_input.text(),
            self.current_session
        )
        
        if success:
            QMessageBox.information(self, "نتیجه", msg)
            self.name_input.clear()
            self.phone_input.clear()
            self.update_session_info()
        else:
            QMessageBox.warning(self, "خطا", msg)
