# indirici.py
import os
import urllib.parse
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import yt_dlp

class IndiriciSinyalleri(QObject):
    """
    İndirme işlemi sırasında arayüze sinyal göndermek için kullanılır.
    """
    platform_belirlendi = pyqtSignal(str)
    klasor_hazirlandi = pyqtSignal(str)
    indirme_basladi = pyqtSignal(str)
    ilerleme_guncellendi = pyqtSignal(int, str)
    indirme_bitti = pyqtSignal()
    iptal_edildi = pyqtSignal() # İptal sinyali için yeni eklenen
    hata_olustu = pyqtSignal(str)

class Indirici(QThread):
    """
    yt-dlp ve ffmpeg kullanarak indirme işlemini ayrı bir thread'de yürütür.
    """
    def __init__(self, url, indirme_dizini, secenek, dosya_adi=None):
        super().__init__()
        self.url = url
        self.indirme_dizini = indirme_dizini
        self.secenek = secenek
        self.dosya_adi = dosya_adi
        self.sinyaller = IndiriciSinyalleri()
        self._is_cancelled = False # İptal durumunu tutmak için yeni eklenen

    def iptal_et(self):
        """
        İndirme işlemini iptal etmek için çağrılır.
        """
        self._is_cancelled = True

    def run(self):
        try:
            platform = self.platform_belirle()
            if platform == "Bilinmeyen" or platform == "GecersizURL":
                self.sinyaller.hata_olustu.emit(f"Geçersiz veya desteklenmeyen URL: {self.url}")
                return

            self.sinyaller.platform_belirlendi.emit(f"Platform belirlendi: {platform}")

            hedef_klasor = self.klasor_hazirla(platform)
            self.sinyaller.klasor_hazirlandi.emit(f"İndirme klasörü hazır: {hedef_klasor}")

            self.sinyaller.indirme_basladi.emit("İndirme başlatılıyor...")

            # İndirme işlemi başlamadan önce iptal edilmiş mi kontrol et
            if self._is_cancelled:
                self.sinyaller.iptal_edildi.emit()
                return

            # --- FFmpeg YOLU AYARI ---
            # yt-dlp, FFmpeg'i sistem PATH'inde arar. Eğer hata alırsanız, 
            # buradaki 'ffmpeg' değerini, ffmpeg.exe dosyasının tam yolu ile değiştirin.
            # Örneğin: r'C:\Program Files\ffmpeg\bin\ffmpeg.exe'
            ffmpeg_path = r'C:\ffmpeg\bin\ffmpeg.exe'

            if self.dosya_adi:
                outtmpl_template = os.path.join(hedef_klasor, f'{self.dosya_adi}.%(ext)s')
            else:
                outtmpl_template = os.path.join(hedef_klasor, '%(title)s.%(ext)s')
            
            if self.secenek == "video":
                ydl_opts = {
                    'outtmpl': outtmpl_template,
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
                    'merge_output_format': 'mp4',
                    'ffmpeg_location': ffmpeg_path,
                    'progress_hooks': [self.ilerleme_hook],
                }
            else: # self.secenek == "ses"
                ydl_opts = {
                    'outtmpl': outtmpl_template,
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'ffmpeg_location': ffmpeg_path,
                    'progress_hooks': [self.ilerleme_hook],
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])

            if not self._is_cancelled:
                self.sinyaller.indirme_bitti.emit()
            else:
                self.sinyaller.iptal_edildi.emit()

        except KeyboardInterrupt:
            # İndirme işlemi iptal edildiğinde burası çalışır.
            self.sinyaller.iptal_edildi.emit()
            # Önemli: Bu noktadan sonra başka bir işlem yapmadan fonksiyonu sonlandırın.
            return
        except yt_dlp.utils.DownloadError as e:
            self.sinyaller.hata_olustu.emit(f"Bir indirme hatası oluştu: {e}")
        except Exception as e:
            self.sinyaller.hata_olustu.emit(f"Beklenmeyen bir hata oluştu: {e}")

    def ilerleme_hook(self, d):
        """
        yt-dlp tarafından indirme ilerlemesini bildirmek için çağrılır.
        Aynı zamanda iptal durumunu kontrol eder ve indirmeyi durdurur.
        """
        # İptal durumu kontrolü
        if self._is_cancelled:
            # yt-dlp'yi durdurmak için bir istisna fırlat
            raise KeyboardInterrupt

        if d['status'] == 'downloading':
            if d.get('total_bytes'):
                yuzde = d['downloaded_bytes'] * 100 / d['total_bytes']
            elif d.get('total_bytes_estimate'):
                yuzde = d['downloaded_bytes'] * 100 / d['total_bytes_estimate']
            else:
                yuzde = 0

            hiz = f"{d.get('speed', 0) / 1024 / 1024:.2f} MiB/s" if d.get('speed') else "Bilinmiyor"
            tahmini_sure = f"{d.get('eta', 0)}s" if d.get('eta') else "Bilinmiyor"
            durum_mesaji = f"Hız: {hiz}, Tahmini Kalan Süre: {tahmini_sure}"

            self.sinyaller.ilerleme_guncellendi.emit(int(yuzde), durum_mesaji)
        elif d['status'] == 'finished':
            self.sinyaller.ilerleme_guncellendi.emit(100, "İndirme tamamlandı.")


    def platform_belirle(self):
        """
        URL'ye göre platform adını belirler.
        """
        try:
            parsed_url = urllib.parse.urlparse(self.url)
            domain = parsed_url.netloc

            if "youtube.com" in domain or "youtu.be" in domain:
                return "YouTube"
            elif "tiktok.com" in domain:
                return "TikTok"
            elif "instagram.com" in domain:
                return "Instagram"
            else:
                return "Bilinmeyen"
        except:
            return "GecersizURL"

    def klasor_hazirla(self, platform_adi):
        """
        İndirme klasörünü hazırlar.
        Seçilen dizin adı platform adı ile aynıysa yeni klasör oluşturmaz.
        """
        if os.path.basename(self.indirme_dizini).lower() == platform_adi.lower():
            return self.indirme_dizini
        else:
            hedef_dizin = os.path.join(self.indirme_dizini, platform_adi)
            if not os.path.exists(hedef_dizin):
                os.makedirs(hedef_dizin)
            return hedef_dizin
