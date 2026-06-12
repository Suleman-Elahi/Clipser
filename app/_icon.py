import os
import sys

from PySide6.QtGui import QIcon


def app_icon():
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, "media", "clipser.png")
    if os.path.exists(path):
        return QIcon(path)
    return QIcon()
