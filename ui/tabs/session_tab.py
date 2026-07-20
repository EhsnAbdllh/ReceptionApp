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
        
        self.start_input.dateTimeChanged.connect(self.on_start_changed)
        self.end_input.dateTimeChanged.connect(self.on_end_changed)
        
    def on_start_changed(self, dt_str):
        try:
            start_dt = jdatetime.datetime.strptime(dt_str, "%Y/%m/%d %H:%M")
            end_dt = start_dt + jdatetime.timedelta(minutes=30)
            end_str = end_dt.strftime("%Y/%m/%d %H:%M")
            self.end_input.blockSignals(True)
            self.end_input.set_datetime(end_str)
            self.end_input.blockSignals(False)
        except Exception:
            pass

    def on_end_changed(self, dt_str):
        try:
            end_dt = jdatetime.datetime.strptime(dt_str, "%Y/%m/%d %H:%M")
            start_dt = end_dt - jdatetime.timedelta(minutes=30)
            start_str = start_dt.strftime("%Y/%m/%d %H:%M")
            self.start_input.blockSignals(True)
            self.start_input.set_datetime(start_str)
            self.start_input.blockSignals(False)
        except Exception:
            pass
        
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

        is_valid, err_msg = SessionManager.validate_session_times(start, end, exclude_session_id=self.session.id)
        if not is_valid:
            QMessageBox.warning(self, "خطا", err_msg)
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
        
        self.start_input.dateTimeChanged.connect(self.on_start_changed)
        self.end_input.dateTimeChanged.connect(self.on_end_changed)
        
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

    def on_start_changed(self, dt_str):
        try:
            start_dt = jdatetime.datetime.strptime(dt_str, "%Y/%m/%d %H:%M")
            end_dt = start_dt + jdatetime.timedelta(minutes=30)
            end_str = end_dt.strftime("%Y/%m/%d %H:%M")
            self.end_input.blockSignals(True)
            self.end_input.set_datetime(end_str)
            self.end_input.blockSignals(False)
        except Exception:
            pass

    def on_end_changed(self, dt_str):
        try:
            end_dt = jdatetime.datetime.strptime(dt_str, "%Y/%m/%d %H:%M")
            start_dt = end_dt - jdatetime.timedelta(minutes=30)
            start_str = start_dt.strftime("%Y/%m/%d %H:%M")
            self.start_input.blockSignals(True)
            self.start_input.set_datetime(start_str)
            self.start_input.blockSignals(False)
        except Exception:
            pass

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

            is_valid, err_msg = SessionManager.validate_session_times(start, end)
            if not is_valid:
                QMessageBox.warning(self, "خطا", err_msg)
                return
                
            num = SessionManager.get_next_session_number()
            Session.create(session_number=num, start_time=start, end_time=end, total_capacity=cap)
            
            main_win = self.window()
            if hasattr(main_win, 'statusBar'):
                main_win.statusBar().showMessage("سانس با موفقیت اضافه شد.", 4000)
                
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
        registrants_count = Registrant.select().where(Registrant.session == session).count()
        if registrants_count > 0:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("هشدار بسیار مهم: حذف زنجیره‌ای")
            msg_box.setText("<font color='#d32f2f'><b>توجه: خطر حذف اطلاعات پذیرش‌ها!</b></font>")
            msg_box.setInformativeText(
                f"با حذف این سانس، <b>تمامی {registrants_count} پذیرش انجام گرفته در آن نیز به صورت زنجیره‌ای حذف خواهند شد!</b><br><br>"
                "این عملیات غیرقابل بازگشت است. آیا کاملاً مطمئن هستید؟"
            )
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.No)
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #ffebee;
                    font-size: 14px;
                }
                QLabel {
                    color: #333333;
                }
                QPushButton {
                    padding: 6px 15px;
                    font-weight: bold;
                }
            """)
            reply = msg_box.exec()
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
            main_win = self.window()
            if hasattr(main_win, 'statusBar'):
                main_win.statusBar().showMessage("سانس با موفقیت حذف شد.", 4000)
            self.load_data()
        except Exception as e:
            QMessageBox.warning(self, "خطا", f"خطا در حذف: {e}")
