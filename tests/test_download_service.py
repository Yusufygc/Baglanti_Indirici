import tempfile

import pytest

from core.download.errors import DownloadError
from core.download.service import DownloadEvents, DownloadRequest, DownloadService
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
            "progress_hook": progress_hook,
        }
        self.options.append(options)
        return options

    def download(self, url, options):
        self.downloads.append(url)
        if self.failures:
            raise self.failures.pop(0)


class FakeExtractor:
    def __init__(self, result):
        self.result = result

    def extract(self, url):
        return self.result


def events(bucket):
    return DownloadEvents(
        platform_detected=lambda value: bucket.append(("platform", value)),
        folder_prepared=lambda value: bucket.append(("folder", value)),
        started=lambda value: bucket.append(("started", value)),
        progress=lambda percent, text: bucket.append(("progress", percent, text)),
    )


def test_service_success_uses_primary_download():
    client = FakeYtDlpClient()
    seen = []
    with tempfile.TemporaryDirectory() as tmp:
        service = DownloadService(yt_dlp_client=client, web_extractor=FakeExtractor(None))
        service.run(
            DownloadRequest("https://example.com/video.mp4", tmp),
            events(seen),
            is_cancelled=lambda: False,
        )

    assert client.downloads == ["https://example.com/video.mp4"]
    assert ("platform", "Web") in seen


def test_service_fallback_only_for_unsupported_web_url():
    client = FakeYtDlpClient([DownloadError("Unsupported URL")])
    extractor = FakeExtractor(WebMediaResult(
        media_url="https://cdn.test/video.mp4",
        source_page_url="https://site.test/embed",
        media_type="file",
    ))

    with tempfile.TemporaryDirectory() as tmp:
        service = DownloadService(yt_dlp_client=client, web_extractor=extractor)
        service.run(
            DownloadRequest("https://site.test/embed", tmp),
            events([]),
            is_cancelled=lambda: False,
        )

    assert client.downloads == ["https://site.test/embed", "https://cdn.test/video.mp4"]
    assert client.options[-1]["http_headers"]["Referer"] == "https://site.test/embed"


def test_service_non_unsupported_error_does_not_fallback():
    client = FakeYtDlpClient([DownloadError("HTTP Error 403")])

    with tempfile.TemporaryDirectory() as tmp:
        service = DownloadService(yt_dlp_client=client, web_extractor=FakeExtractor(None))
        with pytest.raises(DownloadError):
            service.run(
                DownloadRequest("https://site.test/embed", tmp),
                events([]),
                is_cancelled=lambda: False,
            )
