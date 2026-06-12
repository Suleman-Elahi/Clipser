from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QSpinBox,
    QPushButton,
    QLabel,
    QGroupBox,
    QFrame,
    QComboBox,
    QApplication,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from app._icon import app_icon


class SettingsDialog(QDialog):
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self._settings = settings_manager
        self.setWindowTitle("Clipser Settings")
        self.setWindowIcon(app_icon())
        self.setFixedSize(360, 400)
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.WindowCloseButtonHint
            | Qt.WindowType.WindowTitleHint
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Settings")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.DemiBold))
        layout.addWidget(title)

        general = QGroupBox("General")
        general_layout = QVBoxLayout(general)

        self._auto_start_cb = QCheckBox("Launch at startup")
        self._auto_start_cb.setChecked(self._settings.auto_start)
        general_layout.addWidget(self._auto_start_cb)

        self._timestamps_cb = QCheckBox("Show timestamps")
        self._timestamps_cb.setChecked(self._settings.show_timestamps)
        general_layout.addWidget(self._timestamps_cb)

        theme_row = QHBoxLayout()
        theme_label = QLabel("Theme:")
        theme_label.setFont(QFont("Segoe UI", 9))
        self._theme_combo = QComboBox()
        self._theme_combo.addItems(["Dark", "Light"])
        self._theme_combo.setCurrentIndex(0 if self._settings.theme == "dark" else 1)
        self._theme_combo.setFixedWidth(100)
        theme_row.addWidget(theme_label)
        theme_row.addStretch()
        theme_row.addWidget(self._theme_combo)
        general_layout.addLayout(theme_row)

        hotkey_row = QHBoxLayout()
        hotkey_label = QLabel("Hotkey:")
        hotkey_label.setFont(QFont("Segoe UI", 9))
        self._hotkey_combo = QComboBox()
        self._hotkey_combo.setEditable(True)
        self._hotkey_combo.addItems([
            "ctrl+shift+v",
            "alt+shift+v",
            "ctrl+alt+v",
            "win+v",
            "win+shift+v",
        ])
        self._hotkey_combo.setCurrentText(self._settings.hotkey)
        self._hotkey_combo.setFixedWidth(140)
        hotkey_row.addWidget(hotkey_label)
        hotkey_row.addStretch()
        hotkey_row.addWidget(self._hotkey_combo)
        general_layout.addLayout(hotkey_row)

        layout.addWidget(general)

        history = QGroupBox("History")
        history_layout = QVBoxLayout(history)

        max_row = QHBoxLayout()
        max_label = QLabel("Max entries:")
        max_label.setFont(QFont("Segoe UI", 9))
        self._max_spin = QSpinBox()
        self._max_spin.setRange(10, 2000)
        self._max_spin.setValue(self._settings.max_entries)
        self._max_spin.setFixedWidth(90)
        self._max_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        max_row.addWidget(max_label)
        max_row.addStretch()
        max_row.addWidget(self._max_spin)
        history_layout.addLayout(max_row)

        clear_btn = QPushButton("Clear All History")
        clear_btn.setObjectName("DangerButton")
        clear_btn.setFixedHeight(30)
        clear_btn.clicked.connect(self._on_clear)
        history_layout.addWidget(clear_btn)

        layout.addWidget(history)

        layout.addStretch()

        buttons = QHBoxLayout()
        buttons.addStretch()

        save_btn = QPushButton("Save")
        save_btn.setObjectName("PrimaryButton")
        save_btn.setFixedWidth(90)
        save_btn.clicked.connect(self._on_save)
        buttons.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("SecondaryButton")
        cancel_btn.setFixedWidth(90)
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)

        layout.addLayout(buttons)

        self._clear_requested = False

    def _on_save(self):
        self._settings.auto_start = self._auto_start_cb.isChecked()
        self._settings.max_entries = self._max_spin.value()
        self._settings.show_timestamps = self._timestamps_cb.isChecked()
        self._settings.theme = "dark" if self._theme_combo.currentIndex() == 0 else "light"
        self._settings.hotkey = self._hotkey_combo.currentText().strip()
        self.accept()

    def _on_clear(self):
        self._clear_requested = True

    def is_clear_requested(self):
        return self._clear_requested

    def showEvent(self, event):
        super().showEvent(event)
        self._auto_start_cb.setChecked(self._settings.auto_start)
        self._max_spin.setValue(self._settings.max_entries)
        self._timestamps_cb.setChecked(self._settings.show_timestamps)
        self._theme_combo.setCurrentIndex(0 if self._settings.theme == "dark" else 1)
        self._hotkey_combo.setCurrentText(self._settings.hotkey)
