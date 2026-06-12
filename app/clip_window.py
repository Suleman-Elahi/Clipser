from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QKeyEvent, QColor
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QScrollArea,
    QLabel,
    QPushButton,
    QFrame,
    QGraphicsDropShadowEffect,
    QApplication,
)
import sys

from app.clip_item import ClipItem
from app.emoji_panel import EmojiPanel
from app._icon import app_icon


class ClipWindow(QWidget):
    clip_copied = Signal(int)
    clip_pin_toggled = Signal(int)
    clip_deleted = Signal(int)
    clear_requested = Signal()
    settings_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Clipser")
        self.setWindowIcon(app_icon())
        self.setFixedSize(412, 524)
        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)

        self._container = QFrame(self)
        self._container.setObjectName("WindowContainer")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 28)
        outer.addWidget(self._container)

        layout = QVBoxLayout(self._container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = self._build_header()
        layout.addWidget(header)

        self._scroll = QScrollArea()
        self._scroll.setObjectName("ClipScroll")
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)

        self._list_widget = QWidget()
        self._list_widget.setObjectName("ClipList")
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(6, 4, 6, 4)
        self._list_layout.setSpacing(2)
        self._list_layout.addStretch()
        self._scroll.setWidget(self._list_widget)

        layout.addWidget(self._scroll, 1)

        footer = self._build_footer()
        layout.addWidget(footer)

        self._items_widgets = []
        self._show_timestamps = True
        self._anim = None
        self._no_opacity = sys.platform.startswith("linux")

        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._apply_search)

        self._emoji_panel = EmojiPanel()
        self._emoji_panel.emoji_selected.connect(self._on_emoji_copied)
        self._emoji_panel.close_requested.connect(self._on_emoji_panel_close)

    def _build_header(self):
        frame = QFrame()
        frame.setObjectName("HeaderFrame")
        frame.setFixedHeight(42)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 6, 8, 6)

        self._search_input = QLineEdit()
        self._search_input.setObjectName("SearchInput")
        self._search_input.setPlaceholderText("Search clipboard...")
        self._search_input.setFont(QFont("Segoe UI", 9))
        self._search_input.setClearButtonEnabled(True)
        self._search_input.textChanged.connect(self._on_search_changed)
        layout.addWidget(self._search_input)

        self._emoji_btn = QPushButton()
        self._emoji_btn.setObjectName("EmojiButton")
        self._emoji_btn.setFixedSize(26, 26)
        self._emoji_btn.setText("\U0001F60A")
        self._emoji_btn.setToolTip("Emoji Panel")
        self._emoji_btn.clicked.connect(self._toggle_emoji_panel)
        layout.addWidget(self._emoji_btn)

        self._settings_btn = QPushButton()
        self._settings_btn.setObjectName("SettingsButton")
        self._settings_btn.setFixedSize(26, 26)
        self._settings_btn.setText("\u2699")
        self._settings_btn.setToolTip("Settings")
        self._settings_btn.clicked.connect(self.settings_requested.emit)
        layout.addWidget(self._settings_btn)

        return frame

    def _build_footer(self):
        frame = QFrame()
        frame.setObjectName("FooterFrame")
        frame.setFixedHeight(28)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 2, 12, 2)

        self._count_label = QLabel("0 items")
        self._count_label.setObjectName("FooterLabel")
        self._count_label.setFont(QFont("Segoe UI", 7))
        layout.addWidget(self._count_label)

        layout.addStretch()

        clear_btn = QPushButton("Clear All")
        clear_btn.setObjectName("FooterClearBtn")
        clear_btn.setFont(QFont("Segoe UI", 7))
        clear_btn.setFixedHeight(20)
        clear_btn.clicked.connect(self.clear_requested.emit)
        layout.addWidget(clear_btn)

        return frame

    def populate(self, entries):
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._items_widgets.clear()

        pinned_entries = [e for e in entries if e[2]]
        unpinned_entries = [e for e in entries if not e[2]]

        if pinned_entries:
            for i, entry in enumerate(pinned_entries):
                self._add_item_widget(entry, is_pinned_area=True)

            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setObjectName("PinSeparator")
            separator.setFixedHeight(1)
            idx = self._list_layout.count() - 1
            self._list_layout.insertWidget(idx, separator)

        for entry in unpinned_entries:
            self._add_item_widget(entry, is_pinned_area=False)

        self._update_count()

    def _add_item_widget(self, entry, is_pinned_area=False):
        clip_id, text, pinned, ts = entry
        widget = ClipItem(clip_id, text, bool(pinned), ts)
        widget.copied.connect(self.clip_copied.emit)
        widget.pin_toggled.connect(self.clip_pin_toggled.emit)
        widget.deleted.connect(self.clip_deleted.emit)
        widget.update_timestamp_visibility(self._show_timestamps)
        self._items_widgets.append(widget)
        idx = self._list_layout.count() - 1
        self._list_layout.insertWidget(idx, widget)

    def _update_count(self):
        visible = sum(1 for w in self._items_widgets if w.isVisible())
        self._count_label.setText(f"{visible} items")

    def _on_search_changed(self, text):
        self._search_timer.start(150)

    def _apply_search(self):
        query = self._search_input.text().lower().strip()
        for widget in self._items_widgets:
            if not query:
                widget.setVisible(True)
            else:
                widget.setVisible(query in widget.clip_text.lower())
        self._update_count()

    def set_timestamp_visibility(self, visible):
        self._show_timestamps = visible
        for widget in self._items_widgets:
            widget.update_timestamp_visibility(visible)

    def show_at_center(self):
        screen = QApplication.primaryScreen()
        if screen:
            center = screen.geometry().center()
            self.move(center.x() - self.width() // 2, center.y() - self.height() // 2)
        self._animate_in()

    def _animate_in(self):
        if self._no_opacity:
            self.show()
            self.raise_()
            self.activateWindow()
            self._search_input.setFocus()
            self._search_input.clear()
            return

        if self._anim:
            self._anim.stop()
        self.setWindowOpacity(0.0)
        self.show()
        self._anim = QPropertyAnimation(self, b"windowOpacity")
        self._anim.setDuration(120)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.start()
        self.raise_()
        self.activateWindow()
        self._search_input.setFocus()
        self._search_input.clear()

    def hide_with_anim(self):
        if self._no_opacity:
            self.hide()
            return

        if self._anim:
            self._anim.stop()
        self._anim = QPropertyAnimation(self, b"windowOpacity")
        self._anim.setDuration(80)
        self._anim.setStartValue(self.windowOpacity())
        self._anim.setEndValue(0.0)
        self._anim.setEasingCurve(QEasingCurve.Type.InCubic)
        self._anim.finished.connect(self.hide)
        self._anim.start()

    def toggle_visibility(self):
        if self.isVisible():
            self.hide_with_anim()
        else:
            self.show_at_center()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.hide_with_anim()
        else:
            super().keyPressEvent(event)

    def changeEvent(self, event):
        if event.type() == event.Type.ActivationChange:
            if not self.isActiveWindow():
                self.hide_with_anim()
        super().changeEvent(event)

    def _toggle_emoji_panel(self):
        if self._emoji_panel.isVisible():
            self._emoji_panel.hide_panel()
        else:
            self.hide_with_anim()
            pos = self.pos()
            self._emoji_panel.show_panel(pos)

    def _on_emoji_copied(self, emoji):
        QApplication.clipboard().setText(emoji)
        self._emoji_panel.hide_panel()
        self.show_at_center()

    def _on_emoji_panel_close(self):
        self._emoji_panel.hide_panel()
        self.show_at_center()
