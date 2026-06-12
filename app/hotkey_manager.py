import os
import sys
from PySide6.QtCore import QObject, Signal, QThread


class _HotkeyWorker(QThread):
    triggered = Signal()

    def __init__(self, hotkey, parent=None):
        super().__init__(parent)
        self._running = True
        self._hotkey = hotkey

    def run(self):
        stderr_fd = sys.stderr.fileno()
        with open(os.devnull, "w") as null:
            old_stderr = os.dup(stderr_fd)
            os.dup2(null.fileno(), stderr_fd)
            try:
                import keyboard
            except ImportError:
                os.dup2(old_stderr, stderr_fd)
                os.close(old_stderr)
                return
            try:
                keyboard.add_hotkey(
                    self._hotkey, self._emit, suppress=True, trigger_on_release=False
                )
            except Exception:
                pass
            finally:
                os.dup2(old_stderr, stderr_fd)
                os.close(old_stderr)

        while self._running:
            self.msleep(150)
        try:
            keyboard.remove_all_hotkeys()
        except Exception:
            pass

    def _emit(self):
        self.triggered.emit()

    def stop(self):
        self._running = False


class HotkeyManager(QObject):
    activated = Signal()

    def __init__(self, hotkey="ctrl+shift+v", parent=None):
        super().__init__(parent)
        self._hotkey = hotkey
        self._worker = None

    def set_hotkey(self, hotkey):
        self._hotkey = hotkey
        if self._worker is not None:
            self.stop()
            self.start()

    def start(self):
        if self._worker is not None:
            return
        self._worker = _HotkeyWorker(self._hotkey, self)
        self._worker.triggered.connect(self.activated)
        self._worker.start()

    def stop(self):
        if self._worker is None:
            return
        self._worker.stop()
        self._worker.wait(2000)
        self._worker = None
