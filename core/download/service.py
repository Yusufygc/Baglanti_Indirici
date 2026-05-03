import os
from dataclasses import dataclass, replace
from typing import Callable

from core.platform.service import PlatformService
from .progress import ProgressFormatter
from core.web.extractor import USER_AGENT, WebMediaExtractor
from .errors import DownloadError


class CancelledDownload(Exception):
    pass


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


class DownloadService:
    def __init__(self, yt_dlp_client=None, web_extractor=None, platform_service=None):
        if yt_dlp_client is None:
            from .yt_dlp_client import YtDlpClient
            yt_dlp_client = YtDlpClient()

        self.yt_dlp_client = yt_dlp_client
        self.web_extractor = web_extractor or WebMediaExtractor
        self.platform_service = platform_service or PlatformService

    def cancel(self):
        self.yt_dlp_client.cancel()

    def run(self, request, events, is_cancelled):
        normalized_url = self.platform_service.normalize_url(request.url)
        platform = self.platform_service.detect(normalized_url)
        if not self.platform_service.is_supported(platform):
            raise DownloadError(f"Geçersiz veya desteklenmeyen URL: {normalized_url}")

        request = replace(request, url=normalized_url, platform=platform)
        events.platform_detected(platform)

        target_dir = self._prepare_directory(request.download_dir, platform)
        events.folder_prepared(target_dir)
        events.started("İndirme başlatılıyor...")
        self._raise_if_cancelled(is_cancelled)

        try:
            self._download(request, target_dir, events, is_cancelled)
        except DownloadError as exc:
            if platform != "Web" or "Unsupported URL" not in str(exc):
                raise
            self._raise_if_cancelled(is_cancelled)
            self._download_with_web_fallback(request, target_dir, events, is_cancelled)

    def _download(self, request, target_dir, events, is_cancelled, url=None, http_headers=None):
        options = self.yt_dlp_client.build_options(
            request,
            target_dir,
            self._output_template(request, target_dir),
            self._progress_hook(events, is_cancelled),
            http_headers=http_headers,
        )
        self.yt_dlp_client.download(url or request.url, options)

    def _download_with_web_fallback(self, request, target_dir, events, is_cancelled):
        events.started("Sayfa analiz ediliyor…")
        result = self.web_extractor.extract(request.url)
        if not result:
            raise DownloadError(
                "Bu sayfada indirilebilir video kaynağı bulunamadı veya kaynak korumalı."
            )

        self._raise_if_cancelled(is_cancelled)
        events.started("Video kaynağı bulundu…")
        fallback_request = replace(request, platform="Web")
        events.started("İndiriliyor…")
        self._download(
            fallback_request,
            target_dir,
            events,
            is_cancelled,
            url=result.media_url,
            http_headers={
                "User-Agent": USER_AGENT,
                "Referer": request.url,
            },
        )

    def _progress_hook(self, events, is_cancelled):
        def hook(data):
            self._raise_if_cancelled(is_cancelled)
            formatted = ProgressFormatter.from_yt_dlp(data)
            if formatted:
                percent, message = formatted
                events.progress(percent, message)

        return hook

    @staticmethod
    def _prepare_directory(download_dir, platform_name):
        if os.path.basename(download_dir).lower() == platform_name.lower():
            return download_dir

        target_path = os.path.join(download_dir, platform_name)
        os.makedirs(target_path, exist_ok=True)
        return target_path

    @staticmethod
    def _output_template(request, target_dir):
        suffix = "video" if request.mode == "video" else "audio"
        extension = "%(ext)s"

        if request.is_playlist:
            return os.path.join(
                target_dir,
                "%(playlist_title)s",
                f"%(playlist_index)02d - %(title)s_{suffix}.{extension}",
            )
        if request.filename:
            return os.path.join(target_dir, f"{request.filename}_{suffix}.{extension}")
        return os.path.join(target_dir, f"%(title)s_{suffix}.{extension}")

    @staticmethod
    def _raise_if_cancelled(is_cancelled):
        if is_cancelled():
            raise CancelledDownload
