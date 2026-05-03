import tempfile

from core.download.engine import DownloadEngine
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
