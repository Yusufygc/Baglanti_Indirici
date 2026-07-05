from core.domain import DownloadOptions, JobStatus
from core.download.worker import DownloadQueueWorker
from core.history import HistoryRepository
from core.logger import get_logger
from core.queue import DownloadQueueService
from core.update.worker import UpdateCheckWorker, UpdateInstallWorker

logger = get_logger("controller")


class MainWindowController:
    def __init__(
        self,
        view,
        worker_factory=DownloadQueueWorker,
        history_repository=None,
        queue_service=None,
        update_check_worker_factory=UpdateCheckWorker,
        update_install_worker_factory=UpdateInstallWorker,
    ):
        self.view = view
        self.worker_factory = worker_factory
        self.history_repository = history_repository or HistoryRepository()
        self.queue_service = queue_service or DownloadQueueService(self.history_repository)
        self.worker = None
        self.update_check_worker_factory = update_check_worker_factory
        self.update_install_worker_factory = update_install_worker_factory
        self._update_check_worker = None
        self._update_install_worker = None
        self._pending_release = None

    def is_running(self):
        return bool(self.worker and self.worker.isRunning())

    def start_download(self, url, download_dir, mode, filename, is_playlist):
        return self.enqueue_download(url, download_dir, mode, filename, is_playlist)

    def enqueue_download(self, url, download_dir, mode, filename, is_playlist):
        try:
            job = self.queue_service.enqueue(
                url,
                DownloadOptions(
                    download_dir=download_dir,
                    mode=mode,
                    filename=filename,
                    is_playlist=is_playlist,
                ),
            )
        except Exception as exc:
            logger.exception("Kuyruga ekleme basarisiz: url=%s", url)
            self.view.set_status(f"Gecersiz baglanti: {exc}", error=True)
            return None

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
            self.view.flash_compact_result(True)
        elif job.status == JobStatus.FAILED:
            self._handle_failed_job(job)
            self.view.flash_compact_result(False)
        elif job.status == JobStatus.CANCELLED:
            self.view.set_status("Indirme iptal edildi.", error=True)

    def _handle_failed_job(self, job):
        from core.instagram import session as ig_session

        message = job.error_message or "Indirme basarisiz."
        if ig_session.INSTAGRAM_LOGIN_REQUIRED_MSG in message:
            if ig_session.has_session():
                # Oturum var ama yine login duvarina takildi -> suresi dolmus.
                ig_session.clear_session()
                self.view.prompt_instagram_login(
                    "Instagram oturumu suresi dolmus. 'Instagram Giris' butonuna "
                    "tiklayip tekrar giris yapin."
                )
            else:
                self.view.prompt_instagram_login(
                    "Instagram girisi gerekiyor. Ust taraftaki 'Instagram Giris' "
                    "butonuna tiklayip giris yapin."
                )
            return
        self.view.set_status(message, error=True)

    def _on_queue_idle(self):
        self.clear_worker()
        self.view.render_queue(self.queue_service.active_jobs())
        self.view.render_history(self.list_history())
        self.view.set_status("Hazir")

    def check_for_yt_dlp_update(self):
        if self._update_check_worker and self._update_check_worker.isRunning():
            return
        self._update_check_worker = self.update_check_worker_factory()
        self._update_check_worker.signals.update_available.connect(self._on_update_available)
        self._update_check_worker.signals.up_to_date.connect(lambda: None)
        self._update_check_worker.signals.error.connect(lambda _msg: None)  # sessiz
        self._update_check_worker.start()

    def _on_update_available(self, release):
        self._pending_release = release
        self.view.show_update_available(release.version)

    def install_yt_dlp_update(self):
        if not self._pending_release:
            return
        if self._update_install_worker and self._update_install_worker.isRunning():
            return
        self._update_install_worker = self.update_install_worker_factory(self._pending_release)
        self._update_install_worker.signals.progress.connect(self.view.show_update_progress)
        self._update_install_worker.signals.completed.connect(self._on_update_installed)
        self._update_install_worker.signals.error.connect(self._on_update_error)
        self.view.show_update_installing()
        self._update_install_worker.start()

    def _on_update_installed(self, version):
        self._pending_release = None
        self.view.show_update_installed(version)

    def _on_update_error(self, message):
        self.view.set_status(f"Guncelleme hatasi: {message}", error=True)
        self.view.hide_update_button()
