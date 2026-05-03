from __future__ import annotations

from collections import deque
from threading import RLock

from core.domain import DownloadJob, DownloadOptions, JobStatus
from core.domain.models import utc_now_iso
from core.history import HistoryRepository
from core.platform.registry import PlatformRegistry


class DownloadQueueService:
    def __init__(
        self,
        history_repository: HistoryRepository | None = None,
        platform_registry: PlatformRegistry | None = None,
        max_concurrent: int = 1,
    ):
        self.history_repository = history_repository
        self.platform_registry = platform_registry or PlatformRegistry()
        self.max_concurrent = max(1, max_concurrent)
        self._jobs: dict[str, DownloadJob] = {}
        self._queue: deque[str] = deque()
        self._running: set[str] = set()
        self._cancel_requested: set[str] = set()
        self._paused = False
        self._lock = RLock()

    def enqueue(self, url: str, options: DownloadOptions) -> DownloadJob:
        with self._lock:
            normalized_url = self.platform_registry.normalize_url(url)
            platform = self.platform_registry.detect(normalized_url)
            job = DownloadJob(
                url=url,
                normalized_url=normalized_url,
                platform=platform,
                options=options,
            )
            self._jobs[job.id] = job
            self._queue.append(job.id)
            self._persist(job)
            return job

    def next_job(self) -> DownloadJob | None:
        with self._lock:
            if self._paused or len(self._running) >= self.max_concurrent:
                return None
            while self._queue:
                job_id = self._queue.popleft()
                job = self._jobs.get(job_id)
                if job and job.status == JobStatus.QUEUED:
                    updated = job.update(
                        status=JobStatus.RUNNING,
                        started_at=utc_now_iso(),
                        status_message="Baslatiliyor",
                    )
                    self._jobs[job_id] = updated
                    self._running.add(job_id)
                    self._persist(updated)
                    return updated
            return None

    def mark_progress(self, job_id: str, percent: int, message: str) -> DownloadJob | None:
        return self._update_job(
            job_id,
            progress_percent=percent,
            status_message=message,
        )

    def mark_platform(self, job_id: str, platform: str) -> DownloadJob | None:
        return self._update_job(job_id, platform=platform)

    def mark_message(self, job_id: str, message: str) -> DownloadJob | None:
        return self._update_job(job_id, status_message=message)

    def mark_title(self, job_id: str, title: str) -> DownloadJob | None:
        cleaned = " ".join((title or "").split())
        if not cleaned:
            return self._jobs.get(job_id)
        return self._update_job(job_id, title=cleaned)

    def mark_completed(self, job_id: str, output_path: str | None = None) -> DownloadJob | None:
        with self._lock:
            self._running.discard(job_id)
        return self._update_job(
            job_id,
            status=JobStatus.COMPLETED,
            finished_at=utc_now_iso(),
            output_path=output_path,
            progress_percent=100,
            status_message="Tamamlandi",
            error_message=None,
        )

    def mark_failed(self, job_id: str, message: str) -> DownloadJob | None:
        with self._lock:
            self._running.discard(job_id)
        return self._update_job(
            job_id,
            status=JobStatus.FAILED,
            finished_at=utc_now_iso(),
            error_message=message,
            status_message=message,
        )

    def mark_cancelled(self, job_id: str) -> DownloadJob | None:
        with self._lock:
            self._running.discard(job_id)
            self._cancel_requested.discard(job_id)
        return self._update_job(
            job_id,
            status=JobStatus.CANCELLED,
            finished_at=utc_now_iso(),
            status_message="Iptal edildi",
        )

    def cancel(self, job_id: str) -> DownloadJob | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None
            self._cancel_requested.add(job_id)
            if job.status == JobStatus.QUEUED:
                self._queue = deque(item for item in self._queue if item != job_id)
                return self.mark_cancelled(job_id)
            return job

    def retry(self, job_id: str) -> DownloadJob | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job and self.history_repository:
                job = self.history_repository.get(job_id)
            if not job:
                return None
            return self.enqueue(job.url, job.options)

    def pause_queue(self) -> None:
        with self._lock:
            self._paused = True

    def resume_queue(self) -> None:
        with self._lock:
            self._paused = False

    def is_cancel_requested(self, job_id: str) -> bool:
        with self._lock:
            return job_id in self._cancel_requested

    def list_jobs(self) -> list[DownloadJob]:
        with self._lock:
            return list(self._jobs.values())

    def active_jobs(self) -> list[DownloadJob]:
        with self._lock:
            return [
                job for job in self._jobs.values()
                if job.status in (JobStatus.QUEUED, JobStatus.RUNNING)
            ]

    def has_pending_work(self) -> bool:
        with self._lock:
            return bool(self._queue or self._running)

    def _update_job(self, job_id: str, **changes) -> DownloadJob | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None
            updated = job.update(**changes)
            self._jobs[job_id] = updated
            self._persist(updated)
            return updated

    def _persist(self, job: DownloadJob) -> None:
        if self.history_repository:
            self.history_repository.add_or_update(job)
