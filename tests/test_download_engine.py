import tempfile

import pytest

from core.download.engine import CancelledDownload, DownloadEngine
from core.download.errors import DownloadError
from core.download.service import DownloadEvents, DownloadRequest
from core.web.extractor import WebMediaResult


class FakeYtDlpClient:
    def __init__(self, failures=None):
        self.failures = list(failures or [])
        self.downloads = []
        self.options = []

    def cancel(self):
        pass

    def build_options(self, request, target_dir, output_template, progress_hook, http_headers=None):
        options = {
            "platform": request.platform,
            "target_dir": target_dir,
            "outtmpl": output_template,
            "http_headers": http_headers,
        }
        self.options.append(options)
        return options

    def download(self, url, options):
        self.downloads.append(url)
        if self.failures:
            raise self.failures.pop(0)


class FakeExtractor:
    def extract(self, url):
        return WebMediaResult(
            media_url="https://cdn.test/video.mp4",
            source_page_url=url,
            media_type="file",
        )


def test_download_engine_keeps_web_fallback_behavior():
    client = FakeYtDlpClient([DownloadError("Unsupported URL")])
    engine = DownloadEngine(yt_dlp_client=client, web_extractor=FakeExtractor())
    events = DownloadEvents(
        platform_detected=lambda value: None,
        folder_prepared=lambda value: None,
        started=lambda value: None,
        progress=lambda percent, text: None,
    )

    with tempfile.TemporaryDirectory() as tmp:
        engine.run(
            DownloadRequest("https://site.test/embed", tmp),
            events,
            is_cancelled=lambda: False,
        )

    assert client.downloads == ["https://site.test/embed", "https://cdn.test/video.mp4"]
    assert client.options[-1]["http_headers"]["Referer"] == "https://site.test/embed"


class _FakePlatformService:
    @staticmethod
    def normalize_url(url):
        return url

    @staticmethod
    def detect(url):
        return "Test"

    @staticmethod
    def is_supported(platform):
        return True


class _CancellingClient:
    """Indirme sirasinda progress hook'u cagirip iptal tetikleyen sahte istemci."""

    def __init__(self, part_path, cancel_state):
        self.part_path = part_path
        self.cancel_state = cancel_state

    def cancel(self):
        pass

    def build_options(self, request, target_dir, output_template, progress_hook, http_headers=None):
        return {"hook": progress_hook}

    def download(self, url, options):
        hook = options["hook"]
        # yt-dlp gibi once ilerleme bildir (yarim dosya kaydedilir), sonra iptal gelir.
        hook({"status": "downloading", "tmpfilename": self.part_path})
        self.cancel_state["cancelled"] = True
        hook({"status": "downloading", "tmpfilename": self.part_path})


def test_download_engine_removes_partial_file_on_cancel(tmp_path):
    part_file = tmp_path / "video.mp4.part"
    part_file.write_bytes(b"yarim veri")
    cancel_state = {"cancelled": False}

    engine = DownloadEngine(
        yt_dlp_client=_CancellingClient(str(part_file), cancel_state),
        platform_service=_FakePlatformService(),
    )
    events = DownloadEvents(
        platform_detected=lambda value: None,
        folder_prepared=lambda value: None,
        started=lambda value: None,
        progress=lambda percent, text: None,
    )

    with pytest.raises(CancelledDownload):
        engine.run(
            DownloadRequest("https://site.test/video", str(tmp_path)),
            events,
            is_cancelled=lambda: cancel_state["cancelled"],
        )

    assert not part_file.exists()
