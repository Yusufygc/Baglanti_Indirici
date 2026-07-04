import pytest

import yt_dlp

from core.download.yt_dlp_client import YtDlpClient
from core.download.errors import DownloadError
from core.download.service import DownloadRequest
from core.instagram import session as ig_session


class _FakeDownloader:
    """yt_dlp.YoutubeDL yerine gecen, context manager destekli sahte indirici."""

    def __init__(self, options):
        self.options = options

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False

    def download(self, urls):
        raise self.options["_raise"]


def _patch_youtubedl(monkeypatch, exc):
    def factory(options):
        options = dict(options)
        options["_raise"] = exc
        return _FakeDownloader(options)

    monkeypatch.setattr(yt_dlp, "YoutubeDL", factory)


def test_instagram_login_wall_maps_to_turkish_message(monkeypatch):
    raw = yt_dlp.utils.DownloadError(
        "ERROR: [Instagram] DaT5F7Jy4ws: Instagram sent an empty media response."
    )
    _patch_youtubedl(monkeypatch, raw)

    client = YtDlpClient()
    with pytest.raises(DownloadError) as excinfo:
        client.download("https://www.instagram.com/reel/DaT5F7Jy4ws/", {})

    message = str(excinfo.value)
    assert "giriş" in message
    assert "empty media response" not in message.lower()


def test_unrelated_error_passes_through_unchanged(monkeypatch):
    raw = yt_dlp.utils.DownloadError("ERROR: [youtube] abc: HTTP Error 404: Not Found")
    _patch_youtubedl(monkeypatch, raw)

    client = YtDlpClient()
    with pytest.raises(DownloadError) as excinfo:
        client.download("https://www.youtube.com/watch?v=abc", {})

    assert "HTTP Error 404" in str(excinfo.value)


def _build(platform):
    request = DownloadRequest(
        url="https://x/y", download_dir="/tmp", platform=platform
    )
    return YtDlpClient().build_options(request, "/tmp", "out.%(ext)s", lambda d: None)


def test_build_options_adds_cookiefile_for_instagram_with_session(monkeypatch):
    monkeypatch.setattr(ig_session, "has_session", lambda: True)
    monkeypatch.setattr(ig_session, "cookies_path", lambda: "/path/cookies.txt")

    options = _build("Instagram")

    assert options.get("cookiefile") == "/path/cookies.txt"


def test_build_options_no_cookiefile_without_session(monkeypatch):
    monkeypatch.setattr(ig_session, "has_session", lambda: False)

    assert "cookiefile" not in _build("Instagram")


def test_build_options_no_cookiefile_for_other_platform(monkeypatch):
    monkeypatch.setattr(ig_session, "has_session", lambda: True)
    monkeypatch.setattr(ig_session, "cookies_path", lambda: "/path/cookies.txt")

    assert "cookiefile" not in _build("YouTube")
