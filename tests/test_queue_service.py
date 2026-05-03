from core.domain import DownloadOptions, JobStatus
from core.history import HistoryRepository
from core.queue import DownloadQueueService


def test_queue_service_runs_jobs_fifo(tmp_path):
    queue = DownloadQueueService(HistoryRepository(str(tmp_path / "history.sqlite3")))
    options = DownloadOptions(download_dir=str(tmp_path))

    first = queue.enqueue("https://example.com/1", options)
    second = queue.enqueue("https://example.com/2", options)

    assert queue.next_job().id == first.id
    queue.mark_completed(first.id, str(tmp_path))
    assert queue.next_job().id == second.id


def test_queue_service_cancels_queued_job(tmp_path):
    queue = DownloadQueueService(HistoryRepository(str(tmp_path / "history.sqlite3")))
    job = queue.enqueue("https://example.com/1", DownloadOptions(download_dir=str(tmp_path)))

    cancelled = queue.cancel(job.id)

    assert cancelled.status == JobStatus.CANCELLED
    assert queue.next_job() is None


def test_queue_service_retries_from_history(tmp_path):
    repo = HistoryRepository(str(tmp_path / "history.sqlite3"))
    queue = DownloadQueueService(repo)
    job = queue.enqueue("https://example.com/1", DownloadOptions(download_dir=str(tmp_path)))
    queue.mark_failed(job.id, "failed")

    retried = queue.retry(job.id)

    assert retried.id != job.id
    assert retried.status == JobStatus.QUEUED
    assert queue.next_job().id == retried.id
