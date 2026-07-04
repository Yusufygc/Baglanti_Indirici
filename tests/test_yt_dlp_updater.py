import io
import os
import zipfile
from unittest.mock import patch

import pytest

from core.update.errors import UpdateError
from core.update.pypi_client import ReleaseInfo
from core.update.yt_dlp_updater import YtDlpUpdater, _parse_version


def _make_wheel_bytes(version_content: str = "__version__ = '2099.01.01'\n") -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("yt_dlp/__init__.py", "")
        zf.writestr("yt_dlp/version.py", version_content)
    return buffer.getvalue()


def test_parse_version_orders_correctly():
    assert _parse_version("2025.1.15") < _parse_version("2025.1.15.1")
    assert _parse_version("2025.1.15") < _parse_version("2025.2.1")
    assert _parse_version("2024.12.31") < _parse_version("2025.1.1")


def test_check_for_update_detects_newer_version(tmp_path):
    updater = YtDlpUpdater(str(tmp_path))
    with patch.object(updater, "get_installed_version", return_value="2024.01.01"):
        with patch.object(
            updater.pypi_client,
            "fetch_latest_release",
            return_value=ReleaseInfo(version="2025.11.03", wheel_url="x", sha256=None, size=None),
        ):
            is_newer, release = updater.check_for_update()

    assert is_newer is True
    assert release.version == "2025.11.03"


def test_check_for_update_reports_up_to_date(tmp_path):
    updater = YtDlpUpdater(str(tmp_path))
    with patch.object(updater, "get_installed_version", return_value="2025.11.03"):
        with patch.object(
            updater.pypi_client,
            "fetch_latest_release",
            return_value=ReleaseInfo(version="2025.11.03", wheel_url="x", sha256=None, size=None),
        ):
            is_newer, _release = updater.check_for_update()

    assert is_newer is False


def test_install_update_replaces_yt_dlp_folder(tmp_path):
    lib_dir = tmp_path / "lib"
    lib_dir.mkdir()
    old_yt_dlp = lib_dir / "yt_dlp"
    old_yt_dlp.mkdir()
    (old_yt_dlp / "version.py").write_text("__version__ = '2024.01.01'\n")

    wheel_bytes = _make_wheel_bytes("__version__ = '2099.01.01'\n")
    release = ReleaseInfo(version="2099.01.01", wheel_url="https://example.com/x.whl", sha256=None, size=None)

    updater = YtDlpUpdater(str(lib_dir))
    with patch.object(updater, "_download_wheel", return_value=wheel_bytes):
        updater.install_update(release)

    new_version_file = old_yt_dlp / "version.py"
    assert new_version_file.exists()
    assert "2099.01.01" in new_version_file.read_text()
    assert not os.path.exists(str(lib_dir / "yt_dlp__old"))
    assert not os.path.exists(str(lib_dir / "yt_dlp__new"))


def test_install_update_rejects_wheel_without_yt_dlp_package(tmp_path):
    lib_dir = tmp_path / "lib"
    lib_dir.mkdir()

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("some_other_package/__init__.py", "")

    release = ReleaseInfo(version="2099.01.01", wheel_url="x", sha256=None, size=None)
    updater = YtDlpUpdater(str(lib_dir))

    with patch.object(updater, "_download_wheel", return_value=buffer.getvalue()):
        with pytest.raises(UpdateError):
            updater.install_update(release)


def test_install_update_rejects_bad_zip(tmp_path):
    lib_dir = tmp_path / "lib"
    lib_dir.mkdir()

    release = ReleaseInfo(version="2099.01.01", wheel_url="x", sha256=None, size=None)
    updater = YtDlpUpdater(str(lib_dir))

    with patch.object(updater, "_download_wheel", return_value=b"not a zip file"):
        with pytest.raises(UpdateError):
            updater.install_update(release)


def test_download_wheel_rejects_sha256_mismatch(tmp_path):
    release = ReleaseInfo(version="2099.01.01", wheel_url="https://example.com/x.whl", sha256="deadbeef", size=None)
    updater = YtDlpUpdater(str(tmp_path))

    class _Resp:
        headers = {}

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self, _n=None):
            if not hasattr(self, "_read_once"):
                self._read_once = True
                return b"some bytes"
            return b""

    with patch("urllib.request.urlopen", return_value=_Resp()):
        with pytest.raises(UpdateError):
            updater._download_wheel(release, None)
