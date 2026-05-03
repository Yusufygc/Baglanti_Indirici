from PyQt5.QtCore import QObject, QThread, pyqtSignal

from core.domain import DownloadOptions
from core.platform.service import PlatformService

from .errors import DownloadError
from .service import CancelledDownload, DownloadEvents, DownloadRequest, DownloadService


class WorkerSignals(QObject):
    platform_detected = pyqtSignal(str)
    folder_prepared = pyqtSignal(str)
    started = pyqtSignal(str)
    progress = pyqtSignal(int, str)
    finished = pyqtSignal()
    cancelled = pyqtSignal()
    error = pyqtSignal(str)


class QueueWorkerSignals(QObject):
    job_updated = pyqtSignal(object)
    queue_idle = pyqtSignal()


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
            self.signals.error.emit(f"Indirme hatasi: {exc}")
        except Exception as exc:
            self.signals.error.emit(f"Beklenmeyen hata: {exc}")


class DownloadQueueWorker(QThread):
    def __init__(self, queue_service, download_service_factory=DownloadService):
        super().__init__()
        self.queue_service = queue_service
        self.download_service_factory = download_service_factory
        self.signals = QueueWorkerSignals()
        self._active_service = None

    def cancel_job(self, job_id: str):
        job = self.queue_service.cancel(job_id)
        if job:
            self.signals.job_updated.emit(job)
        if self._active_service:
            self._active_service.cancel()

    def run(self):
        while True:
            job = self.queue_service.next_job()
            if not job:
                break

            self.signals.job_updated.emit(job)
            output_path = {"value": None}
            service = self.download_service_factory()
            self._active_service = service

            try:
                service.run(
                    self._request_from_job(job),
                    DownloadEvents(
                        platform_detected=lambda platform, job_id=job.id: self._set_platform(
                            job_id,
                            platform,
                        ),
                        folder_prepared=lambda path: output_path.update(value=path),
                        started=lambda message, job_id=job.id: self._set_message(job_id, message),
                        progress=lambda percent, message, job_id=job.id: self._set_progress(
                            job_id,
                            percent,
                            message,
                        ),
                        title_detected=lambda title, job_id=job.id: self._set_title(
                            job_id,
                            title,
                        ),
                    ),
                    is_cancelled=lambda job_id=job.id: self.queue_service.is_cancel_requested(job_id),
                )

                if self.queue_service.is_cancel_requested(job.id):
                    updated = self.queue_service.mark_cancelled(job.id)
                else:
                    updated = self.queue_service.mark_completed(job.id, output_path["value"])
                if updated:
                    self.signals.job_updated.emit(updated)
            except CancelledDownload:
                updated = self.queue_service.mark_cancelled(job.id)
                if updated:
                    self.signals.job_updated.emit(updated)
            except KeyboardInterrupt:
                updated = self.queue_service.mark_cancelled(job.id)
                if updated:
                    self.signals.job_updated.emit(updated)
            except DownloadError as exc:
                updated = self.queue_service.mark_failed(job.id, f"Indirme hatasi: {exc}")
                if updated:
                    self.signals.job_updated.emit(updated)
            except Exception as exc:
                updated = self.queue_service.mark_failed(job.id, f"Beklenmeyen hata: {exc}")
                if updated:
                    self.signals.job_updated.emit(updated)
            finally:
                self._active_service = None

        self.signals.queue_idle.emit()

    @staticmethod
    def _request_from_job(job):
        options: DownloadOptions = job.options
        return DownloadRequest(
            url=job.normalized_url,
            download_dir=options.download_dir,
            mode=options.mode,
            filename=options.filename,
            is_playlist=options.is_playlist,
            platform=job.platform,
        )

    def _set_platform(self, job_id: str, platform: str) -> None:
        job = self.queue_service.mark_platform(job_id, platform)
        if job:
            self.signals.job_updated.emit(job)

    def _set_message(self, job_id: str, message: str) -> None:
        job = self.queue_service.mark_message(job_id, message)
        if job:
            self.signals.job_updated.emit(job)

    def _set_progress(self, job_id: str, percent: int, message: str) -> None:
        job = self.queue_service.mark_progress(job_id, percent, message)
        if job:
            self.signals.job_updated.emit(job)

    def _set_title(self, job_id: str, title: str) -> None:
        job = self.queue_service.mark_title(job_id, title)
        if job:
            self.signals.job_updated.emit(job)
