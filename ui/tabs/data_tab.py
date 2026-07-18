from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QHeaderView, QComboBox, QDialog, QFormLayout)
from PyQt6.QtCore import Qt
from models.registrant import Registrant
from models.session import Session
from controllers.export_service import ExportService
from controllers.registration_manager import RegistrationManager
from controllers.printer_service import PrinterService
from utils.persian_utils import to_persian_digits

class EditRegistrantDialog(QDialog):
    def __init__(self, registrant, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ویرایش ثبت‌نام")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.registrant = registrant
        
        layout = QFormLayout()
        
        self.name_input = QLineEdit(self.registrant.full_name)
        self.phone_input = QLineEdit(self.registrant.phone_number)
        
        self.id_input = QLineEdit(str(self.registrant.id)[:4])
        self.id_input.setReadOnly(True)
        self.time_input = QLineEdit(to_persian_digits(self.registrant.registration_time))
        self.time_input.setReadOnly(True)
        self.session_input = QLineEdit(to_persian_digits(str(self.registrant.session.session_number)))
        self.session_input.setReadOnly(True)
        
        layout.addRow("نام:", self.name_input)
        layout.addRow("موبایل:", self.phone_input)
        layout.addRow("کد یکتا:", self.id_input)
        layout.addRow("زمان ثبت:", self.time_input)
        layout.addRow("شماره سانس:", self.session_input)
        
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
        new_name = self.name_input.text()
        new_phone = self.phone_input.text()
        
        success, msg = RegistrationManager.update_registrant(self.registrant.id, new_name, new_phone)
        if success:
            QMessageBox.information(self, "موفق", msg)
            self.accept()
        else:
            QMessageBox.warning(self, "خطا", msg)


class DataTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        layout = QVBoxLayout()
        
        filter_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("جستجو (نام، موبایل، کد)...")
        self.search_input.textChanged.connect(self.load_data)
        
        self.session_filter = QComboBox()
        self.session_filter.addItem("همه سانس‌ها", None)
        for s in Session.select():
            self.session_filter.addItem(f"سانس {to_persian_digits(s.session_number)}", s.id)
        self.session_filter.currentIndexChanged.connect(self.load_data)
        
        export_btn = QPushButton("خروجی اکسل")
        export_btn.clicked.connect(self.export_excel)
        
        refresh_btn = QPushButton("بروزرسانی")
        refresh_btn.clicked.connect(self.refresh_filters)
        
        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(self.session_filter)
        filter_layout.addWidget(refresh_btn)
        filter_layout.addWidget(export_btn)
        layout.addLayout(filter_layout)
        
        self.summary_label = QLabel("")
        layout.addWidget(self.summary_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["کد", "نام", "موبایل", "زمان ثبت", "سانس", "عملیات"])
        
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.load_data()

    def refresh_filters(self):
        self.session_filter.blockSignals(True)
        self.session_filter.clear()
        self.session_filter.addItem("همه سانس‌ها", None)
        for s in Session.select():
            self.session_filter.addItem(f"سانس {to_persian_digits(s.session_number)}", s.id)
        self.session_filter.blockSignals(False)
        self.load_data()

    def get_query(self):
        query = Registrant.select().join(Session)
        
        search_term = self.search_input.text().strip()
        if search_term:
            query = query.where(
                (Registrant.full_name.contains(search_term)) |
                (Registrant.phone_number.contains(search_term)) |
                (Registrant.id.cast('text').contains(search_term))
            )
            
        session_id = self.session_filter.currentData()
        if session_id:
            query = query.where(Registrant.session == session_id)
            
        return query

    def load_data(self):
        query = self.get_query()
        self.table.setRowCount(query.count())
        for row, reg in enumerate(query):
            self.table.setItem(row, 0, QTableWidgetItem(to_persian_digits(str(reg.id)[:4])))
            self.table.setItem(row, 1, QTableWidgetItem(reg.full_name))
            self.table.setItem(row, 2, QTableWidgetItem(to_persian_digits(reg.phone_number)))
            self.table.setItem(row, 3, QTableWidgetItem(to_persian_digits(reg.registration_time)))
            self.table.setItem(row, 4, QTableWidgetItem(to_persian_digits(str(reg.session.session_number))))
            
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(2, 2, 2, 2)
            action_layout.setSpacing(4)
            
            reprint_btn = QPushButton("چاپ مجدد")
            reprint_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3; 
                    color: white; 
                    padding: 2px 4px; 
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            reprint_btn.clicked.connect(lambda checked, r=reg: self.reprint_label(r))
            
            edit_btn = QPushButton("ویرایش")
            edit_btn.setStyleSheet("""
                QPushButton {
                    padding: 2px 4px; 
                    font-size: 11px;
                }
            """)
            edit_btn.clicked.connect(lambda checked, r=reg: self.edit_registrant(r))
            
            delete_btn = QPushButton("حذف")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f44336; 
                    color: white; 
                    padding: 2px 4px; 
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #d32f2f;
                }
            """)
            delete_btn.clicked.connect(lambda checked, r=reg: self.delete_registrant(r))
            
            action_layout.addWidget(reprint_btn)
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(row, 5, action_widget)
            
        self.summary_label.setText(f"تعداد کل نمایش داده شده: {to_persian_digits(query.count())}")

    def edit_registrant(self, registrant):
        dialog = EditRegistrantDialog(registrant, self)
        if dialog.exec():
            self.load_data()

    def delete_registrant(self, registrant):
        reply = QMessageBox.question(self, 'حذف ثبت‌نام', 
                                    "آیا از حذف این مورد مطمئن هستید؟",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                    QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            success, msg = RegistrationManager.delete_registrant(registrant.id)
            if success:
                QMessageBox.information(self, "موفق", msg)
                self.load_data()
            else:
                QMessageBox.warning(self, "خطا", msg)
                
    def reprint_label(self, registrant):
        try:
            PrinterService.print_label(registrant)
            QMessageBox.information(self, "موفق", "دستور چاپ ارسال شد.")
        except Exception as e:
            QMessageBox.warning(self, "خطا", f"خطا در چاپ: {e}")

    def export_excel(self):
        try:
            query = self.get_query()
            path = ExportService.export_to_excel(query)
            QMessageBox.information(self, "موفق", f"فایل با موفقیت در مسیر زیر ذخیره شد:\n{path}")
        except Exception as e:
            QMessageBox.warning(self, "خطا", f"خطا در ایجاد فایل اکسل: {e}")
