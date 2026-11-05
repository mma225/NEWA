import sys
import time
import platform
from datetime import datetime

from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QTabWidget, QComboBox, QSpinBox,
    QCheckBox, QCalendarWidget, QProgressBar, QSlider, QSystemTrayIcon,
    QMenu
)


class FloatingNotch(QWidget):
    """Simple always-on-top desktop notch prototype."""
    def __init__(self, parent_window):
        super().__init__(None)
        self.parent_window = parent_window
        self.expanded = False
        self.setWindowFlags(
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(210, 42)
        self.move_to_top()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_clock)
        self.timer.start(1000)
        self.build_ui()

    def move_to_top(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.center().x() - self.width() // 2, screen.top() + 8)

    def build_ui(self):
        self.setStyleSheet("""
            QWidget#notch {
                background: rgba(18, 20, 26, 238);
                border: 1px solid rgba(255,255,255,45);
                border-radius: 20px;
                color: white;
            }
            QLabel { color: white; }
            QPushButton {
                color: white; background: rgba(255,255,255,22);
                border: 0; border-radius: 9px; padding: 5px 9px;
            }
            QPushButton:hover { background: rgba(255,255,255,45); }
        """)
        self.panel = QFrame(self)
        self.panel.setObjectName("notch")
        self.panel.setGeometry(0, 0, self.width(), self.height())
        self.layout = QVBoxLayout(self.panel)
        self.layout.setContentsMargins(12, 7, 12, 7)
        self.layout.setSpacing(5)

        top = QHBoxLayout()
        self.title = QLabel("NUSA")
        self.title.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.clock = QLabel()
        self.clock.setAlignment(Qt.AlignmentFlag.AlignRight)
        top.addWidget(self.title)
        top.addStretch()
        top.addWidget(self.clock)
        self.layout.addLayout(top)

        self.details = QWidget()
        detail_layout = QVBoxLayout(self.details)
        detail_layout.setContentsMargins(0, 3, 0, 0)
        detail_layout.addWidget(QLabel("Floating Notch • Windows 11"))
        buttons = QHBoxLayout()
        btn_app = QPushButton("Buka Nusa")
        btn_app.clicked.connect(self.parent_window.showNormal)
        btn_hide = QPushButton("Tutup")
        btn_hide.clicked.connect(self.hide)
        buttons.addWidget(btn_app)
        buttons.addWidget(btn_hide)
        detail_layout.addLayout(buttons)
        self.layout.addWidget(self.details)
        self.details.hide()
        self.refresh_clock()

    def refresh_clock(self):
        self.clock.setText(datetime.now().strftime("%H:%M"))

    def set_expanded(self, expanded):
        self.expanded = expanded
        self.details.setVisible(expanded)
        self.setFixedSize(260 if expanded else 210, 112 if expanded else 42)
        self.panel.setGeometry(0, 0, self.width(), self.height())
        self.move_to_top()

    def enterEvent(self, event):
        if getattr(self, "interaction", "Hover") == "Hover":
            self.set_expanded(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if getattr(self, "interaction", "Hover") == "Hover":
            self.set_expanded(False)
        super().leaveEvent(event)

    def set_interaction(self, mode):
        self.interaction = mode

    def mousePressEvent(self, event):
        if getattr(self, "interaction", "Hover") == "Click" and event.button() == Qt.MouseButton.LeftButton:
            self.set_expanded(not self.expanded)
        super().mousePressEvent(event)


class NusaWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nusa Rebuilt")
        self.resize(760, 590)
        self.setMinimumSize(QSize(650, 500))
        self.remaining = 25 * 60
        self.total_seconds = self.remaining
        self.running = False
        self.tick = QTimer(self)
        self.tick.timeout.connect(self.on_tick)
        self.build()
        self.notch = FloatingNotch(self)
        self.notch.show()

    def build(self):
        self.setStyleSheet("""
            QMainWindow, QWidget { background: #171a22; color: #eef1f7; font-family: 'Segoe UI'; }
            QTabWidget::pane { border: 1px solid #343a49; border-radius: 10px; }
            QTabBar::tab { background: #252a36; padding: 10px 18px; margin: 3px; border-radius: 7px; }
            QTabBar::tab:selected { background: #465b83; }
            QPushButton { background: #40577e; color: white; border: 0; border-radius: 8px; padding: 9px 14px; }
            QPushButton:hover { background: #526d9b; }
            QFrame#card { background: #222733; border: 1px solid #343b4b; border-radius: 12px; }
            QComboBox, QSpinBox { background: #252b38; border: 1px solid #41495b; border-radius: 6px; padding: 6px; }
            QProgressBar { background: #303746; border: 0; border-radius: 6px; text-align: center; height: 12px; }
            QProgressBar::chunk { background: #81a9e8; border-radius: 6px; }
        """)
        root = QWidget()
        layout = QVBoxLayout(root)
        header = QHBoxLayout()
        name = QLabel("Nusa")
        name.setFont(QFont("Segoe UI", 23, QFont.Weight.Bold))
        subtitle = QLabel("Desktop companion • Windows 11")
        subtitle.setStyleSheet("color:#aab4c7")
        header.addWidget(name)
        header.addWidget(subtitle)
        header.addStretch()
        layout.addLayout(header)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.make_focus_tab(), "Pomodoro")
        self.tabs.addTab(self.make_calendar_tab(), "Calendar")
        self.tabs.addTab(self.make_hud_tab(), "HUD & Popups")
        self.tabs.addTab(self.make_appearance_tab(), "Appearance")
        layout.addWidget(self.tabs)
        self.setCentralWidget(root)

    def make_focus_tab(self):
        page = QWidget()
        v = QVBoxLayout(page)
        card = QFrame()
        card.setObjectName("card")
        c = QVBoxLayout(card)
        title = QLabel("Focus timer")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.timer_label = QLabel("25:00")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setFont(QFont("Segoe UI", 42, QFont.Weight.Bold))
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        row = QHBoxLayout()
        self.mode = QComboBox()
        self.mode.addItems(["Focus", "Short Break", "Long Break"])
        self.mode.currentTextChanged.connect(self.change_mode)
        self.focus_min = QSpinBox()
        self.focus_min.setRange(1, 180)
        self.focus_min.setValue(25)
        self.short_min = QSpinBox()
        self.short_min.setRange(1, 60)
        self.short_min.setValue(5)
        self.long_min = QSpinBox()
        self.long_min.setRange(1, 90)
        self.long_min.setValue(15)
        row.addWidget(QLabel("Mode"))
        row.addWidget(self.mode)
        row.addWidget(QLabel("Focus"))
        row.addWidget(self.focus_min)
        row.addWidget(QLabel("Short"))
        row.addWidget(self.short_min)
        row.addWidget(QLabel("Long"))
        row.addWidget(self.long_min)
        self.start_btn = QPushButton("Mulai")
        self.start_btn.clicked.connect(self.toggle_timer)
        reset = QPushButton("Reset")
        reset.clicked.connect(self.reset_timer)
        c.addWidget(title)
        c.addWidget(self.timer_label)
        c.addWidget(self.progress)
        c.addLayout(row)
        controls = QHBoxLayout()
        controls.addStretch()
        controls.addWidget(self.start_btn)
        controls.addWidget(reset)
        controls.addStretch()
        c.addLayout(controls)
        v.addWidget(card)
        v.addStretch()
        return page

    def duration_for_mode(self):
        return {
            "Focus": self.focus_min.value(),
            "Short Break": self.short_min.value(),
            "Long Break": self.long_min.value()
        }[self.mode.currentText()] * 60

    def change_mode(self, _):
        self.running = False
        self.tick.stop()
        self.start_btn.setText("Mulai")
        self.reset_timer()

    def toggle_timer(self):
        self.running = not self.running
        if self.running:
            self.tick.start(1000)
            self.start_btn.setText("Jeda")
        else:
            self.tick.stop()
            self.start_btn.setText("Lanjut")

    def reset_timer(self):
        self.remaining = self.duration_for_mode()
        self.total_seconds = self.remaining
        self.update_timer_display()

    def on_tick(self):
        if self.remaining > 0:
            self.remaining -= 1
            self.update_timer_display()
        else:
            self.tick.stop()
            self.running = False
            self.start_btn.setText("Mulai")
            self.timer_label.setText("Selesai!")

    def update_timer_display(self):
        self.timer_label.setText(f"{self.remaining // 60:02d}:{self.remaining % 60:02d}")
        done = self.total_seconds - self.remaining
        self.progress.setValue(int(done * 100 / max(1, self.total_seconds)))

    def make_calendar_tab(self):
        page = QWidget()
        v = QVBoxLayout(page)
        note = QLabel("Kalender bulanan")
        note.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.week_start = QComboBox()
        self.week_start.addItems(["Minggu", "Senin"])
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.week_start.currentTextChanged.connect(self.set_week_start)
        v.addWidget(note)
        v.addWidget(QLabel("Awal minggu"))
        v.addWidget(self.week_start)
        v.addWidget(self.calendar)
        return page

    def set_week_start(self, value):
        from PySide6.QtCore import Qt as Q
        self.calendar.setFirstDayOfWeek(
            Q.Day.Sunday if value == "Minggu" else Q.Day.Monday
        )

    def make_hud_tab(self):
        page = QWidget()
        v = QVBoxLayout(page)
        title = QLabel("HUD & Popups")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        v.addWidget(title)
        v.addWidget(QLabel("Pilih notifikasi sistem yang ingin ditampilkan (opsi antarmuka)."))
        for text in ["Volume", "Brightness", "Caps Lock", "Input language",
                     "Battery", "Wi-Fi", "Bluetooth headset"]:
            cb = QCheckBox(text)
            cb.setChecked(True)
            v.addWidget(cb)
        v.addStretch()
        return page

    def make_appearance_tab(self):
        page = QWidget()
        v = QVBoxLayout(page)
        title = QLabel("Floating Notch & Appearance")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        v.addWidget(title)
        v.addWidget(QLabel("Mode tampilan"))
        self.notch_mode = QComboBox()
        self.notch_mode.addItems(["Floating", "Classic"])
        self.notch_mode.currentTextChanged.connect(self.toggle_notch)
        v.addWidget(self.notch_mode)
        v.addWidget(QLabel("Glass tint"))
        self.tint = QSlider(Qt.Orientation.Horizontal)
        self.tint.setRange(10, 100)
        self.tint.setValue(85)
        self.tint.valueChanged.connect(self.change_tint)
        v.addWidget(self.tint)
        self.hover_option = QComboBox()
        self.hover_option.addItems(["Hover", "Click"])
        v.addWidget(QLabel("Interaksi notch"))
        v.addWidget(self.hover_option)
        apply_btn = QPushButton("Terapkan pengaturan")
        apply_btn.clicked.connect(self.apply_appearance)
        v.addWidget(apply_btn)
        v.addStretch()
        return page

    def toggle_notch(self, mode):
        if hasattr(self, "notch"):
            self.notch.setVisible(mode == "Floating")

    def change_tint(self, value):
        if hasattr(self, "notch"):
            self.notch.setWindowOpacity(value / 100)

    def apply_appearance(self):
        if hasattr(self, "notch"):
            self.notch.setVisible(self.notch_mode.currentText() == "Floating")
            self.notch.set_interaction(self.hover_option.currentText())

    def closeEvent(self, event):
        if hasattr(self, "notch"):
            self.notch.close()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Nusa Rebuilt")
    window = NusaWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
