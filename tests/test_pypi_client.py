import json
from unittest.mock import patch

import pytest

from core.update.errors import UpdateError
from core.update.pypi_client import PyPiClient


def _fake_response(payload: dict):
    class _Resp:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps(payload).encode("utf-8")

    return _Resp()


def test_fetch_latest_release_parses_wheel_entry():
    payload = {
        "info": {"version": "2025.11.03"},
        "urls": [
            {"packagetype": "sdist", "url": "https://example.com/yt-dlp.tar.gz"},
            {
                "packagetype": "bdist_wheel",
                "url": "https://example.com/yt_dlp-2025.11.03-py3-none-any.whl",
                "size": 4096,
                "digests": {"sha256": "abc123"},
            },
        ],
    }

    with patch("urllib.request.urlopen", return_value=_fake_response(payload)):
        release = PyPiClient("yt-dlp").fetch_latest_release()

    assert release.version == "2025.11.03"
    assert release.wheel_url.endswith(".whl")
    assert release.sha256 == "abc123"
    assert release.size == 4096


def test_fetch_latest_release_raises_when_no_wheel():
    payload = {"info": {"version": "2025.11.03"}, "urls": [{"packagetype": "sdist", "url": "x"}]}

    with patch("urllib.request.urlopen", return_value=_fake_response(payload)):
        with pytest.raises(UpdateError):
            PyPiClient("yt-dlp").fetch_latest_release()


def test_fetch_latest_release_raises_when_no_version():
    payload = {"info": {}, "urls": []}

    with patch("urllib.request.urlopen", return_value=_fake_response(payload)):
        with pytest.raises(UpdateError):
            PyPiClient("yt-dlp").fetch_latest_release()
