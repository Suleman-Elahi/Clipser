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
    QGridLayout,
    QGraphicsDropShadowEffect,
    QApplication,
)
import sys

from app._icon import app_icon


EMOJI_CATEGORIES = {
    "Smileys": [
        "\U0001F600", "\U0001F601", "\U0001F602", "\U0001F923", "\U0001F603",
        "\U0001F604", "\U0001F605", "\U0001F606", "\U0001F607", "\U0001F608",
        "\U0001F609", "\U0001F60A", "\U0001F60B", "\U0001F60C", "\U0001F60D",
        "\U0001F970", "\U0001F60E", "\U0001F913", "\U0001F9D0", "\U0001F60F",
        "\U0001F612", "\U0001F61E", "\U0001F614", "\U0001F61F", "\U0001F615",
        "\U0001F641", "\u2639\uFE0F", "\U0001F623", "\U0001F616", "\U0001F62B",
        "\U0001F629", "\U0001F97A", "\U0001F622", "\U0001F62D", "\U0001F624",
        "\U0001F620", "\U0001F621", "\U0001F92C", "\U0001F92F", "\U0001F633",
        "\U0001F975", "\U0001F976", "\U0001F631", "\U0001F628", "\U0001F630",
        "\U0001F625", "\U0001F613", "\U0001F917", "\U0001F914", "\U0001F92D",
        "\U0001F92B", "\U0001F925", "\U0001F636", "\U0001F610", "\U0001F611",
        "\U0001F62C", "\U0001F644", "\U0001F62F", "\U0001F626", "\U0001F627",
        "\U0001F62E", "\U0001F632", "\U0001F971", "\U0001F634", "\U0001F924",
        "\U0001F62A", "\U0001F635", "\U0001F910", "\U0001F974", "\U0001F922",
        "\U0001F92E", "\U0001F927", "\U0001F637", "\U0001F912", "\U0001F915",
    ],
    "Gestures": [
        "\U0001F44B", "\U0001F91A", "\U0001F590\uFE0F", "\u270B", "\U0001F596",
        "\U0001F44C", "\U0001F90C", "\U0001F90F", "\u270C\uFE0F", "\U0001F91E",
        "\U0001F91F", "\U0001F918", "\U0001F919", "\U0001F448", "\U0001F449",
        "\U0001F446", "\U0001F595", "\U0001F447", "\u261D\uFE0F", "\U0001F44D",
        "\U0001F44E", "\u270A", "\U0001F44A", "\U0001F91B", "\U0001F91C",
        "\U0001F44F", "\U0001F64C", "\U0001F450", "\U0001F932", "\U0001F91D",
        "\U0001F64F", "\u270D\uFE0F", "\U0001F485", "\U0001F933", "\U0001F4AA",
        "\U0001F9BE", "\U0001F9BF", "\U0001F9B5", "\U0001F9B6",
    ],
    "Animals": [
        "\U0001F436", "\U0001F431", "\U0001F42D", "\U0001F439", "\U0001F430",
        "\U0001F98A", "\U0001F43B", "\U0001F43C", "\U0001F43B\u200D\u2744\uFE0F",
        "\U0001F428", "\U0001F42F", "\U0001F981", "\U0001F42E", "\U0001F437",
        "\U0001F438", "\U0001F435", "\U0001F648", "\U0001F649", "\U0001F64A",
        "\U0001F414", "\U0001F427", "\U0001F426", "\U0001F424", "\U0001F986",
        "\U0001F985", "\U0001F989", "\U0001F987", "\U0001F43A", "\U0001F417",
        "\U0001F434", "\U0001F984", "\U0001F41D", "\U0001FAB1", "\U0001F41B",
        "\U0001F98B", "\U0001F40C", "\U0001F41E", "\U0001F41C", "\U0001FAB2",
        "\U0001F99F", "\U0001F997", "\U0001FAB0", "\U0001F982", "\U0001F422",
        "\U0001F40D", "\U0001F98E", "\U0001F996", "\U0001F995", "\U0001F40A",
        "\U0001F438", "\U0001F993", "\U0001F98D", "\U0001F9A7", "\U0001F9A3",
        "\U0001F418", "\U0001F99B", "\U0001F98F", "\U0001F42A", "\U0001F42B",
        "\U0001F992", "\U0001F998", "\U0001F9AC", "\U0001F403", "\U0001F402",
        "\U0001F404", "\U0001F40E", "\U0001F416", "\U0001F40F", "\U0001F411",
        "\U0001F999", "\U0001F410", "\U0001F98C", "\U0001F415", "\U0001F429",
        "\U0001F9AE", "\U0001F415\u200D\u0001F9BA", "\U0001F408", "\U0001F408\u200D\u2B1B",
        "\U0001F413", "\U0001F983",
    ],
    "Food": [
        "\U0001F34E", "\U0001F34A", "\U0001F34B", "\U0001F347", "\U0001F353",
        "\U0001FAD0", "\U0001F348", "\U0001F352", "\U0001F351", "\U0001F96D",
        "\U0001F34D", "\U0001F965", "\U0001F95D", "\U0001F345", "\U0001F346",
        "\U0001F951", "\U0001FAD1", "\U0001F966", "\U0001F96C", "\U0001F952",
        "\U0001F33D", "\U0001F955", "\U0001F9C4", "\U0001F9C5", "\U0001F954",
        "\U0001F360", "\U0001F9C7", "\U0001F95E", "\U0001F9C8", "\U0001F373",
        "\U0001F95A", "\U0001F9C0", "\U0001F957", "\U0001F959", "\U0001F32E",
        "\U0001F32F", "\U0001F96A", "\U0001F355", "\U0001F354", "\U0001F35F",
        "\U0001F32D", "\U0001F37F", "\U0001F366", "\U0001F367", "\U0001F368",
        "\U0001F369", "\U0001F36A", "\U0001F382", "\U0001F370", "\U0001F9C1",
        "\U0001F36B", "\U0001F36C", "\U0001F36D", "\u2615", "\U0001F375",
        "\U0001F9C3", "\U0001F964", "\U0001F9CB", "\U0001F37A", "\U0001F37B",
    ],
    "Objects": [
        "\u231A", "\U0001F4F1", "\U0001F4BB", "\u2328\uFE0F", "\U0001F5A5\uFE0F",
        "\U0001F5A8\uFE0F", "\U0001F5B1\uFE0F", "\U0001F4F7", "\U0001F4F8", "\U0001F4F9",
        "\U0001F3A5", "\U0001F4DE", "\u260E\uFE0F", "\U0001F4DF", "\U0001F4E0",
        "\U0001F4FA", "\U0001F4FB", "\U0001F9ED", "\u23F1\uFE0F", "\u23F0",
        "\U0001F4E1", "\U0001F50B", "\U0001F50C", "\U0001F4A1", "\U0001F526",
        "\U0001F56F\uFE0F", "\U0001FA94", "\U0001F9EF", "\U0001F6E2\uFE0F", "\U0001F4B0",
        "\U0001F4B3", "\U0001FA99", "\U0001F48E", "\u2696\uFE0F", "\U0001F527",
        "\U0001F528", "\u2692\uFE0F", "\U0001F6E0\uFE0F", "\U0001F529", "\u2699\uFE0F",
        "\U0001F517", "\u26D3\uFE0F", "\U0001F9F2", "\U0001F52B", "\U0001F4A3",
        "\U0001FA93", "\U0001F52A", "\U0001F5E1\uFE0F", "\u2694\uFE0F", "\U0001F6E1\uFE0F",
        "\U0001F6AA", "\U0001FA9E", "\U0001FA9F", "\U0001F6CB\uFE0F", "\U0001FA91",
        "\U0001F6BD", "\U0001F9FB", "\U0001F6BF", "\U0001F6C1",
    ],
    "Symbols": [
        "\u2764\uFE0F", "\U0001F9E1", "\U0001F49B", "\U0001F49A", "\U0001F499",
        "\U0001F49C", "\U0001F5A4", "\U0001F90D", "\U0001F90E", "\U0001F494",
        "\u2763\uFE0F", "\U0001F495", "\U0001F49E", "\U0001F493", "\U0001F497",
        "\U0001F496", "\U0001F498", "\U0001F49D", "\u2728", "\u2B50",
        "\U0001F31F", "\U0001F4AB", "\u26A1", "\U0001F308", "\U0001F525",
        "\U0001F4A7", "\u2744\uFE0F", "\U0001F30A", "\U0001F4A5", "\U0001F389",
        "\U0001F38A", "\U0001F388", "\U0001F381", "\U0001F3C6", "\U0001F947",
        "\U0001F948", "\U0001F949", "\U0001F3AF", "\U0001F3AE", "\U0001F3B2",
        "\u2660\uFE0F", "\u2665\uFE0F", "\u2666\uFE0F", "\u2663\uFE0F", "\U0001F0CF",
        "\U0001F004", "\u265F\uFE0F", "\u2705", "\u274C", "\u2B55",
        "\U0001F534", "\U0001F7E0", "\U0001F7E1", "\U0001F7E2", "\U0001F535",
        "\U0001F7E3", "\u26AB", "\u26AA", "\U0001F7E4",
    ],
}

CATEGORY_ICONS = {
    "Smileys": "\U0001F600",
    "Gestures": "\U0001F44D",
    "Animals": "\U0001F431",
    "Food": "\U0001F355",
    "Objects": "\U0001F4BB",
    "Symbols": "\u2764\uFE0F",
}

COLS = 8


class EmojiPanel(QWidget):
    emoji_selected = Signal(str)
    close_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Clipser - Emoji")
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

        self._no_opacity = sys.platform.startswith("linux")
        self._anim = None
        self._current_category = list(EMOJI_CATEGORIES.keys())[0]
        self._cat_buttons = {}

        layout.addWidget(self._build_header())
        layout.addWidget(self._build_category_tabs())
        layout.addWidget(self._build_search_bar())
        layout.addWidget(self._build_emoji_grid(), 1)
        self._cat_buttons = {}

    def _build_header(self):
        frame = QFrame()
        frame.setObjectName("HeaderFrame")
        frame.setFixedHeight(42)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 6, 8, 6)

        back_btn = QPushButton()
        back_btn.setObjectName("EmojiBackButton")
        back_btn.setFixedSize(26, 26)
        back_btn.setText("\u2190")
        back_btn.setToolTip("Back to clipboard")
        back_btn.clicked.connect(self.close_requested.emit)
        layout.addWidget(back_btn)

        title = QLabel("Emoji Panel")
        title.setObjectName("EmojiTitle")
        title.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        layout.addWidget(title)
        layout.addStretch()

        return frame

    def _build_category_tabs(self):
        frame = QFrame()
        frame.setObjectName("CategoryTabsFrame")
        frame.setFixedHeight(42)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)

        for i, (cat_name, icon) in enumerate(CATEGORY_ICONS.items()):
            btn = QPushButton()
            btn.setObjectName("CategoryTab")
            btn.setText(f"{icon}  {cat_name}")
            btn.setFont(QFont("Segoe UI", 8))
            btn.setFixedHeight(30)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, c=cat_name: self._on_category(c))
            layout.addWidget(btn)
            self._cat_buttons[cat_name] = btn

        layout.addStretch()
        return frame

    def _build_search_bar(self):
        frame = QFrame()
        frame.setObjectName("EmojiSearchFrame")
        frame.setFixedHeight(38)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 3, 12, 3)

        self._search_input = QLineEdit()
        self._search_input.setObjectName("SearchInput")
        self._search_input.setPlaceholderText("Search emoji...")
        self._search_input.setFont(QFont("Segoe UI", 9))
        self._search_input.setClearButtonEnabled(True)

        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(100)
        self._search_timer.timeout.connect(self._apply_filters)
        self._search_input.textChanged.connect(lambda: self._search_timer.start())

        layout.addWidget(self._search_input)
        return frame

    def _build_emoji_grid(self):
        self._grid_scroll = QScrollArea()
        self._grid_scroll.setObjectName("ClipScroll")
        self._grid_scroll.setWidgetResizable(True)
        self._grid_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._grid_scroll.setFrameShape(QFrame.Shape.NoFrame)

        self._grid_widget = QWidget()
        self._grid_widget.setObjectName("ClipList")
        self._grid_layout = QGridLayout(self._grid_widget)
        self._grid_layout.setContentsMargins(8, 6, 8, 6)
        self._grid_layout.setSpacing(2)
        self._grid_scroll.setWidget(self._grid_widget)

        return self._grid_scroll

    def _on_category(self, category):
        for name, btn in self._cat_buttons.items():
            btn.setProperty("active", name == category)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self._current_category = category
        self._search_input.clear()
        self._populate_grid(EMOJI_CATEGORIES[category])

    def _apply_filters(self):
        query = self._search_input.text().strip()
        emojis = EMOJI_CATEGORIES.get(self._current_category, [])
        if query:
            emojis = [e for e in emojis if query in e]
        self._populate_grid(emojis)

    def _populate_grid(self, emojis):
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for i, emoji in enumerate(emojis):
            btn = QPushButton()
            btn.setObjectName("EmojiItem")
            btn.setFixedSize(38, 38)
            btn.setFont(QFont("Segoe UI Emoji", 13))
            btn.setText(emoji)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setToolTip(emoji)
            btn.clicked.connect(lambda checked, e=emoji: self.emoji_selected.emit(e))
            row, col = divmod(i, COLS)
            self._grid_layout.addWidget(btn, row, col)

    def show_panel(self, pos):
        self.move(pos)
        self._current_category = list(EMOJI_CATEGORIES.keys())[0]
        for name, btn in self._cat_buttons.items():
            btn.setProperty("active", name == self._current_category)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self._search_input.clear()
        self._populate_grid(EMOJI_CATEGORIES[self._current_category])
        self._animate_in()

    def hide_panel(self):
        if self._no_opacity:
            self.hide()
            return
        if self._anim:
            self._anim.stop()
        self._anim = None
        self.hide()

    def _animate_in(self):
        if self._no_opacity:
            self.show()
            self.raise_()
            self.activateWindow()
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

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.close_requested.emit()
        else:
            super().keyPressEvent(event)
