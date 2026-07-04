from core.domain import DownloadJob, DownloadOptions, JobStatus
from core.history import HistoryRepository


def test_history_repository_persists_and_lists_jobs(tmp_path):
    repo = HistoryRepository(str(tmp_path / "history.sqlite3"))
    job = DownloadJob(
        url="https://example.com/video",
        normalized_url="https://example.com/video",
        platform="Web",
        options=DownloadOptions(download_dir=str(tmp_path)),
    )

    repo.add_or_update(job)
    updated = job.update(status=JobStatus.COMPLETED, progress_percent=100)
    repo.add_or_update(updated)

    assert repo.get(job.id).status == JobStatus.COMPLETED
    assert repo.list_recent()[0].id == job.id


def test_list_recent_only_returns_completed(tmp_path):
    repo = HistoryRepository(str(tmp_path / "history.sqlite3"))
    base = DownloadJob(
        url="https://example.com/video",
        normalized_url="https://example.com/video",
        platform="Web",
        options=DownloadOptions(download_dir=str(tmp_path)),
    )
    repo.add_or_update(base.update(status=JobStatus.FAILED))
    repo.add_or_update(base.update(status=JobStatus.CANCELLED))

    assert repo.list_recent() == []

    repo.add_or_update(base.update(status=JobStatus.COMPLETED))
    recent = repo.list_recent()
    assert len(recent) == 1
    assert recent[0].status == JobStatus.COMPLETED


def test_delete_removes_single_row(tmp_path):
    repo = HistoryRepository(str(tmp_path / "history.sqlite3"))
    job = DownloadJob(
        url="https://example.com/video",
        normalized_url="https://example.com/video",
        platform="Web",
        options=DownloadOptions(download_dir=str(tmp_path)),
    )
    repo.add_or_update(job)

    repo.delete(job.id)

    assert repo.get(job.id) is None


def test_history_repository_clear_removes_rows(tmp_path):
    repo = HistoryRepository(str(tmp_path / "history.sqlite3"))
    repo.add_or_update(DownloadJob(
        url="https://example.com/video",
        normalized_url="https://example.com/video",
        platform="Web",
        options=DownloadOptions(download_dir=str(tmp_path)),
    ))

    repo.clear()

    assert repo.list_recent() == []
