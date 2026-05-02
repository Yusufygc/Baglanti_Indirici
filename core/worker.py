import os
import re
import yt_dlp
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from .utils import PlatformHelper

ANSI_ESCAPE_RE = re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')

class WorkerSignals(QObject):
    """
    Worker thread sinyalleri.
    """
    platform_detected = pyqtSignal(str)   # platform_belirlendi
    folder_prepared = pyqtSignal(str)     # klasor_hazirlandi
    started = pyqtSignal(str)             # indirme_basladi
    progress = pyqtSignal(int, str)       # ilerleme_guncellendi
    finished = pyqtSignal()               # indirme_bitti
    cancelled = pyqtSignal()              # iptal_edildi
    error = pyqtSignal(str)               # hata_olustu

class DownloadWorker(QThread):
    def __init__(self, url, download_dir, mode='video', filename=None, is_playlist=False):
        super().__init__()
        self.url = PlatformHelper.normalize_url(url)
        self.download_dir = download_dir
        self.mode = mode # 'video' or 'ses'
        self.filename = filename
        self.is_playlist = is_playlist
        self.signals = WorkerSignals()
        self._is_cancelled = False
        self._ydl = None

    def cancel(self):
        """İndirmeyi güvenli bir şekilde iptal et."""
        self._is_cancelled = True
        if self._ydl:
            self._ydl.to_screen('İndirme işlemi iptal ediliyor...')
            # yt-dlp'nin durmasını tetikleyen özel exception veya flag
            # Aslında yt-dlp hook içinde raise ederek durduracağız.

    def run(self):
        try:
            # 1. Platform Belirleme
            platform = PlatformHelper.get_platform_name(self.url)
            if platform == "Bilinmeyen" or platform == "GecersizURL":
                self.signals.error.emit(f"Geçersiz veya desteklenmeyen URL: {self.url}")
                return

            self.signals.platform_detected.emit(platform)

            # 2. Klasör Hazırlama
            target_dir = self._prepare_directory(platform)
            self.signals.folder_prepared.emit(target_dir)

            self.signals.started.emit("İndirme başlatılıyor...")

            if(self._is_cancelled):
                 self.signals.cancelled.emit()
                 return

            # 3. YDL Ayarları
            from .config import get_ffmpeg_path
            ffmpeg_path = get_ffmpeg_path()
            
            # Utils'den ydl konfigürasyonunu al
            ydl_opts = PlatformHelper.get_video_format_options(platform, self.mode)
            
            # Ortak ayarları ekle
            outtmpl = self._get_output_template(target_dir)
            ydl_opts.update({
                'outtmpl': outtmpl,
                'merge_output_format': 'mp4' if self.mode == 'video' else None,
                'ffmpeg_location': ffmpeg_path,
                'progress_hooks': [self._progress_hook],
                'quiet': True,
                'no_warnings': True,
                'noplaylist': not self.is_playlist,
                'ignoreerrors': True,            # Hata veren videoyu atla, seriye devam et
                'sleep_interval_requests': 1,    # Sunucu istekleri arasına 1 sn bekleme
                'sleep_interval': 2,             # Her indirme arası en az 2 sn bekle
                'max_sleep_interval': 6,         # Bekleme süresini 2-6 sn arası rastgele yap
                'retries': 10                    # Başarısızlık durumunda tekrar deneme sayısı
            })

            # 4. İndirme Başlat
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self._ydl = ydl
                ydl.download([self.url])

            if not self._is_cancelled:
                self.signals.finished.emit()
            else:
                self.signals.cancelled.emit()

        except KeyboardInterrupt:
            self.signals.cancelled.emit()
        except yt_dlp.utils.DownloadError as e:
            self.signals.error.emit(f"İndirme hatası: {str(e)}")
        except Exception as e:
            self.signals.error.emit(f"Beklenmeyen hata: {str(e)}")

    def _prepare_directory(self, platform_name):
        """Hedef klasörü hazırlar."""
        if os.path.basename(self.download_dir).lower() == platform_name.lower():
            return self.download_dir
            
        target_path = os.path.join(self.download_dir, platform_name)
        os.makedirs(target_path, exist_ok=True)
        return target_path

    def _get_output_template(self, target_dir):
        """Çıktı dosyası şablonunu belirler."""
        suffix = "video" if self.mode == "video" else "audio"
        ext = "%(ext)s"
        
        if self.is_playlist:
            return os.path.join(target_dir, '%(playlist_title)s', f'%(playlist_index)02d - %(title)s_{suffix}.{ext}')
        elif self.filename:
            return os.path.join(target_dir, f'{self.filename}_{suffix}.{ext}')
        else:
            return os.path.join(target_dir, f'%(title)s_{suffix}.{ext}')

    def _progress_hook(self, d):
        """yt-dlp callback fonksiyonu."""
        if self._is_cancelled:
            # yt-dlp'ye interrupt gönder
            raise KeyboardInterrupt

        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes', 0)
            
            percentage = 0
            if total > 0:
                percentage = int(downloaded * 100 / total)
            
            # Hız ve Süre hesabı
            speed_str = d.get('_speed_str', 'Bilinmiyor') # yt-dlp string olarak veriyor bazen
            eta_str = d.get('_eta_str', 'Bilinmiyor')

            if not speed_str: # Sayısal olarak geldiyse formatla
                speed = d.get('speed', 0)
                if speed: speed_str = f"{speed / 1024 / 1024:.2f} MiB/s"
            
            if not eta_str:
                eta = d.get('eta', 0)
                if eta: eta_str = f"{eta}s"

            speed_str = self._clean_terminal_text(speed_str)
            eta_str = self._clean_terminal_text(eta_str)

            # Playlist bilgisi ekle
            info = d.get('info_dict', {})
            p_index = info.get('playlist_index')
            p_count = info.get('n_entries')
            playlist_info = f" • Video {p_index}/{p_count}" if p_index and p_count else ""

            status_msg = f"Hız: {speed_str} • Kalan: {eta_str}{playlist_info}"
            self.signals.progress.emit(percentage, status_msg)
            
        elif d['status'] == 'finished':
            self.signals.progress.emit(100, "İşleniyor…")

    @staticmethod
    def _clean_terminal_text(value):
        """yt-dlp'nin renkli terminal çıktılarındaki ANSI kodlarını arayüzden temizle."""
        if value is None:
            return "Bilinmiyor"
        text = str(value)
        text = ANSI_ESCAPE_RE.sub('', text)
        return " ".join(text.split()) or "Bilinmiyor"
