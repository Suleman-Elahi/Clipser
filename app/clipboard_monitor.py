import hashlib
from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtWidgets import QApplication


class ClipboardMonitor(QObject):
    new_clip = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._check)
        self._last_hash = None
        self._suppress = False

    def start(self, interval=400):
        self._timer.start(interval)

    def stop(self):
        self._timer.stop()

    def suppress_next(self):
        self._suppress = True

    def _check(self):
        if self._suppress:
            self._suppress = False
            return
        mime = QApplication.clipboard().mimeData()
        if not mime.hasText():
            return
        text = mime.text()
        if not text or len(text.strip()) == 0:
            return
        h = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()
        if h != self._last_hash:
            self._last_hash = h
            self.new_clip.emit(text)
