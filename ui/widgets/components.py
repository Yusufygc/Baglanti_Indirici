from PyQt5.QtWidgets import QFrame, QGraphicsDropShadowEffect, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QColor, QIcon, QPalette


class ModernCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("modernCard")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(18)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)


class HeaderLabel(QLabel):
    def __init__(self, text, subtitle=False):
        super().__init__(text)
        self.setAlignment(Qt.AlignCenter)
        self.setObjectName("headerSubtitle" if subtitle else "headerTitle")


class ModernButton(QPushButton):
    def __init__(self, text, btn_type="primary", handler=None, icon: QIcon | None = None):
        super().__init__(text)
        self.setCursor(Qt.PointingHandCursor)

        if btn_type == "primary":
            self.setObjectName("primaryButton")
            self.setFixedHeight(48)
            self.setMinimumWidth(150)
        elif btn_type == "danger":
            self.setObjectName("dangerButton")
            self.setFixedHeight(48)
            self.setMinimumWidth(150)
        elif btn_type == "secondary":
            self.setObjectName("secondaryButton")
            self.setMinimumHeight(38)
        elif btn_type == "link":
            self.setObjectName("linkButton")

        if icon and not icon.isNull():
            self.setIcon(icon)
            self.setIconSize(QSize(17, 17))

        if handler:
            self.clicked.connect(handler)


class ModernInput(QLineEdit):
    def __init__(self, placeholder="", read_only=False):
        super().__init__()
        self.setPlaceholderText(placeholder)
        palette = self.palette()
        palette.setColor(QPalette.PlaceholderText, QColor("#D7E6FA"))
        self.setPalette(palette)
        if read_only:
            self.setReadOnly(True)
            self.setObjectName("pathDisplay")
        else:
            self.setObjectName("modernInput")


class SegmentControl(QFrame):
    """
    Segment control — birden fazla seçenekten birini vurgulayarak seçer.
    selectionChanged(str) sinyali seçim değişiminde tetiklenir.
    """
    selectionChanged = pyqtSignal(str)

    def __init__(self, options: list[tuple[str, str]], parent=None):
        """
        options: [(görünür_metin, değer), ...]
        """
        super().__init__(parent)
        self.setObjectName("segmentControl")
        self._buttons: dict[str, QPushButton] = {}
        self._current_value = ""

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        for text, value in options:
            btn = QPushButton(text)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFocusPolicy(Qt.TabFocus)
            btn.setProperty("active", False)
            btn.clicked.connect(lambda _, v=value: self.select(v))
            layout.addWidget(btn)
            self._buttons[value] = btn

        if options:
            self.select(options[0][1], emit=False)

    def select(self, value: str, emit: bool = True) -> None:
        if value == self._current_value:
            return
        for v, btn in self._buttons.items():
            active = (v == value)
            btn.setProperty("active", active)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self._current_value = value
        if emit:
            self.selectionChanged.emit(value)

    def value(self) -> str:
        return self._current_value
