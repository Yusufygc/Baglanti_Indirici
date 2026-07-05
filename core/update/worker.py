from PySide6.QtCore import QObject, QThread, Signal

from core.config import get_yt_dlp_lib_dir
from core.logger import get_logger

from .errors import UpdateError
from .yt_dlp_updater import YtDlpUpdater

logger = get_logger("update_worker")


def _default_updater():
    lib_dir = get_yt_dlp_lib_dir()
    if not lib_dir:
        return None
    return YtDlpUpdater(lib_dir)


class UpdateCheckSignals(QObject):
    update_available = Signal(object)   # ReleaseInfo
    up_to_date = Signal()
    error = Signal(str)


class UpdateCheckWorker(QThread):
    """Sadece PyPI'a sorup versiyon kiyaslar; indirme YAPMAZ. Hizli, hafif."""

    def __init__(self, updater_factory=None):
        super().__init__()
        self.signals = UpdateCheckSignals()
        self._updater_factory = updater_factory or _default_updater

    def run(self):
        try:
            updater = self._updater_factory()
            if updater is None:
                return  # harici lib klasoru yok; sessizce cik
            is_newer, release = updater.check_for_update()
            if is_newer:
                self.signals.update_available.emit(release)
            else:
                self.signals.up_to_date.emit()
        except UpdateError as exc:
            logger.warning("yt-dlp guncelleme kontrolu basarisiz: %s", exc)
            self.signals.error.emit(str(exc))
        except Exception as exc:
            logger.exception("yt-dlp guncelleme kontrolunde beklenmeyen hata")
            self.signals.error.emit(f"Beklenmeyen hata: {exc}")


class UpdateInstallSignals(QObject):
    progress = Signal(int)
    completed = Signal(str)   # yeni surum
    error = Signal(str)


class UpdateInstallWorker(QThread):
    def __init__(self, release, updater_factory=None):
        super().__init__()
        self.release = release
        self.signals = UpdateInstallSignals()
        self._updater_factory = updater_factory or _default_updater

    def run(self):
        try:
            updater = self._updater_factory()
            if updater is None:
                self.signals.error.emit("Harici yt-dlp klasoru bulunamadi.")
                return
            updater.install_update(self.release, progress_callback=self.signals.progress.emit)
            self.signals.completed.emit(self.release.version)
        except UpdateError as exc:
            logger.warning("yt-dlp guncelleme kurulumu basarisiz: %s", exc)
            self.signals.error.emit(str(exc))
        except Exception as exc:
            logger.exception("yt-dlp guncelleme kurulumunda beklenmeyen hata")
            self.signals.error.emit(f"Beklenmeyen hata: {exc}")
