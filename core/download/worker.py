from PyQt5.QtCore import QObject, QThread, pyqtSignal

from .service import CancelledDownload, DownloadEvents, DownloadRequest, DownloadService
from .errors import DownloadError
from core.platform.service import PlatformService


class WorkerSignals(QObject):
    platform_detected = pyqtSignal(str)
    folder_prepared = pyqtSignal(str)
    started = pyqtSignal(str)
    progress = pyqtSignal(int, str)
    finished = pyqtSignal()
    cancelled = pyqtSignal()
    error = pyqtSignal(str)


class DownloadWorker(QThread):
    def __init__(self, url, download_dir, mode="video", filename=None, is_playlist=False):
        super().__init__()
        self.request = DownloadRequest(
            url=PlatformService.normalize_url(url),
            download_dir=download_dir,
            mode=mode,
            filename=filename,
            is_playlist=is_playlist,
        )
        self.signals = WorkerSignals()
        self._is_cancelled = False
        self._service = DownloadService()

    def cancel(self):
        self._is_cancelled = True
        self._service.cancel()

    def run(self):
        try:
            self._service.run(
                self.request,
                DownloadEvents(
                    platform_detected=self.signals.platform_detected.emit,
                    folder_prepared=self.signals.folder_prepared.emit,
                    started=self.signals.started.emit,
                    progress=self.signals.progress.emit,
                ),
                is_cancelled=lambda: self._is_cancelled,
            )

            if self._is_cancelled:
                self.signals.cancelled.emit()
            else:
                self.signals.finished.emit()
        except CancelledDownload:
            self.signals.cancelled.emit()
        except KeyboardInterrupt:
            self.signals.cancelled.emit()
        except DownloadError as exc:
            self.signals.error.emit(f"İndirme hatası: {exc}")
        except Exception as exc:
            self.signals.error.emit(f"Beklenmeyen hata: {exc}")
