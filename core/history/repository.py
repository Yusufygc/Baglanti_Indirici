from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import asdict
from pathlib import Path

from core.domain import DownloadJob, DownloadOptions, JobStatus


class HistoryRepository:
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or self.default_path()
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    @staticmethod
    def default_path() -> str:
        return os.path.join(Path.home(), ".baglanti_indirici", "history.sqlite3")

    def add_or_update(self, job: DownloadJob) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO download_history (
                    id, url, normalized_url, platform, options_json, status,
                    created_at, started_at, finished_at, output_path, error_message,
                    title, progress_percent, status_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    url=excluded.url,
                    normalized_url=excluded.normalized_url,
                    platform=excluded.platform,
                    options_json=excluded.options_json,
                    status=excluded.status,
                    created_at=excluded.created_at,
                    started_at=excluded.started_at,
                    finished_at=excluded.finished_at,
                    output_path=excluded.output_path,
                    error_message=excluded.error_message,
                    title=excluded.title,
                    progress_percent=excluded.progress_percent,
                    status_message=excluded.status_message
                """,
                self._row_values(job),
            )

    def list_recent(self, limit: int = 50) -> list[DownloadJob]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM download_history
                ORDER BY COALESCE(finished_at, started_at, created_at) DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._job_from_row(row) for row in rows]

    def get(self, job_id: str) -> DownloadJob | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM download_history WHERE id = ?",
                (job_id,),
            ).fetchone()
        return self._job_from_row(row) if row else None

    def clear(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM download_history")

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS download_history (
                    id TEXT PRIMARY KEY,
                    url TEXT NOT NULL,
                    normalized_url TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    options_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    finished_at TEXT,
                    output_path TEXT,
                    error_message TEXT,
                    title TEXT,
                    progress_percent INTEGER NOT NULL DEFAULT 0,
                    status_message TEXT NOT NULL DEFAULT ''
                )
                """
            )
            columns = {
                row["name"]
                for row in conn.execute("PRAGMA table_info(download_history)").fetchall()
            }
            if "title" not in columns:
                conn.execute("ALTER TABLE download_history ADD COLUMN title TEXT")

    @staticmethod
    def _row_values(job: DownloadJob) -> tuple:
        return (
            job.id,
            job.url,
            job.normalized_url,
            job.platform,
            json.dumps(asdict(job.options), ensure_ascii=False),
            job.status.value,
            job.created_at,
            job.started_at,
            job.finished_at,
            job.output_path,
            job.error_message,
            job.title,
            job.progress_percent,
            job.status_message,
        )

    @staticmethod
    def _job_from_row(row: sqlite3.Row) -> DownloadJob:
        options = DownloadOptions(**json.loads(row["options_json"]))
        return DownloadJob(
            id=row["id"],
            url=row["url"],
            normalized_url=row["normalized_url"],
            platform=row["platform"],
            options=options,
            status=JobStatus(row["status"]),
            created_at=row["created_at"],
            started_at=row["started_at"],
            finished_at=row["finished_at"],
            output_path=row["output_path"],
            error_message=row["error_message"],
            title=row["title"],
            progress_percent=row["progress_percent"],
            status_message=row["status_message"],
        )
