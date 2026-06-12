from datetime import datetime
from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QFont, QFontMetrics, QMouseEvent
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QApplication,
    QSizePolicy,
)


PIN_ICON = "\u25B2"
UNPIN_ICON = "\u25BC"
DEL_ICON = "\u00D7"
PREVIEW_MAX_CHARS = 60


class ClipItem(QFrame):
    copied = Signal(int)
    pin_toggled = Signal(int)
    deleted = Signal(int)

    def __init__(self, clip_id, text, pinned, timestamp, parent=None):
        super().__init__(parent)
        self._clip_id = clip_id
        self._text = text
        self._pinned = bool(pinned)
        self._timestamp = datetime.fromtimestamp(timestamp)

        self.setObjectName("ClipItem")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(52)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 8, 4)
        layout.setSpacing(6)

        left_layout = QVBoxLayout()
        left_layout.setSpacing(2)

        self._text_label = QLabel()
        self._text_label.setFont(QFont("Consolas", 9))
        self._text_label.setTextFormat(Qt.TextFormat.PlainText)
        self._text_label.setWordWrap(False)
        self._text_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self._text_label.setMaximumWidth(9999)
        preview = self._make_preview(text)
        self._text_label.setText(preview)
        left_layout.addWidget(self._text_label)

        self._time_label = QLabel()
        self._time_label.setObjectName("ClipTime")
        self._time_label.setFont(QFont("Segoe UI", 7))
        time_str = self._timestamp.strftime("%H:%M")
        self._time_label.setText(time_str)
        left_layout.addWidget(self._time_label)

        layout.addLayout(left_layout, 1)

        self._pin_btn = QPushButton()
        self._pin_btn.setObjectName("PinButton")
        self._pin_btn.setFixedSize(24, 24)
        self._pin_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self._pin_btn.setText(PIN_ICON)
        self._pin_btn.setToolTip("Pin to top")
        self._pin_btn.clicked.connect(self._on_pin_clicked)
        self._pin_btn.hide()
        layout.addWidget(self._pin_btn)

        self._del_btn = QPushButton()
        self._del_btn.setObjectName("DelButton")
        self._del_btn.setFixedSize(24, 24)
        self._del_btn.setText(DEL_ICON)
        self._del_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self._del_btn.setToolTip("Remove")
        self._del_btn.clicked.connect(self._on_del_clicked)
        self._del_btn.hide()
        layout.addWidget(self._del_btn)

        if self._pinned:
            self._pin_btn.setText(UNPIN_ICON)
            self._pin_btn.setToolTip("Unpin")
            self._pin_btn.show()

        self._set_pinned_style()

    def _make_preview(self, text):
        single_line = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")
        single_line = " ".join(single_line.split())
        if len(single_line) > PREVIEW_MAX_CHARS:
            single_line = single_line[:PREVIEW_MAX_CHARS - 2] + "\u2026"
        return single_line

    def _set_pinned_style(self):
        if self._pinned:
            self.setProperty("pinned", True)
            self.style().unpolish(self)
            self.style().polish(self)
        else:
            self.setProperty("pinned", False)
            self.style().unpolish(self)
            self.style().polish(self)

    def _on_pin_clicked(self):
        self.pin_toggled.emit(self._clip_id)

    def _on_del_clicked(self):
        self.deleted.emit(self._clip_id)

    def event(self, event):
        if event.type() == QEvent.Type.HoverEnter:
            self._pin_btn.show()
            self._del_btn.show()
        elif event.type() == QEvent.Type.HoverLeave:
            if not self._pinned:
                self._pin_btn.hide()
            self._del_btn.hide()
        return super().event(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self._copy()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._copy()
        super().mousePressEvent(event)

    def _copy(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self._text)
        self.copied.emit(self._clip_id)

    @property
    def clip_id(self):
        return self._clip_id

    @property
    def clip_text(self):
        return self._text

    def update_timestamp_visibility(self, visible):
        self._time_label.setVisible(visible)
