from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, QRect, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QGuiApplication, QPainter, QPalette
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from ui.assets.font_manager import FontManager
from ui.assets.icons import IconManager
from ui.themeing.style_sections import compact_bubble_styles
from ui.themeing.theme import THEMES
from ui.widgets.components import ModernInput

_COLLAPSED_SIZE = 56
_EXPANDED_WIDTH = 360
_SCREEN_MARGIN = 24
_ANIM_MS = 150
_FEEDBACK_MS = 1200


class CompactBubble(QWidget):
    """Yuvarlak, her zaman ustte, surunebilir mini pencere.

    Fare uzerine gelince yandan bir URL kutusu acilir; Enter'a basinca
    url_submitted sinyali yayilir (MainWindow bunu _start_download() ile
    aynen isler, ayri bir indirme yolu YOKTUR). Cift tiklama tam pencereye
    donusu ister (restore_requested).
    """

    url_submitted = Signal(str)
    restore_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("compactBubbleFrame")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFont(FontManager.application_font())

        self._theme_name = "dark"
        self._accent_color = QColor(THEMES["dark"]["accent"])
        self._expanded = False
        self._drag_offset: QPoint | None = None
        self._collapsed_pos: QPoint | None = None
        self._last_pos: QPoint | None = None

        layout = QHBoxLayout(self)
        # Sag margin BURADA verilmez: input gizliyken (daraltilmis/yuvarlak
        # halde) layout bu marjini de genislik hesabina katip minimumSize'i
        # sisirir (56 -> 56+margin), yuvarlak yerine oval bir sekil cikardi.
        # Genisken saga bosluk #compactUrlInput QSS padding'inden gelir.
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._icon_label = QLabel(self)
        self._icon_label.setObjectName("compactBubbleIcon")
        self._icon_label.setFixedSize(_COLLAPSED_SIZE, _COLLAPSED_SIZE)
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_label.setPixmap(IconManager.app_icon().pixmap(28, 28))
        # Mouse olaylari iconun altindaki self'e gecsin (surukleme/cift-tik icin);
        # input alani ise interaktif kalir (metin secimiyle celismesin).
        self._icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        self._url_input = ModernInput(placeholder="URL yapıştırın…")
        self._url_input.setObjectName("compactUrlInput")
        self._url_input.setVisible(False)
        self._url_input.returnPressed.connect(self._on_submit)

        layout.addWidget(self._icon_label)
        layout.addWidget(self._url_input, stretch=1)

        self.resize(_COLLAPSED_SIZE, _COLLAPSED_SIZE)

        self._anim = QPropertyAnimation(self, b"geometry")
        self._anim.setDuration(_ANIM_MS)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.finished.connect(self._on_anim_finished)

        self._feedback_timer = QTimer(self)
        self._feedback_timer.setSingleShot(True)
        self._feedback_timer.timeout.connect(self._after_feedback)

        self.apply_theme(self._theme_name)

    # ---- tema ----
    def apply_theme(self, theme_name: str) -> None:
        self._theme_name = theme_name
        t = THEMES.get(theme_name, THEMES["dark"])
        self._accent_color = QColor(t["accent"])
        self.setStyleSheet(compact_bubble_styles(t))
        text_color = QColor(t["text_button"])
        muted = QColor(text_color)
        muted.setAlpha(150)
        palette = self._url_input.palette()
        palette.setColor(QPalette.ColorRole.PlaceholderText, muted)
        palette.setColor(QPalette.ColorRole.Text, text_color)
        self._url_input.setPalette(palette)
        self.update()

    def paintEvent(self, event) -> None:
        # Yuvarlak/hap dolgusu burada elle cizilir (bkz. style_sections.py'deki
        # not): QSS arkaplan doldurma, resize animasyonu sonrasi genisleyen
        # alani boyamiyordu (sag taraf seffaf kaliyordu).
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._accent_color)
        radius = self.height() / 2
        painter.drawRoundedRect(self.rect(), radius, radius)
        super().paintEvent(event)

    # ---- gosterim ----
    def show_at_last_position(self) -> None:
        if self._last_pos is None:
            screen = QGuiApplication.primaryScreen()
            avail = screen.availableGeometry()
            x = avail.right() - _COLLAPSED_SIZE - _SCREEN_MARGIN
            y = avail.bottom() - _COLLAPSED_SIZE - _SCREEN_MARGIN
            self._last_pos = QPoint(x, y)
        self._expanded = False
        self._url_input.setVisible(False)
        self._url_input.clear()
        self.setGeometry(self._last_pos.x(), self._last_pos.y(), _COLLAPSED_SIZE, _COLLAPSED_SIZE)
        self.show()
        self.raise_()

    def hideEvent(self, event) -> None:
        self._last_pos = self._collapsed_pos if self._expanded else self.pos()
        super().hideEvent(event)

    # ---- hover genislet/daralt ----
    def enterEvent(self, event) -> None:
        super().enterEvent(event)
        self._expand()

    def leaveEvent(self, event) -> None:
        super().leaveEvent(event)
        if not self._url_input.text().strip():
            self._collapse()

    def _expand(self) -> None:
        if self._expanded:
            return
        self._expanded = True
        self._collapsed_pos = self.pos()
        self._url_input.setVisible(True)

        screen = QGuiApplication.screenAt(self._collapsed_pos) or QGuiApplication.primaryScreen()
        avail = screen.availableGeometry()
        if self._collapsed_pos.x() + _EXPANDED_WIDTH > avail.right():
            new_x = self._collapsed_pos.x() + _COLLAPSED_SIZE - _EXPANDED_WIDTH
        else:
            new_x = self._collapsed_pos.x()
        target = QRect(new_x, self._collapsed_pos.y(), _EXPANDED_WIDTH, _COLLAPSED_SIZE)
        self._animate_to(target)
        self._url_input.setFocus()

    def _collapse(self) -> None:
        if not self._expanded or self._collapsed_pos is None:
            return
        self._expanded = False
        target = QRect(self._collapsed_pos.x(), self._collapsed_pos.y(), _COLLAPSED_SIZE, _COLLAPSED_SIZE)
        self._animate_to(target)

    def _animate_to(self, rect: QRect) -> None:
        self._anim.stop()
        self._anim.setStartValue(self.geometry())
        self._anim.setEndValue(rect)
        self._anim.start()

    def _on_anim_finished(self) -> None:
        if not self._expanded:
            self._url_input.setVisible(False)
            self._url_input.clear()

    # ---- surukleme (yalnizca ikon alaninda; input WA_TransparentForMouseEvents degil) ----
    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self._drag_offset = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.restore_requested.emit()
        super().mouseDoubleClickEvent(event)

    # ---- url gonderimi ----
    def _on_submit(self) -> None:
        url = self._url_input.text().strip()
        if not url:
            return
        self.url_submitted.emit(url)
        self._show_feedback("Kuyruğa eklendi ✓")

    def _show_feedback(self, text: str) -> None:
        self._url_input.setReadOnly(True)
        self._url_input.setText(text)
        self._feedback_timer.start(_FEEDBACK_MS)

    def _after_feedback(self) -> None:
        self._url_input.setReadOnly(False)
        self._url_input.clear()
        if not self.underMouse():
            self._collapse()
