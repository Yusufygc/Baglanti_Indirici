from ui.window.controller import MainWindowController


class _FakeView:
    def __init__(self):
        self.status_messages = []
        self.queue_jobs = []

    def upsert_queue_job(self, job):
        self.queue_jobs.append(job)

    def set_status(self, text, error=False):
        self.status_messages.append((text, error))


class _RaisingQueueService:
    def enqueue(self, url, options):
        raise ValueError("gecersiz IPv6 URL")


class _FakeHistoryRepository:
    pass


def test_enqueue_download_handles_malformed_url_without_crashing():
    view = _FakeView()
    controller = MainWindowController(
        view,
        history_repository=_FakeHistoryRepository(),
        queue_service=_RaisingQueueService(),
    )

    result = controller.enqueue_download("http://[bozuk", "/tmp", "video", None, False)

    assert result is None
    assert view.queue_jobs == []
    assert view.status_messages
    text, is_error = view.status_messages[-1]
    assert is_error is True
    assert "Gecersiz baglanti" in text
