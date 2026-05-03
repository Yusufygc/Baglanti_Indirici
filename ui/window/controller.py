from core.domain import DownloadOptions, JobStatus
from core.download.worker import DownloadQueueWorker
from core.history import HistoryRepository
from core.queue import DownloadQueueService


class MainWindowController:
    def __init__(
        self,
        view,
        worker_factory=DownloadQueueWorker,
        history_repository=None,
        queue_service=None,
    ):
        self.view = view
        self.worker_factory = worker_factory
        self.history_repository = history_repository or HistoryRepository()
        self.queue_service = queue_service or DownloadQueueService(self.history_repository)
        self.worker = None

    def is_running(self):
        return bool(self.worker and self.worker.isRunning())

    def start_download(self, url, download_dir, mode, filename, is_playlist):
        return self.enqueue_download(url, download_dir, mode, filename, is_playlist)

    def enqueue_download(self, url, download_dir, mode, filename, is_playlist):
        job = self.queue_service.enqueue(
            url,
            DownloadOptions(
                download_dir=download_dir,
                mode=mode,
                filename=filename,
                is_playlist=is_playlist,
            ),
        )
        self.view.upsert_queue_job(job)
        self.view.set_status(f"Kuyruga eklendi: {job.platform}")
        self._ensure_worker()
        return job

    def retry_download(self, job_id):
        job = self.queue_service.retry(job_id)
        if not job:
            self.view.set_status("Gecmis kaydi bulunamadi.", error=True)
            return None
        self.view.upsert_queue_job(job)
        self.view.set_status("Is tekrar kuyruga eklendi.")
        self._ensure_worker()
        return job

    def cancel_download(self, job_id=None):
        if job_id and self.is_running():
            self.worker.cancel_job(job_id)
            self.view.set_status("Iptal ediliyor...", error=True)

    def clear_history(self):
        self.history_repository.clear()
        self.view.render_history([])
        self.view.set_status("Gecmis temizlendi.")

    def list_history(self, limit=30):
        return self.history_repository.list_recent(limit)

    def clear_worker(self):
        self.worker = None

    def _ensure_worker(self):
        if self.is_running():
            return
        self.worker = self.worker_factory(self.queue_service)
        self.worker.signals.job_updated.connect(self._on_job_updated)
        self.worker.signals.queue_idle.connect(self._on_queue_idle)
        self.worker.start()

    def _on_job_updated(self, job):
        self.view.upsert_queue_job(job)
        if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
            self.view.render_history(self.list_history())
        if job.status == JobStatus.RUNNING:
            self.view.set_status(f"Platform: {job.platform}  -  Indiriliyor...")
        elif job.status == JobStatus.COMPLETED:
            self.view.set_status("Indirme tamamlandi.")
        elif job.status == JobStatus.FAILED:
            self.view.set_status(job.error_message or "Indirme basarisiz.", error=True)
        elif job.status == JobStatus.CANCELLED:
            self.view.set_status("Indirme iptal edildi.", error=True)

    def _on_queue_idle(self):
        self.clear_worker()
        self.view.render_queue(self.queue_service.active_jobs())
        self.view.render_history(self.list_history())
        self.view.set_status("Hazir")
