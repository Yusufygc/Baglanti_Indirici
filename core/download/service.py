from dataclasses import dataclass, field
from typing import Callable

from .engine import CancelledDownload, DownloadEngine


@dataclass(frozen=True)
class DownloadRequest:
    url: str
    download_dir: str
    mode: str = "video"
    filename: str | None = None
    is_playlist: bool = False
    platform: str = ""


@dataclass(frozen=True)
class DownloadEvents:
    platform_detected: Callable[[str], None]
    folder_prepared: Callable[[str], None]
    started: Callable[[str], None]
    progress: Callable[[int, str], None]
    title_detected: Callable[[str], None] = field(default=lambda title: None)


class DownloadService:
    def __init__(self, yt_dlp_client=None, web_extractor=None, platform_service=None):
        self.engine = DownloadEngine(
            yt_dlp_client=yt_dlp_client,
            web_extractor=web_extractor,
            platform_service=platform_service,
        )

    def cancel(self):
        self.engine.cancel()

    def run(self, request, events, is_cancelled):
        return self.engine.run(request, events, is_cancelled)
