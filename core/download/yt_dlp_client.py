import yt_dlp

from core.config import get_ffmpeg_path
from core.instagram import session as ig_session
from .errors import DownloadError
from core.platform.service import PlatformService

# Instagram'in login duvarina takildigini gosteren yt-dlp hata izleri (bkz.
# yt-dlp #17074 - 2026 Temmuz'unda Instagram API'sini degistirip gonderiler icin
# giris zorunlu hale getirdi; bu icerikler giris yapmadan hicbir yolla inmiyor).
_LOGIN_REQUIRED_MARKERS = ("empty media response", "login required", "requested content is not available")


class YtDlpClient:
    def __init__(self):
        self.active_downloader = None

    def cancel(self):
        if self.active_downloader:
            self.active_downloader.to_screen("İndirme işlemi iptal ediliyor...")

    def build_options(self, request, target_dir, output_template, progress_hook, http_headers=None):
        options = PlatformService.format_options(request.platform, request.mode)
        options.update({
            "outtmpl": output_template,
            "merge_output_format": "mp4" if request.mode == "video" else None,
            "ffmpeg_location": get_ffmpeg_path(),
            "progress_hooks": [progress_hook],
            "quiet": True,
            "no_warnings": True,
            "noplaylist": not request.is_playlist,
            "ignoreerrors": request.is_playlist,
            "sleep_interval_requests": 1,
            "sleep_interval": 2,
            "max_sleep_interval": 6,
            "retries": 10,
        })
        # Instagram login-gerekli icerik: kayitli oturum cookies.txt varsa yt-dlp'ye ver.
        if request.platform == "Instagram" and ig_session.has_session():
            options["cookiefile"] = ig_session.cookies_path()
        if http_headers:
            options["http_headers"] = http_headers
        return options

    def download(self, url, options):
        try:
            self._run(url, options)
        except DownloadError as exc:
            raise self._friendly_error(exc) from exc

    def _run(self, url, options):
        try:
            with yt_dlp.YoutubeDL(options) as downloader:
                self.active_downloader = downloader
                result_code = downloader.download([url])
                if result_code not in (None, 0):
                    raise DownloadError(f"yt-dlp hata kodu: {result_code}")
        except yt_dlp.utils.DownloadError as exc:
            raise DownloadError(str(exc)) from exc
        finally:
            self.active_downloader = None

    @classmethod
    def _friendly_error(cls, exc):
        message = str(exc)
        lowered = message.lower()
        if any(marker in lowered for marker in _LOGIN_REQUIRED_MARKERS):
            return DownloadError(ig_session.INSTAGRAM_LOGIN_REQUIRED_MSG)
        return exc
