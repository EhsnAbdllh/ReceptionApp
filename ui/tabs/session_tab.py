from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QHeaderView, QDialog, QFormLayout)
from PyQt6.QtCore import Qt
from models.session import Session
from models.registrant import Registrant
from controllers.session_manager import SessionManager
from ui.components.jalali_datetime_picker import JalaliDateTimePicker
from utils.persian_utils import to_persian_digits
import jdatetime

class EditSessionDialog(QDialog):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ویرایش سانس")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.session = session
        
        layout = QFormLayout()
        
        self.start_input = JalaliDateTimePicker(initial_datetime_str=self.session.start_time)
        self.end_input = JalaliDateTimePicker(initial_datetime_str=self.session.end_time)
        self.cap_input = QLineEdit(str(self.session.total_capacity))
        
        layout.addRow("شروع:", self.start_input)
        layout.addRow("پایان:", self.end_input)
        layout.addRow("ظرفیت:", self.cap_input)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("ذخیره")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("انصراف")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addRow(btn_layout)
        self.setLayout(layout)

    def save(self):
        start = self.start_input.get_datetime_str()
        end = self.end_input.get_datetime_str()
        try:
            cap = int(self.cap_input.text())
        except ValueError:
            QMessageBox.warning(self, "خطا", "ظرفیت باید عدد باشد.")
            return

        if SessionManager.is_overlap(start, end, exclude_session_id=self.session.id):
            QMessageBox.warning(self, "خطا", "تداخل زمانی با سانس‌های دیگر وجود دارد یا زمان پایان کوچکتر از شروع است.")
            return
            
        self.session.start_time = start
        self.session.end_time = end
        self.session.total_capacity = cap
        self.session.save()
        self.accept()

class SessionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        layout = QVBoxLayout()
        
        form_layout = QHBoxLayout()
        
        self.start_input = JalaliDateTimePicker()
        self.end_input = JalaliDateTimePicker()
        
        self.cap_input = QLineEdit()
        self.cap_input.setPlaceholderText("ظرفیت")
        
        add_btn = QPushButton("افزودن سانس")
        add_btn.clicked.connect(self.add_session)
        
        form_layout.addWidget(QLabel("شروع:"))
        form_layout.addWidget(self.start_input)
        form_layout.addSpacing(20)
        form_layout.addWidget(QLabel("پایان:"))
        form_layout.addWidget(self.end_input)
        form_layout.addSpacing(20)
        form_layout.addWidget(QLabel("ظرفیت:"))
        form_layout.addWidget(self.cap_input)
        form_layout.addWidget(add_btn)
        form_layout.addStretch()
        
        layout.addLayout(form_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["شماره سانس", "زمان شروع", "زمان پایان", "ظرفیت کل", "عملیات"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        sessions = Session.select()
        self.table.setRowCount(sessions.count())
        for row, session in enumerate(sessions):
            self.table.setItem(row, 0, QTableWidgetItem(to_persian_digits(session.session_number)))
            self.table.setItem(row, 1, QTableWidgetItem(to_persian_digits(session.start_time)))
            self.table.setItem(row, 2, QTableWidgetItem(to_persian_digits(session.end_time)))
            self.table.setItem(row, 3, QTableWidgetItem(to_persian_digits(session.total_capacity)))
            
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("ویرایش")
            edit_btn.clicked.connect(lambda checked, s=session: self.edit_session(s))
            
            delete_btn = QPushButton("حذف")
            delete_btn.setStyleSheet("background-color: #f44336; color: white;")
            delete_btn.clicked.connect(lambda checked, s=session: self.delete_session(s))
            
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(row, 4, action_widget)

    def add_session(self):
        try:
            cap = int(self.cap_input.text())
            start = self.start_input.get_datetime_str()
            end = self.end_input.get_datetime_str()

            if SessionManager.is_overlap(start, end):
                QMessageBox.warning(self, "خطا", "تداخل زمانی با سانس‌های دیگر وجود دارد یا زمان پایان کوچکتر از شروع است.")
                return
                
            num = SessionManager.get_next_session_number()
            Session.create(session_number=num, start_time=start, end_time=end, total_capacity=cap)
            QMessageBox.information(self, "موفق", "سانس با موفقیت اضافه شد.")
            self.cap_input.clear()
            self.load_data()
            
        except ValueError:
            QMessageBox.warning(self, "خطا", "مقدار عددی برای ظرفیت وارد کنید.")
        except Exception as e:
            QMessageBox.warning(self, "خطا", str(e))

    def edit_session(self, session):
        dialog = EditSessionDialog(session, self)
        if dialog.exec():
            self.load_data()

    def delete_session(self, session):
        has_registrants = Registrant.select().where(Registrant.session == session).count() > 0
        if has_registrants:
            reply = QMessageBox.question(self, 'حذف سانس', 
                                        "با حذف این سانس همه پذیرشهای انجام گرفته در این سانس حذف میشوند. آیا مطمئن هستید؟",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                        QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return
        else:
            reply = QMessageBox.question(self, 'حذف سانس', 
                                        "آیا از حذف این سانس مطمئن هستید؟",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                        QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return
                
        try:
            SessionManager.delete_session(session.id)
            QMessageBox.information(self, "موفق", "سانس با موفقیت حذف شد.")
            self.load_data()
        except Exception as e:
            QMessageBox.warning(self, "خطا", f"خطا در حذف: {e}")
