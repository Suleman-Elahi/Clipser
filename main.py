import sys
import os
import signal
from PySide6.QtCore import Qt, qInstallMessageHandler, QtMsgType
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QMessageBox

from app.database import ClipDatabase
from app.clipboard_monitor import ClipboardMonitor
from app.hotkey_manager import HotkeyManager
from app.system_tray import SystemTray
from app.settings_manager import SettingsManager
from app.clip_window import ClipWindow
from app.settings_dialog import SettingsDialog


def _filter_qt_warnings(msg_type, context, message):
    if "does not support setting window opacity" in message:
        return


class ClipserApp:
    def __init__(self):
        QFont.insertSubstitution("Segoe UI", "Arial")

        self._app = QApplication(sys.argv)
        self._app.setApplicationName("Clipser")
        self._app.setApplicationDisplayName("Clipser")
        self._app.setQuitOnLastWindowClosed(False)

        qInstallMessageHandler(_filter_qt_warnings)

        self._db = ClipDatabase()
        self._settings = SettingsManager()
        self._monitor = ClipboardMonitor()
        self._hotkey = HotkeyManager(hotkey=self._settings.hotkey)
        self._window = ClipWindow()
        self._apply_stylesheet()

        self._tray = SystemTray()
        self._tray.set_toggle_callback(self._toggle_window)
        self._tray.set_settings_callback(self._show_settings)
        self._tray.show()

        self._monitor.new_clip.connect(self._on_new_clip)
        self._hotkey.activated.connect(self._toggle_window)
        self._window.clip_copied.connect(self._on_clip_copied)
        self._window.clip_pin_toggled.connect(self._on_clip_pin_toggle)
        self._window.clip_deleted.connect(self._on_clip_deleted)
        self._window.clear_requested.connect(self._on_clear_all)
        self._window.settings_requested.connect(self._show_settings)

        self._monitor.start()
        self._hotkey.start()

        self._load_entries()

        self._db.enforce_limit(self._settings.max_entries)

    def _apply_stylesheet(self):
        theme = self._settings.theme
        style_name = "style_light.qss" if theme == "light" else "style.qss"
        style_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "resources", style_name
        )
        if not os.path.exists(style_path):
            style_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "resources", "style.qss"
            )
        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                self._app.setStyleSheet(f.read())
        self._refire_style()

    def _refire_style(self):
        for widget in self._app.topLevelWidgets():
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.repaint()
        self._app.processEvents()

    def _toggle_window(self):
        self._window.toggle_visibility()

    def _on_new_clip(self, text):
        self._db.add_entry(text)
        self._db.enforce_limit(self._settings.max_entries)
        self._load_entries()

    def _on_clip_copied(self, clip_id):
        self._db.add_entry(
            next(
                (
                    w.clip_text
                    for w in self._window._items_widgets
                    if w.clip_id == clip_id
                ),
                "",
            )
        )
        self._db.enforce_limit(self._settings.max_entries)
        self._monitor.suppress_next()
        self._load_entries()

    def _on_clip_pin_toggle(self, clip_id):
        if self._db.toggle_pin(clip_id):
            self._load_entries()

    def _on_clip_deleted(self, clip_id):
        self._db.delete_entry(clip_id)
        self._load_entries()

    def _on_clear_all(self):
        reply = QMessageBox.question(
            self._window,
            "Clear History",
            "Delete all clipboard history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._db.clear_all()
            self._load_entries()

    def _show_settings(self):
        old_theme = self._settings.theme
        old_hotkey = self._settings.hotkey
        dlg = SettingsDialog(self._settings, self._window)
        if dlg.exec() == SettingsDialog.DialogCode.Accepted:
            self._db.enforce_limit(self._settings.max_entries)
            self._window.set_timestamp_visibility(self._settings.show_timestamps)
            if self._settings.theme != old_theme:
                self._apply_stylesheet()
            if self._settings.hotkey != old_hotkey:
                self._hotkey.set_hotkey(self._settings.hotkey)
            self._load_entries()
        if dlg.is_clear_requested():
            self._db.clear_all()
            self._load_entries()
        self._refire_style()

    def _load_entries(self):
        entries = self._db.get_entries(limit=self._settings.max_entries)
        self._window.populate(entries)
        self._window.set_timestamp_visibility(self._settings.show_timestamps)

    def run(self):
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        try:
            sys.exit(self._app.exec())
        finally:
            self._monitor.stop()
            self._hotkey.stop()
            self._db.close()


def main():
    app = ClipserApp()
    app.run()


if __name__ == "__main__":
    main()
