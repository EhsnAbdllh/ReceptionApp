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
        self.name_input.setMaxLength(24)
        self.phone_input = QLineEdit(self.registrant.phone_number)
        self.phone_input.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
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
            from PyQt6.QtWidgets import QApplication
            main_win = QApplication.activeWindow()
            if main_win and hasattr(main_win, 'statusBar'):
                main_win.statusBar().showMessage(msg, 4000)
            self.accept()
        else:
            QMessageBox.warning(self, "خطا", msg)


class DataTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        layout = QVBoxLayout()
        
        # Debounce timer for search
        from PyQt6.QtCore import QTimer
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.on_search_timeout)
        
        filter_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("جستجو (نام، موبایل، کد)...")
        self.search_input.textChanged.connect(self.on_search_changed)
        
        self.session_filter = QComboBox()
        self.session_filter.addItem("همه سانس‌ها", None)
        for s in Session.select():
            self.session_filter.addItem(f"سانس {to_persian_digits(s.session_number)}", s.id)
        self.session_filter.currentIndexChanged.connect(self.on_session_changed)
        
        export_btn = QPushButton("خروجی اکسل")
        export_btn.clicked.connect(self.export_excel)
        
        refresh_btn = QPushButton("بروزرسانی")
        refresh_btn.clicked.connect(self.refresh_filters)
        
        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(self.session_filter)
        filter_layout.addWidget(refresh_btn)
        filter_layout.addWidget(export_btn)
        layout.addLayout(filter_layout)
        
        summary_layout = QHBoxLayout()
        self.summary_label = QLabel("")
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        summary_layout.addWidget(self.summary_label)
        summary_layout.addWidget(self.status_label)
        summary_layout.addStretch()
        layout.addLayout(summary_layout)
        
        # Pagination variables
        self.current_page = 1
        self.page_size = 50
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["کد", "نام", "موبایل", "زمان ثبت", "سانس", "عملیات"])
        
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.table)
        
        # Pagination layout
        pagination_layout = QHBoxLayout()
        pagination_layout.addStretch()
        
        self.prev_btn = QPushButton("صفحه قبل")
        self.prev_btn.clicked.connect(self.prev_page)
        
        self.page_label = QLabel("صفحه ۱")
        self.page_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 0 15px;")
        
        self.next_btn = QPushButton("صفحه بعد")
        self.next_btn.clicked.connect(self.next_page)
        
        pagination_layout.addWidget(self.prev_btn)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_btn)
        pagination_layout.addStretch()
        
        layout.addLayout(pagination_layout)
        
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

    def on_search_changed(self):
        # Reset to page 1 and start debounce timer
        self.current_page = 1
        self.search_timer.start(300)

    def on_search_timeout(self):
        self.load_data()

    def on_session_changed(self):
        self.current_page = 1
        self.load_data()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_data()

    def next_page(self):
        self.current_page += 1
        self.load_data()

    def load_data(self):
        self.table.setRowCount(0)
        
        base_query = self.get_query()
        total_count = base_query.count()
        
        import math
        total_pages = math.ceil(total_count / self.page_size)
        if total_pages == 0:
            total_pages = 1
            
        if self.current_page > total_pages:
            self.current_page = total_pages
        if self.current_page < 1:
            self.current_page = 1
            
        paginated_query = base_query.limit(self.page_size).offset((self.current_page - 1) * self.page_size)
        
        self.table.setRowCount(paginated_query.count())
        for row, reg in enumerate(paginated_query):
            self.table.setItem(row, 0, QTableWidgetItem(to_persian_digits(str(reg.id)[:4])))
            self.table.setItem(row, 1, QTableWidgetItem(reg.full_name))
            self.table.setItem(row, 2, QTableWidgetItem("\u200e" + to_persian_digits(reg.phone_number)))
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
            
        start_idx = (self.current_page - 1) * self.page_size + 1 if total_count > 0 else 0
        end_idx = min(self.current_page * self.page_size, total_count)
        
        self.summary_label.setText(
            f"نمایش {to_persian_digits(start_idx)} تا {to_persian_digits(end_idx)} از "
            f"کل {to_persian_digits(total_count)} پذیرش"
        )
        
        self.page_label.setText(to_persian_digits(f"صفحه {self.current_page} از {total_pages}"))
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < total_pages)

    def edit_registrant(self, registrant):
        dialog = EditRegistrantDialog(registrant, self)
        if dialog.exec():
            self.load_data()
            self.show_status_message("✓ اطلاعات پذیرش با موفقیت ویرایش شد.")

    def delete_registrant(self, registrant):
        reply = QMessageBox.question(self, 'حذف ثبت‌نام', 
                                    "آیا از حذف این مورد مطمئن هستید؟",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                    QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            success, msg = RegistrationManager.delete_registrant(registrant.id)
            if success:
                self.show_status_message(msg)
                self.load_data()
            else:
                QMessageBox.warning(self, "خطا", msg)
                
    def reprint_label(self, registrant):
        try:
            PrinterService.print_label(registrant)
            self.show_status_message("✓ دستور چاپ با موفقیت ارسال شد.")
        except Exception as e:
            QMessageBox.warning(self, "خطا", f"خطا در چاپ: {e}")

    def export_excel(self):
        try:
            import os
            query = self.get_query()
            path = ExportService.export_to_excel(query)
            
            # Automatically open the exported file on Windows
            try:
                os.startfile(path)
            except Exception as e:
                print(f"Error opening exported excel file: {e}")
                
            self.show_status_message("✓ فایل اکسل با موفقیت ایجاد و باز شد.")
        except Exception as e:
            QMessageBox.warning(self, "خطا", f"خطا در ایجاد فایل اکسل: {e}")

    def show_status_message(self, message, is_success=True):
        from PyQt6.QtCore import QTimer
        color = "#2e7d32" if is_success else "#c62828"
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: bold; margin-right: 15px;")
        QTimer.singleShot(4000, lambda: self.status_label.setText(""))
