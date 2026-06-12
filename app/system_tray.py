from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication

from app._icon import app_icon


class SystemTray(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent)
        icon = app_icon()
        if icon.isNull():
            icon = self._generate_icon()
        self.setIcon(icon)
        self.setToolTip("Clipser")
        self._menu = QMenu()
        self._show_action = QAction("Show / Hide  (Win+V)")
        self._show_action.triggered.connect(self._on_show)
        self._settings_action = QAction("Settings")
        self._exit_action = QAction("Exit")
        self._exit_action.triggered.connect(self._on_exit)
        self._menu.addAction(self._show_action)
        self._menu.addSeparator()
        self._menu.addAction(self._settings_action)
        self._menu.addSeparator()
        self._menu.addAction(self._exit_action)
        self.setContextMenu(self._menu)
        self._toggle_callback = None
        self._settings_callback = None
        self.activated.connect(self._on_activated)

    def set_toggle_callback(self, cb):
        self._toggle_callback = cb

    def set_settings_callback(self, cb):
        self._settings_callback = cb
        if cb:
            self._settings_action.triggered.connect(cb)

    def _on_show(self):
        if self._toggle_callback:
            self._toggle_callback()

    def _on_exit(self):
        QApplication.instance().quit()

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self._toggle_callback:
                self._toggle_callback()

    @staticmethod
    def _generate_icon():
        from PySide6.QtGui import QPixmap, QPainter, QColor, QFont
        from PySide6.QtCore import Qt

        px = QPixmap(64, 64)
        px.fill(Qt.GlobalColor.transparent)
        p = QPainter(px)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor("#6C63FF"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(4, 4, 56, 56, 14, 14)
        p.setPen(QColor("white"))
        font = QFont("Segoe UI", 22, QFont.Weight.Bold)
        p.setFont(font)
        p.drawText(px.rect(), Qt.AlignmentFlag.AlignCenter, "C")
        p.end()
        return QIcon(px)
