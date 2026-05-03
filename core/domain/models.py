from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Callable
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class DownloadMode(str, Enum):
    VIDEO = "video"
    AUDIO = "ses"

    @classmethod
    def from_value(cls, value: str) -> "DownloadMode":
        if value == cls.AUDIO.value:
            return cls.AUDIO
        return cls.VIDEO


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class DownloadOptions:
    download_dir: str
    mode: str = DownloadMode.VIDEO.value
    filename: str | None = None
    is_playlist: bool = False
    quality: str = "best"
    audio_bitrate: str = "192"
    subtitles: bool = False


@dataclass(frozen=True)
class DownloadJob:
    url: str
    normalized_url: str
    platform: str
    options: DownloadOptions
    id: str = field(default_factory=lambda: str(uuid4()))
    status: JobStatus = JobStatus.QUEUED
    created_at: str = field(default_factory=utc_now_iso)
    started_at: str | None = None
    finished_at: str | None = None
    output_path: str | None = None
    error_message: str | None = None
    title: str | None = None
    progress_percent: int = 0
    status_message: str = "Bekliyor"

    def update(self, **changes) -> "DownloadJob":
        return replace(self, **changes)


FormatPolicy = Callable[[str], dict]


@dataclass(frozen=True)
class PlatformProfile:
    name: str
    domains: tuple[str, ...]
    color: str = "#8B91A7"
    format_policy: FormatPolicy | None = None

    def matches(self, domain: str) -> bool:
        lowered = domain.lower()
        return any(pattern in lowered for pattern in self.domains)

    def format_options(self, mode: str) -> dict:
        if self.format_policy:
            return self.format_policy(mode)
        return default_format_policy(mode)


def default_format_policy(mode: str) -> dict:
    if mode == DownloadMode.AUDIO.value:
        return {
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        }
    return {"format": "best[ext=mp4]/bestvideo+bestaudio/best"}
