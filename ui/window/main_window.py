import os
import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFileDialog, QProgressBar, QFrame, QScrollArea, QStackedWidget
)
from PyQt5.QtCore import Qt, pyqtSlot, QUrl
from PyQt5.QtGui import QDesktopServices, QColor

from ui.themeing.styles import StyleManager
from ui.widgets.components import ModernCard, HeaderLabel, ModernButton, ModernInput, SegmentControl
from ui.window.controller import MainWindowController
from ui.assets.icons import IconManager
from ui.window.view_state import DownloadViewState
from core.utils import PlatformHelper
from core.domain import JobStatus


# Platform adı → vurgu rengi (hex)
_PLATFORM_COLORS: dict[str, str] = {
    'YouTube':    '#FF4444',
    'TikTok':     '#69C9D0',
    'Instagram':  '#E1306C',
    'Twitter':    '#1D9BF0',
    'X (Twitter)': '#1D9BF0',
    'Facebook':   '#1877F2',
    'Twitch':     '#9146FF',
    'SoundCloud': '#FF5500',
    'Pinterest':  '#E60023',
    'Web':        '#8B91A7',
}


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bağlantı İndirici")
        self.setWindowIcon(IconManager.app_icon())
        self.setGeometry(200, 80, 620, 720)
        self.setMinimumSize(580, 680)

        self.download_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
        self.controller = MainWindowController(self)
        self.queue_rows = {}
        self.history_rows = {}

        self._init_ui()
        self.setStyleSheet(StyleManager.get_main_stylesheet())
        self.render_history(self.controller.list_history())

    def showEvent(self, event):
        super().showEvent(event)
        self._apply_dark_title_bar()

    def _apply_dark_title_bar(self) -> None:
        if not sys.platform.startswith("win"):
            return
        try:
            import ctypes
            hwnd = int(self.winId())
            value = ctypes.c_int(1)
            for attribute in (20, 19):
                result = ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd,
                    attribute,
                    ctypes.byref(value),
                    ctypes.sizeof(value),
                )
                if result == 0:
                    break
        except Exception:
            pass

    # ------------------------------------------------------------------ #
    #  LAYOUT KURULUMU
    # ------------------------------------------------------------------ #

    def _init_ui(self):
        root = QVBoxLayout()
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(28, 28, 28, 16)
        content_layout.setSpacing(16)

        content_layout.addLayout(self._create_header())
        content_layout.addWidget(self._create_url_card())
        content_layout.addWidget(self._create_settings_card())
        content_layout.addLayout(self._create_action_buttons())
        self.progress_container = self._create_progress_section()
        content_layout.addWidget(self.progress_container)
        content_layout.addWidget(self._create_queue_card())
        content_layout.addStretch()

        scroll = QScrollArea()
        scroll.setObjectName("appScroll")
        scroll.setWidgetResizable(True)
        scroll.setWidget(content_widget)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
            "QWidget#scrollContent { background: transparent; }"
        )
        content_widget.setObjectName("scrollContent")

        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        history_layout.setContentsMargins(28, 28, 28, 16)
        history_layout.setSpacing(16)
        history_layout.addLayout(self._create_history_header())
        history_layout.addWidget(self._create_history_card())
        history_layout.addStretch()

        history_scroll = QScrollArea()
        history_scroll.setObjectName("appScroll")
        history_scroll.setWidgetResizable(True)
        history_scroll.setWidget(history_widget)
        history_scroll.setFrameShape(QFrame.NoFrame)
        history_widget.setObjectName("scrollContent")

        self.page_stack = QStackedWidget()
        self.page_stack.addWidget(scroll)
        self.page_stack.addWidget(history_scroll)

        root.addWidget(self.page_stack)
        root.addWidget(self._create_status_bar())
        self.setLayout(root)

    def _create_header(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(4)
        top_row = QHBoxLayout()
        top_row.setSpacing(8)
        spacer = QWidget()
        spacer.setFixedWidth(88)
        title = HeaderLabel("Bağlantı İndirici")
        title.setAlignment(Qt.AlignCenter)
        self.btn_history_page = ModernButton("Geçmiş", "secondary", self._show_history_page)
        self.btn_history_page.setFixedWidth(88)
        self.btn_history_page.setFixedHeight(38)
        top_row.addWidget(spacer)
        top_row.addWidget(title, stretch=1)
        top_row.addWidget(self.btn_history_page, alignment=Qt.AlignRight | Qt.AlignTop)
        layout.addLayout(top_row)
        layout.addWidget(HeaderLabel("YouTube, TikTok, Instagram ve daha fazlasından içerik indirin", subtitle=True))
        return layout

    def _create_history_header(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(12)
        spacer = QWidget()
        spacer.setFixedWidth(112)
        title = HeaderLabel("Geçmiş")
        title.setAlignment(Qt.AlignCenter)
        btn_back = ModernButton("Ana Sayfa", "secondary", self._show_main_page)
        btn_back.setFixedWidth(112)
        layout.addWidget(spacer)
        layout.addWidget(title, stretch=1)
        layout.addWidget(btn_back, alignment=Qt.AlignRight | Qt.AlignTop)
        return layout

    def _show_history_page(self) -> None:
        self.render_history(self.controller.list_history())
        self.page_stack.setCurrentIndex(1)
        self.set_status("Geçmiş")

    def _show_main_page(self) -> None:
        self.page_stack.setCurrentIndex(0)
        self.set_status("Hazır")

    # -- URL KARTI ---------------------------------------------------- #

    def _create_url_card(self) -> ModernCard:
        card = ModernCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(8)

        # Etiket + platform rozeti satırı
        row = QHBoxLayout()
        lbl = QLabel("BAĞLANTI")
        lbl.setObjectName("formLabel")
        self.platform_badge = QLabel()
        self.platform_badge.setObjectName("platformBadge")
        self.platform_badge.setFixedHeight(20)
        self.platform_badge.hide()
        row.addWidget(lbl)
        row.addStretch()
        row.addWidget(self.platform_badge)
        layout.addLayout(row)

        self.url_input = ModernInput(placeholder="URL yapıştırın…")
        self.url_input.textChanged.connect(self._on_url_changed)
        layout.addWidget(self.url_input)

        self.lbl_url_feedback = QLabel("")
        self.lbl_url_feedback.setObjectName("helperText")
        self.lbl_url_feedback.hide()
        layout.addWidget(self.lbl_url_feedback)

        return card

    # -- AYARLAR KARTI ------------------------------------------------- #

    def _create_settings_card(self) -> ModernCard:
        card = ModernCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(6)

        # Kayıt Konumu
        lbl_path = QLabel("KAYIT KONUMU")
        lbl_path.setObjectName("formLabel")
        layout.addWidget(lbl_path)

        path_row = QHBoxLayout()
        path_row.setSpacing(8)
        self.path_input = ModernInput(self._display_download_dir(), read_only=True)
        btn_select = ModernButton("Seç", "secondary", self._select_directory,
                                  icon=IconManager.get('folder'))
        path_row.addWidget(self.path_input, stretch=1)
        path_row.addWidget(btn_select)
        layout.addLayout(path_row)

        layout.addSpacing(12)

        # Dosya Adı
        lbl_name = QLabel("DOSYA ADI")
        lbl_name.setObjectName("formLabel")
        layout.addWidget(lbl_name)

        self.filename_input = ModernInput("Varsayılan dosya adı kullanılacak")
        layout.addWidget(self.filename_input)

        lbl_helper = QLabel("Boş bırakırsanız orijinal ad kullanılır.")
        lbl_helper.setObjectName("helperText")
        layout.addWidget(lbl_helper)

        layout.addSpacing(12)

        # Format Segment
        lbl_fmt = QLabel("FORMAT")
        lbl_fmt.setObjectName("formLabel")
        layout.addWidget(lbl_fmt)

        self.format_segment = SegmentControl([
            ("Video",      "video"),
            ("Ses (MP3)",  "ses"),
            ("Playlist",   "playlist"),
        ])
        self.format_segment.selectionChanged.connect(self._on_format_changed)
        layout.addWidget(self.format_segment)

        return card

    # -- AKSİYON BUTONLARI --------------------------------------------- #

    def _create_action_buttons(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(12)

        self.btn_download = ModernButton("Kuyruga Ekle", "primary", self._start_download,
                                         icon=IconManager.get('download'))
        self.btn_download.setEnabled(False)  # URL boşken disabled

        self.btn_cancel = ModernButton("İptal", "danger", self._cancel_download,
                                       icon=IconManager.get('cancel'))
        self.btn_cancel.hide()

        layout.addStretch()
        layout.addWidget(self.btn_download)
        layout.addWidget(self.btn_cancel)
        layout.addStretch()
        return layout

    # -- İLERLEME BÖLÜMÜ ----------------------------------------------- #

    def _create_progress_section(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(6)

        # Yüzde satırı
        pct_row = QHBoxLayout()
        self.lbl_progress_title = QLabel("İndiriliyor…")
        self.lbl_progress_title.setObjectName("statusBarText")
        self.lbl_percent = QLabel("")
        self.lbl_percent.setObjectName("statusBarText")
        self.lbl_percent.setAlignment(Qt.AlignRight)
        pct_row.addWidget(self.lbl_progress_title)
        pct_row.addStretch()
        pct_row.addWidget(self.lbl_percent)
        layout.addLayout(pct_row)

        # Progress bar (ince)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        layout.addWidget(self.progress_bar)

        # Hız / kalan süre
        self.lbl_details = QLabel("")
        self.lbl_details.setObjectName("detailLabel")
        self.lbl_details.setAlignment(Qt.AlignCenter)
        self.lbl_details.setWordWrap(True)
        layout.addWidget(self.lbl_details)

        self.success_actions = QWidget()
        success_layout = QHBoxLayout(self.success_actions)
        success_layout.setContentsMargins(0, 8, 0, 0)
        success_layout.setSpacing(10)

        self.btn_show_folder = ModernButton("Klasörde Göster", "primary", self._open_directory,
                                            icon=IconManager.get('folder_open'))
        self.btn_new_download = ModernButton("Yeni İndirme", "secondary", self._prepare_new_download)

        success_layout.addStretch()
        success_layout.addWidget(self.btn_show_folder)
        success_layout.addWidget(self.btn_new_download)
        success_layout.addStretch()

        self.success_actions.hide()
        layout.addWidget(self.success_actions)

        container.hide()
        return container

    def _create_queue_card(self) -> ModernCard:
        card = ModernCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        title_row = QHBoxLayout()
        title = QLabel("AKTIF KUYRUK")
        title.setObjectName("formLabel")
        title_row.addWidget(title)
        title_row.addStretch()
        layout.addLayout(title_row)

        self.queue_list = QWidget()
        self.queue_list_layout = QVBoxLayout(self.queue_list)
        self.queue_list_layout.setContentsMargins(0, 0, 0, 0)
        self.queue_list_layout.setSpacing(8)
        layout.addWidget(self.queue_list)

        self.render_queue([])
        return card

    def _create_history_card(self) -> ModernCard:
        card = ModernCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        title_row = QHBoxLayout()
        title = QLabel("GECMIS")
        title.setObjectName("formLabel")
        btn_clear = ModernButton("Gecmisi Temizle", "secondary", self._clear_history)
        title_row.addWidget(title)
        title_row.addStretch()
        title_row.addWidget(btn_clear)
        layout.addLayout(title_row)

        self.history_list = QWidget()
        self.history_list_layout = QVBoxLayout(self.history_list)
        self.history_list_layout.setContentsMargins(0, 0, 0, 0)
        self.history_list_layout.setSpacing(8)
        layout.addWidget(self.history_list)

        self.render_history([])
        return card

    # -- STATUS BAR ---------------------------------------------------- #

    def _create_status_bar(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("statusBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 0, 16, 0)

        self.lbl_status_bar = QLabel("Hazır")
        self.lbl_status_bar.setObjectName("statusBarText")

        lbl_ver = QLabel("v1.0.0")
        lbl_ver.setObjectName("footerText")

        layout.addWidget(self.lbl_status_bar)
        layout.addStretch()
        layout.addWidget(lbl_ver)
        return bar

    # ------------------------------------------------------------------ #
    #  PLATFORM ALGILAMA
    # ------------------------------------------------------------------ #

    def _detect_platform(self, url: str) -> str:
        platform = PlatformHelper.get_platform_name(url)
        if platform in ("Bilinmeyen", "GecersizURL"):
            return ""
        return platform

    def _update_platform_badge(self, platform: str) -> None:
        if not platform:
            self.platform_badge.hide()
            return
        color = _PLATFORM_COLORS.get(platform, '#8B91A7')
        c = QColor(color)
        bg  = f"rgba({c.red()},{c.green()},{c.blue()},38)"
        bdr = f"rgba({c.red()},{c.green()},{c.blue()},90)"
        self.platform_badge.setStyleSheet(
            f"background-color:{bg}; color:{color}; border:1px solid {bdr};"
            f"border-radius:4px; padding:1px 8px; font-size:11px; font-weight:700;"
        )
        self.platform_badge.setText(platform)
        self.platform_badge.show()

    # ------------------------------------------------------------------ #
    #  KUYRUK VE GECMIS
    # ------------------------------------------------------------------ #

    def render_queue(self, jobs) -> None:
        self._clear_layout(self.queue_list_layout)
        active_jobs = [job for job in jobs if job.status in (JobStatus.QUEUED, JobStatus.RUNNING)]
        if not active_jobs:
            self.queue_list_layout.addWidget(self._empty_label("Kuyrukta is yok."))
            return
        for job in active_jobs:
            self.queue_list_layout.addWidget(self._queue_row(job))

    def upsert_queue_job(self, job) -> None:
        self.render_queue(self.controller.queue_service.active_jobs())
        if job.status == JobStatus.RUNNING:
            self.progress_container.show()
            self.progress_bar.setValue(job.progress_percent)
            self.lbl_percent.setText(f"{job.progress_percent}%")
            self.lbl_details.setText(job.status_message)
            self.lbl_progress_title.setText(job.platform)
        elif not self.controller.queue_service.active_jobs():
            self.progress_container.hide()

    def render_history(self, jobs) -> None:
        if not hasattr(self, "history_list_layout"):
            return
        self._clear_layout(self.history_list_layout)
        finished_jobs = [
            job for job in jobs
            if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED)
        ]
        if not finished_jobs:
            self.history_list_layout.addWidget(self._empty_label("Gecmis kaydi yok."))
            return
        for job in finished_jobs:
            self.history_list_layout.addWidget(self._history_row(job))

    def _queue_row(self, job) -> QFrame:
        row = QFrame()
        row.setObjectName("statusBar")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        text = QLabel(self._history_summary(job))
        text.setObjectName("statusBarText")
        text.setWordWrap(True)
        layout.addWidget(text, stretch=1)

        if job.status in (JobStatus.QUEUED, JobStatus.RUNNING):
            btn_cancel = ModernButton("Iptal", "danger", lambda _, job_id=job.id: self.controller.cancel_download(job_id))
            layout.addWidget(btn_cancel)

        return row

    def _history_row(self, job) -> QFrame:
        row = QFrame()
        row.setObjectName("statusBar")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        text = QLabel(self._job_summary(job))
        text.setObjectName("statusBarText")
        text.setWordWrap(True)
        layout.addWidget(text, stretch=1)

        btn_retry = ModernButton("Tekrar Dene", "secondary", lambda _, job_id=job.id: self.controller.retry_download(job_id))
        layout.addWidget(btn_retry)

        if job.output_path:
            btn_folder = ModernButton(
                "Klasorde Goster",
                "secondary",
                lambda _, path=job.output_path: self._open_path(path),
                icon=IconManager.get('folder_open'),
            )
            layout.addWidget(btn_folder)

        return row

    def _job_summary(self, job) -> str:
        status_labels = {
            JobStatus.QUEUED: "Bekliyor",
            JobStatus.RUNNING: "Indiriliyor",
            JobStatus.COMPLETED: "Tamamlandi",
            JobStatus.FAILED: "Basarisiz",
            JobStatus.CANCELLED: "Iptal",
        }
        filename = self._display_name(job, allow_url=True)
        detail = job.error_message or job.status_message
        return (
            f"{job.platform} - {status_labels.get(job.status, job.status.value)} "
            f"- %{job.progress_percent}\n{filename}\n{detail}"
        )

    def _history_summary(self, job) -> str:
        status_labels = {
            JobStatus.COMPLETED: "Tamamlandi",
            JobStatus.FAILED: "Basarisiz",
            JobStatus.CANCELLED: "Iptal",
        }
        name = self._display_name(job, allow_url=False)
        detail = job.error_message or job.status_message
        return (
            f"{job.platform} - {status_labels.get(job.status, job.status.value)} "
            f"- %{job.progress_percent}\n{name}\n{detail}"
        )

    def _display_name(self, job, allow_url: bool) -> str:
        if job.title and not self._looks_like_url(job.title):
            return job.title
        if job.options.filename:
            return job.options.filename
        if job.output_path and os.path.isfile(job.output_path):
            return os.path.basename(job.output_path)
        if allow_url:
            return job.normalized_url
        return f"{job.platform} indirimi"

    @staticmethod
    def _looks_like_url(value: str) -> bool:
        lowered = (value or "").strip().lower()
        return lowered.startswith(("http://", "https://", "www.", "youtu.be/"))

    def _empty_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("helperText")
        label.setAlignment(Qt.AlignCenter)
        return label

    def _clear_layout(self, layout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    # ------------------------------------------------------------------ #
    #  EVENT HANDLER'LAR
    # ------------------------------------------------------------------ #

    @pyqtSlot(str)
    def _on_url_changed(self, text: str) -> None:
        stripped = text.strip()
        platform = self._detect_platform(stripped) if stripped else ''
        self._update_platform_badge(platform)
        self.url_input.setToolTip(stripped)

        if not stripped:
            self.lbl_url_feedback.hide()
            self._set_ready(False)
            return

        if platform:
            self.lbl_url_feedback.hide()
            self._set_ready(True)
        else:
            self.lbl_url_feedback.setText("Geçerli bir URL yapıştırın.")
            self.lbl_url_feedback.setObjectName("errorText")
            self.lbl_url_feedback.style().unpolish(self.lbl_url_feedback)
            self.lbl_url_feedback.style().polish(self.lbl_url_feedback)
            self.lbl_url_feedback.show()
            self._set_ready(False)

    @pyqtSlot(str)
    def _on_format_changed(self, value: str) -> None:
        is_playlist = (value == 'playlist')
        self.filename_input.setEnabled(not is_playlist)
        if is_playlist:
            self.filename_input.setPlaceholderText("Playlist modunda kullanılamaz")
        else:
            self.filename_input.setPlaceholderText("Varsayılan dosya adı kullanılacak")

    def _select_directory(self) -> None:
        new_dir = QFileDialog.getExistingDirectory(self, "İndirme Dizinini Seç", self.download_dir)
        if new_dir:
            self.download_dir = new_dir
            self.path_input.setText(self._display_download_dir())

    def _open_directory(self) -> None:
        if os.path.exists(self.download_dir):
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.download_dir))

    def _open_path(self, path: str) -> None:
        if path and os.path.exists(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def _clear_history(self) -> None:
        self.controller.clear_history()

    def _display_download_dir(self) -> str:
        home_dir = os.path.normpath(os.path.expanduser("~"))
        download_dir = os.path.normpath(self.download_dir)
        if sys.platform.startswith("win"):
            home_cmp = home_dir.lower()
            dir_cmp = download_dir.lower()
            if dir_cmp == home_cmp or dir_cmp.startswith(home_cmp + os.sep):
                suffix = download_dir[len(home_dir):].lstrip("\\/")
                return os.path.join(r"C:\Users\<user>", suffix) if suffix else r"C:\Users\<user>"
        elif download_dir == home_dir or download_dir.startswith(home_dir + os.sep):
            suffix = download_dir[len(home_dir):].lstrip("/")
            return f"/home/<user>/{suffix}" if suffix else "/home/<user>"
        return download_dir

    # ------------------------------------------------------------------ #
    #  İNDİRME MANTIĞI
    # ------------------------------------------------------------------ #

    def _start_download(self) -> None:
        url = self.url_input.text().strip()
        if not url:
            return

        seg = self.format_segment.value()
        if seg == 'playlist':
            mode = 'video'
            is_playlist = True
        else:
            mode = seg          # 'video' veya 'ses'
            is_playlist = False

        filename = self.filename_input.text().strip() or None

        self.controller.enqueue_download(url, self.download_dir, mode, filename, is_playlist)
        self.url_input.clear()
        self._set_ready(False)

    def _cancel_download(self) -> None:
        active_jobs = self.controller.queue_service.active_jobs()
        if active_jobs:
            self.controller.cancel_download(active_jobs[0].id)

    # -- Sinyal alıcılar ----------------------------------------------- #

    @pyqtSlot(int, str)
    def update_progress(self, percent: int, status_msg: str) -> None:
        self.progress_bar.setValue(percent)
        self.lbl_percent.setText(f"{percent}%")
        self.lbl_details.setText(status_msg)

    @pyqtSlot()
    def handle_finished(self) -> None:
        self.progress_bar.setValue(100)
        self.lbl_percent.setText("100%")
        self.lbl_progress_title.setText("Tamamlandı")
        self.lbl_details.setText("Dosya başarıyla kaydedildi.")
        self.success_actions.show()
        self.set_status("✓  İndirme tamamlandı", error=False)
        self._set_success()

    @pyqtSlot()
    def handle_cancelled(self) -> None:
        self.lbl_progress_title.setText("İptal Edildi")
        self.lbl_percent.setText("")
        self.lbl_details.setText("İşlem kullanıcı tarafından durduruldu.")
        self.set_status("İndirme iptal edildi.", error=True)
        self._render_state(DownloadViewState.CANCELLED)
        self._reset_controls()

    @pyqtSlot(str)
    def handle_error(self, msg: str) -> None:
        self.progress_container.show()
        self.lbl_progress_title.setText("Hata")
        self.lbl_percent.setText("")
        self.lbl_details.setText(msg)
        self.set_status(f"⚠  {msg}", error=True)
        self._render_state(DownloadViewState.ERROR)
        self._reset_controls()

    # -- Yardımcılar --------------------------------------------------- #

    def set_status(self, text: str, error: bool = False) -> None:
        color = "#FF4757" if error else "#00d4ff"
        self.lbl_status_bar.setText(text)
        self.lbl_status_bar.setStyleSheet(
            f"font-size:12px; font-weight:600; color:{color};"
        )

    def _set_ready(self, ready: bool) -> None:
        self._render_state(DownloadViewState.READY if ready else DownloadViewState.IDLE)
        self.btn_download.setEnabled(ready)

    def _is_url_ready(self) -> bool:
        return bool(self._detect_platform(self.url_input.text().strip()))

    def _set_downloading(self) -> None:
        self._render_state(DownloadViewState.DOWNLOADING)

    def _set_success(self) -> None:
        self._render_state(DownloadViewState.SUCCESS)

    def _prepare_new_download(self) -> None:
        self.progress_container.hide()
        self.success_actions.hide()
        self.progress_bar.setValue(0)
        self.lbl_percent.setText("")
        self.lbl_details.setText("")
        self._set_ready(self._is_url_ready())
        self.set_status("Hazır")

    def _reset_controls(self) -> None:
        self._set_ready(self._is_url_ready())

    def _render_state(self, state: DownloadViewState) -> None:
        if state == DownloadViewState.DOWNLOADING:
            self.btn_download.setText("Kuyruga Ekle")
            self.btn_download.setEnabled(False)
            self.btn_download.show()
            self.btn_cancel.setText("İptal")
            self.btn_cancel.setEnabled(True)
            self.btn_cancel.show()
            self.success_actions.hide()
            return

        if state == DownloadViewState.SUCCESS:
            self.btn_download.setText("Kuyruga Ekle")
            self.btn_download.hide()
            self.btn_cancel.hide()
            self.success_actions.show()
            return

        self.btn_download.setText("Kuyruga Ekle")
        self.btn_download.show()
        self.btn_cancel.setText("İptal")
        self.btn_cancel.hide()
        self.success_actions.hide()
