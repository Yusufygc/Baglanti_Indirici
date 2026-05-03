from core.download.worker import DownloadWorker


class MainWindowController:
    def __init__(self, view, worker_factory=DownloadWorker):
        self.view = view
        self.worker_factory = worker_factory
        self.worker = None

    def is_running(self):
        return bool(self.worker and self.worker.isRunning())

    def start_download(self, url, download_dir, mode, filename, is_playlist):
        self.worker = self.worker_factory(url, download_dir, mode, filename, is_playlist)
        self.worker.signals.platform_detected.connect(
            lambda platform: self.view.set_status(f"Platform: {platform}  •  İndiriliyor…")
        )
        self.worker.signals.started.connect(self.view.set_status)
        self.worker.signals.progress.connect(self.view.update_progress)
        self.worker.signals.finished.connect(self._on_finished)
        self.worker.signals.cancelled.connect(self._on_cancelled)
        self.worker.signals.error.connect(self._on_error)
        self.worker.signals.folder_prepared.connect(lambda _: None)
        self.worker.start()

    def cancel_download(self):
        if self.is_running():
            self.worker.cancel()
            self.view.set_status("İptal ediliyor…", error=True)

    def clear_worker(self):
        self.worker = None

    def _on_finished(self):
        self.view.handle_finished()
        self.clear_worker()

    def _on_cancelled(self):
        self.view.handle_cancelled()
        self.clear_worker()

    def _on_error(self, message):
        self.view.handle_error(message)
        self.clear_worker()
