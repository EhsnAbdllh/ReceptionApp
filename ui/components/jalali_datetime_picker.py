from PyQt6.QtWidgets import QWidget, QHBoxLayout, QComboBox, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
import jdatetime

class JalaliDateTimePicker(QWidget):
    dateTimeChanged = pyqtSignal(str)

    def __init__(self, parent=None, initial_datetime_str=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.year_cb = QComboBox()
        self.month_cb = QComboBox()
        self.day_cb = QComboBox()
        self.hour_cb = QComboBox()
        self.minute_cb = QComboBox()
        
        current_jdate = jdatetime.datetime.now()
        
        for y in range(1400, 1450):
            self.year_cb.addItem(str(y))
            
        for m in range(1, 13):
            self.month_cb.addItem(f"{m:02d}")
            
        for d in range(1, 32):
            self.day_cb.addItem(f"{d:02d}")
            
        for h in range(0, 24):
            self.hour_cb.addItem(f"{h:02d}")
            
        for min in range(0, 60, 5):
            self.minute_cb.addItem(f"{min:02d}")
            
        layout.addWidget(self.year_cb)
        layout.addWidget(QLabel("/"))
        layout.addWidget(self.month_cb)
        layout.addWidget(QLabel("/"))
        layout.addWidget(self.day_cb)
        layout.addWidget(QLabel("  ساعت: "))
        layout.addWidget(self.hour_cb)
        layout.addWidget(QLabel(":"))
        layout.addWidget(self.minute_cb)
        
        self.set_datetime(initial_datetime_str if initial_datetime_str else current_jdate.strftime("%Y/%m/%d %H:%M"))
        
        # Connect change signals to emit dateTimeChanged
        self.year_cb.currentIndexChanged.connect(self._on_change)
        self.month_cb.currentIndexChanged.connect(self._on_change)
        self.day_cb.currentIndexChanged.connect(self._on_change)
        self.hour_cb.currentIndexChanged.connect(self._on_change)
        self.minute_cb.currentIndexChanged.connect(self._on_change)

    def _on_change(self):
        self.dateTimeChanged.emit(self.get_datetime_str())

    def set_datetime(self, dt_str):
        try:
            dt = jdatetime.datetime.strptime(dt_str, "%Y/%m/%d %H:%M")
            
            # Temporarily block signals of child combos to avoid multiple dateTimeChanged emissions
            self.year_cb.blockSignals(True)
            self.month_cb.blockSignals(True)
            self.day_cb.blockSignals(True)
            self.hour_cb.blockSignals(True)
            self.minute_cb.blockSignals(True)
            
            self.year_cb.setCurrentText(str(dt.year))
            self.month_cb.setCurrentText(f"{dt.month:02d}")
            self.day_cb.setCurrentText(f"{dt.day:02d}")
            self.hour_cb.setCurrentText(f"{dt.hour:02d}")
            min_val = (dt.minute // 5) * 5
            self.minute_cb.setCurrentText(f"{min_val:02d}")
            
            self.year_cb.blockSignals(False)
            self.month_cb.blockSignals(False)
            self.day_cb.blockSignals(False)
            self.hour_cb.blockSignals(False)
            self.minute_cb.blockSignals(False)
        except ValueError:
            pass

    def get_datetime_str(self):
        y = self.year_cb.currentText()
        m = self.month_cb.currentText()
        d = self.day_cb.currentText()
        h = self.hour_cb.currentText()
        min = self.minute_cb.currentText()
        return f"{y}/{m}/{d} {h}:{min}"
