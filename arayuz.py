# arayuz.py
import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QFileDialog,
                             QTextEdit, QProgressBar, QRadioButton)
from PyQt5.QtCore import Qt, pyqtSlot
from indirici import Indirici

class UygulamaArayuzu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bağlantı İndirici")
        self.setGeometry(300, 300, 600, 400)

        # Varsayılan indirme dizini
        self.indirme_dizini = os.path.join(os.path.expanduser('~'), 'Downloads')
        self.indirici_thread = None

        self.arayuzu_olustur()

    def arayuzu_olustur(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setAlignment(Qt.AlignTop)

        # 1. URL Giriş Alanı
        url_layout = QHBoxLayout()
        self.url_label = QLabel("URL:")
        self.url_entry = QLineEdit()
        self.url_entry.setPlaceholderText("İndirmek istediğiniz bağlantıyı yapıştırın...")
        url_layout.addWidget(self.url_label)
        url_layout.addWidget(self.url_entry)

        main_layout.addLayout(url_layout)

        # 2. Dizin Seçme Alanı
        dizin_layout = QHBoxLayout()
        self.dizin_label = QLabel("Hedef Dizin:")
        self.dizin_display = QLabel(self.indirme_dizini)
        self.dizin_sec_button = QPushButton("Dizin Seç")
        self.dizin_sec_button.clicked.connect(self.dizin_sec)

        dizin_layout.addWidget(self.dizin_label)
        dizin_layout.addWidget(self.dizin_display)
        dizin_layout.addWidget(self.dizin_sec_button)

        main_layout.addLayout(dizin_layout)
        
        # 3. Dosya Adı Giriş Alanı
        dosya_adi_layout = QHBoxLayout()
        self.dosya_adi_label = QLabel("Dosya Adı (isteğe bağlı):")
        self.dosya_adi_entry = QLineEdit()
        self.dosya_adi_entry.setPlaceholderText("Boş bırakılırsa orijinal isim kullanılır...")
        dosya_adi_layout.addWidget(self.dosya_adi_label)
        dosya_adi_layout.addWidget(self.dosya_adi_entry)
        
        main_layout.addLayout(dosya_adi_layout)

        # 4. İndirme Seçenekleri (Video/Ses)
        secenek_layout = QHBoxLayout()
        secenek_label = QLabel("İndirme Formatı:")
        self.video_secenegi = QRadioButton("Video")
        self.video_secenegi.setChecked(True)  # Varsayılan olarak video seçili
        self.ses_secenegi = QRadioButton("Ses")
        
        secenek_layout.addWidget(secenek_label)
        secenek_layout.addWidget(self.video_secenegi)
        secenek_layout.addWidget(self.ses_secenegi)
        secenek_layout.addStretch() # Düğmeleri sola yasla

        main_layout.addLayout(secenek_layout)

        # 5. İşlem Butonları
        buton_layout = QHBoxLayout()
        self.indir_button = QPushButton("İndir")
        self.indir_button.setFixedSize(100, 40)
        self.indir_button.clicked.connect(self.indirmeyi_baslat)
        
        self.iptal_button = QPushButton("İptal Et")
        self.iptal_button.setFixedSize(100, 40)
        self.iptal_button.setEnabled(False)  # Başlangıçta devre dışı
        self.iptal_button.clicked.connect(self.indirmeyi_iptal_et)

        buton_layout.addStretch()
        buton_layout.addWidget(self.indir_button)
        buton_layout.addWidget(self.iptal_button)
        buton_layout.addStretch()

        main_layout.addLayout(buton_layout)

        # 6. Durum ve Log Alanı
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setPlaceholderText("İşlem adımları burada görüntülenecek...")
        main_layout.addWidget(self.log_display)

        # 7. İlerleme Çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)

        self.setLayout(main_layout)

    def dizin_sec(self):
        """
        Kullanıcıdan indirme dizini seçmesini ister ve günceller.
        """
        yeni_dizin = QFileDialog.getExistingDirectory(self, "İndirme Dizinini Seç", self.indirme_dizini)
        if yeni_dizin:
            self.indirme_dizini = yeni_dizin
            self.dizin_display.setText(self.indirme_dizini)
            self.log_display.append(f"<b>Dizin güncellendi:</b> {self.indirme_dizini}")

    def indirmeyi_baslat(self):
        """
        İndirme işlemini başlatır ve arayüzü günceller.
        """
        url = self.url_entry.text().strip()
        if not url:
            self.log_display.append("<span style='color:red;'>Lütfen bir URL girin!</span>")
            return

        self.indir_button.setEnabled(False)
        self.iptal_button.setEnabled(True)  # İndirme başladığında iptal butonunu aktif et
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        self.log_display.clear()
        self.log_display.append(f"<b>URL alındı:</b> {url}")
        
        # Seçilen indirme seçeneğini ve dosya adını belirle
        if self.video_secenegi.isChecked():
            secenek = "video"
        else:
            secenek = "ses"
        
        dosya_adi = self.dosya_adi_entry.text().strip()
        if not dosya_adi:
            dosya_adi = None # Boşsa None olarak gönderelim

        self.indirici_thread = Indirici(url, self.indirme_dizini, secenek, dosya_adi)
        self.indirici_thread.sinyaller.platform_belirlendi.connect(self.log_mesaji_goster)
        self.indirici_thread.sinyaller.klasor_hazirlandi.connect(self.log_mesaji_goster)
        self.indirici_thread.sinyaller.indirme_basladi.connect(self.indirme_basladi_guncelle)
        self.indirici_thread.sinyaller.ilerleme_guncellendi.connect(self.ilerleme_guncelle)
        self.indirici_thread.sinyaller.indirme_bitti.connect(self.indirme_tamamlandi)
        self.indirici_thread.sinyaller.iptal_edildi.connect(self.indirme_iptal_edildi) # Yeni sinyal
        self.indirici_thread.sinyaller.hata_olustu.connect(self.indirme_hatasi)

        self.indirici_thread.start()

    def indirmeyi_iptal_et(self):
        """
        İndirme işlemini iptal etmek için sinyal gönderir.
        """
        if self.indirici_thread and self.indirici_thread.isRunning():
            self.indirici_thread.iptal_et()
            self.log_display.append("<span style='color:orange;'>İndirme işlemi iptal ediliyor...</span>")

    @pyqtSlot(str)
    def log_mesaji_goster(self, mesaj):
        self.log_display.append(mesaj)
    
    @pyqtSlot(str)
    def indirme_basladi_guncelle(self, mesaj):
        self.log_display.append(mesaj)
        self.progress_bar.show()
        self.progress_bar.setValue(0)

    @pyqtSlot(int, str)
    def ilerleme_guncelle(self, yuzde, durum_mesaji):
        """
        İlerleme çubuğunu ve log ekranını günceller.
        """
        self.progress_bar.setValue(yuzde)
        self.log_display.setText(f"<b>Durum:</b> {durum_mesaji}<br><b>İndirme yüzdesi:</b> {yuzde}%")

    @pyqtSlot()
    def indirme_tamamlandi(self):
        self.progress_bar.setValue(100)
        self.log_display.append("<span style='color:green;'><b>İndirme işlemi başarıyla tamamlandı!</b></span>")
        self.progress_bar.hide()
        self.indir_button.setEnabled(True)
        self.iptal_button.setEnabled(False) # İndirme bittiğinde iptal butonunu devre dışı bırak
        self.indirici_thread = None
        self.url_entry.clear()
        self.dosya_adi_entry.clear()

    @pyqtSlot()
    def indirme_iptal_edildi(self):
        self.log_display.append("<span style='color:orange;'><b>İndirme işlemi iptal edildi. Uygulama yeni indirme için hazır.</b></span>")
        self.progress_bar.hide()
        self.indir_button.setEnabled(True)
        self.iptal_button.setEnabled(False) # İndirme iptal edildiğinde iptal butonunu devre dışı bırak
        self.indirici_thread = None
        self.url_entry.clear()
        self.dosya_adi_entry.clear()

    @pyqtSlot(str)
    def indirme_hatasi(self, hata_mesaji):
        self.log_display.append(f"<span style='color:red;'><b>Hata:</b> {hata_mesaji}</span>")
        self.progress_bar.hide()
        self.indir_button.setEnabled(True)
        self.iptal_button.setEnabled(False) # Hata oluştuğunda iptal butonunu devre dışı bırak
        self.indirici_thread = None
        self.url_entry.clear()
        self.dosya_adi_entry.clear()