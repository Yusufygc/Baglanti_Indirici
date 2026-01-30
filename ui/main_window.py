import sys
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFileDialog, QProgressBar, 
                             QRadioButton, QButtonGroup, QFrame)
from PyQt5.QtCore import Qt, pyqtSlot, QUrl
from PyQt5.QtGui import QDesktopServices, QIcon

# Modüler importlar
from ui.styles import StyleManager
from ui.components import ModernCard, HeaderLabel, ModernButton, ModernInput
from core.worker import DownloadWorker

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bağlantı İndirici")
        self.setWindowIcon(QIcon("icons/icon.ico"))
        self.setGeometry(200, 100, 650, 735)
        self.setMinimumSize(600, 725)

        # Durum Değişkenleri
        self.download_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
        self.worker = None

        # Arayüzü Kur
        self._init_ui()
        
        # Stilleri Uygula
        self.setStyleSheet(StyleManager.get_main_stylesheet())

    def _init_ui(self):
        """UI bileşenlerini oluşturur ve yerleştirir."""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(0, 0, 0, 0) # Ana layout marginsiz, padding'i içerde vereceğiz.

        # Ana Layout (Scroll Area İçinde Olacak)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 10)
        content_layout.setSpacing(15) # Spacing biraz azaltıldı

        # 1. Başlık Alanı
        header_layout = QVBoxLayout()
        header_layout.addWidget(HeaderLabel("🔗 Bağlantı İndirici"))
        header_layout.addWidget(HeaderLabel("YouTube, TikTok, Instagram ve daha fazlasından içerik indirin", subtitle=True))
        content_layout.addLayout(header_layout)

        # 2. URL Giriş Alanı
        self.url_card = self._create_url_section()
        content_layout.addWidget(self.url_card)

        # 3. Ayarlar Alanı (Dizin + Dosya Adı + Format)
        self.settings_card = self._create_settings_section()
        content_layout.addWidget(self.settings_card)

        # 4. Aksiyon Butonları
        self.btn_layout = self._create_action_buttons()
        content_layout.addLayout(self.btn_layout)

        # 5. İlerleme Alanı (Minimalist)
        self.progress_container = self._create_progress_section()
        content_layout.addWidget(self.progress_container)
        
        content_layout.addStretch() # İçeriği yukarı iter

        # Scroll Area Ekleme (Taşmaları Önlemek İçin)
        from PyQt5.QtWidgets import QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)
        scroll_area.setFrameShape(QFrame.NoFrame) # Kenarlık yok
        
        # Scroll Area arka plan stilini düzelt (CSS ile çakışmaması için)
        # StyleManager'da QScrollArea için transparent background verebiliriz ama burada inline verelim garanti olsun
        scroll_area.setStyleSheet("QScrollArea { background-color: transparent; border: none; } QWidget#scrollContent { background-color: transparent; }")
        content_widget.setObjectName("scrollContent") # CSS seçicisi için ID

        main_layout.addWidget(scroll_area)

        # 6. Status Bar (En Altta)
        self.status_bar = self._create_status_bar()
        main_layout.addWidget(self.status_bar)

        self.setLayout(main_layout)

    def _create_url_section(self):
        card = ModernCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header = QLabel("🌐 Bağlantı")
        header.setObjectName("cardHeader")
        
        self.url_input = ModernInput(placeholder="İndirmek istediğiniz bağlantıyı yapıştırın...")
        
        layout.addWidget(header)
        layout.addWidget(self.url_input)
        return card

    def _create_settings_section(self):
        card = ModernCard()
        layout = QVBoxLayout(card)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Başlık
        header = QLabel("⚙️ Ayarlar")
        header.setObjectName("cardHeader")
        layout.addWidget(header)
        
        # Dizin Seçici
        dizin_layout = QHBoxLayout()
        self.path_input = ModernInput(self.download_dir, read_only=True)
        
        btn_select = ModernButton("📁 Seç", "secondary", self._select_directory)
        btn_open = ModernButton("📂 Aç", "secondary", self._open_directory)

        dizin_layout.addWidget(self.path_input, stretch=1)
        dizin_layout.addWidget(btn_select)
        dizin_layout.addWidget(btn_open)
        layout.addLayout(dizin_layout)

        # Dosya Adı
        name_layout = QHBoxLayout()
        lbl_name = QLabel("📝 Dosya Adı:")
        lbl_name.setObjectName("inputLabel")
        self.filename_input = ModernInput("Orijinal isim için boş bırakın...")
        
        name_layout.addWidget(lbl_name)
        name_layout.addWidget(self.filename_input, stretch=1)
        layout.addLayout(name_layout)

        # Format Seçimi
        fmt_layout = QHBoxLayout()
        lbl_fmt = QLabel("🎬 Format:")
        lbl_fmt.setObjectName("inputLabel")
        
        self.rb_video = QRadioButton("🎥 Video")
        self.rb_video.setChecked(True)
        self.rb_video.setCursor(Qt.PointingHandCursor)
        
        self.rb_audio = QRadioButton("🎵 Ses (MP3)")
        self.rb_audio.setCursor(Qt.PointingHandCursor)
        
        self.fmt_group = QButtonGroup()
        self.fmt_group.addButton(self.rb_video)
        self.fmt_group.addButton(self.rb_audio)
        
        fmt_layout.addWidget(lbl_fmt)
        fmt_layout.addWidget(self.rb_video)
        fmt_layout.addWidget(self.rb_audio)
        fmt_layout.addStretch()
        layout.addLayout(fmt_layout)

        return card

    def _create_action_buttons(self):
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        self.btn_download = ModernButton("⬇️ İndir", "primary", self._start_download)
        self.btn_cancel = ModernButton("❌ İptal", "danger", self._cancel_download)
        self.btn_cancel.setEnabled(False)
        
        layout.addStretch()
        layout.addWidget(self.btn_download)
        layout.addWidget(self.btn_cancel)
        layout.addStretch()
        return layout

    def _create_progress_section(self):
        """İlerleme çubuğunu içeren minimal container."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 10, 0, 5)
        
        # Etiket ve Yüzde
        info_layout = QHBoxLayout()
        self.lbl_status = QLabel("Hazır") # İşlem durumu mesajı
        self.lbl_status.setObjectName("statusLabel")
        self.lbl_percent = QLabel("") # %45
        self.lbl_percent.setObjectName("statusLabel")
        
        info_layout.addWidget(self.lbl_status)
        info_layout.addStretch()
        info_layout.addWidget(self.lbl_percent)
        
        layout.addLayout(info_layout)
        
        # Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False) # Metin yukarıda
        self.progress_bar.setFixedHeight(6) # İnce bar
        
        layout.addWidget(self.progress_bar)
        
        # Detaylar (Hız, Süre) - Barın altında
        self.lbl_details = QLabel("")
        self.lbl_details.setObjectName("detailLabel")
        self.lbl_details.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_details)
        
        container.hide() # Başlangıçta gizli
        return container

    def _create_status_bar(self):
        """Footer yerine geçen status bar."""
        container = QFrame()
        container.setObjectName("statusBar")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(15, 8, 15, 8)
        
        lbl_info = QLabel("v1.0.0 • Yüksek Performanslı İndirici")
        lbl_info.setObjectName("footerText")
        
        layout.addWidget(lbl_info)
        layout.addStretch()
        
        return container

    # --- İŞ MANTIĞI VE EVENT HANDLERLAR ---

    def _update_status(self, message, is_error=False):
        """Durum metnini günceller."""
        self.lbl_status.setText(message)
        if is_error:
            self.lbl_status.setStyleSheet("color: #ff4757; font-weight: bold;")
        else:
            self.lbl_status.setStyleSheet("color: #00d4ff; font-weight: bold;")

    def _select_directory(self):
        new_dir = QFileDialog.getExistingDirectory(self, "İndirme Dizinini Seç", self.download_dir)
        if new_dir:
            self.download_dir = new_dir
            self.path_input.setText(self.download_dir)

    def _open_directory(self):
        if os.path.exists(self.download_dir):
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.download_dir))

    def _start_download(self):
        url = self.url_input.text().strip()
        if not url:
            self.progress_container.show()
            self._update_status("⚠️ Lütfen geçerli bir URL girin!", is_error=True)
            return

        self.btn_download.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        
        # UI Hazırla
        self.progress_container.show()
        self.progress_bar.setValue(0)
        self.lbl_percent.setText("%0")
        self.lbl_details.setText("Hazırlanıyor...")
        self._update_status("Bağlantı analizi yapılıyor...", is_error=False)

        mode = "video" if self.rb_video.isChecked() else "ses"
        filename = self.filename_input.text().strip() or None

        # Thread Başlatma
        self.worker = DownloadWorker(url, self.download_dir, mode, filename)
        
        # Sinyal Bağlantıları
        self.worker.signals.platform_detected.connect(lambda p: self._update_status(f"Platform: {p}"))
        self.worker.signals.folder_prepared.connect(lambda _: None) # Klasör bilgisi kullanıcıyı yormasın
        self.worker.signals.started.connect(lambda m: self._update_status(m))
        self.worker.signals.progress.connect(self._update_progress)
        self.worker.signals.finished.connect(self._on_finished)
        self.worker.signals.cancelled.connect(self._on_cancelled)
        self.worker.signals.error.connect(self._on_error)
        
        self.worker.start()

    def _cancel_download(self):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self._update_status("🛑 İptal ediliyor...", is_error=True)

    @pyqtSlot(int, str)
    def _update_progress(self, percent, status_msg):
        self.progress_bar.setValue(percent)
        self.lbl_percent.setText(f"%{percent}")
        self.lbl_details.setText(status_msg)
        
        if percent < 100:
             self.lbl_status.setText("İndiriliyor...")
             self.lbl_status.setStyleSheet("color: #00d4ff; font-weight: bold;")

    @pyqtSlot()
    def _on_finished(self):
        self.progress_bar.setValue(100)
        self.lbl_percent.setText("%100")
        self._update_status("✅ İndirme Tamamlandı!")
        self.lbl_details.setText("Dosya klasöre kaydedildi.")
        self._reset_ui_state()

    @pyqtSlot()
    def _on_cancelled(self):
        self._update_status("⛔ İndirme İptal Edildi", is_error=True)
        self.lbl_details.setText("")
        self._reset_ui_state()

    @pyqtSlot(str)
    def _on_error(self, err_msg):
        self.progress_container.show() # Hata oluşursa göster
        self._update_status(f"Hata: {err_msg}", is_error=True)
        self._reset_ui_state()

    def _reset_ui_state(self):
        self.btn_download.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.worker = None
        self.url_input.clear()
        self.filename_input.clear()
        # Bar gizlenmiyor, kullanıcı sonucu görsün
