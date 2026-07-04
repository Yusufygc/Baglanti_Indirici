import hashlib
import io
import os
import shutil
import tempfile
import urllib.request
import zipfile
from typing import Optional, Tuple

from .errors import UpdateError
from .pypi_client import PyPiClient, ReleaseInfo


def _parse_version(v: str) -> Tuple[int, ...]:
    parts = []
    for chunk in v.split("."):
        digits = "".join(ch for ch in chunk if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


class YtDlpUpdater:
    def __init__(self, lib_dir: str, pypi_client: Optional[PyPiClient] = None):
        # lib_dir: get_yt_dlp_lib_dir()'in dondurdugu klasor (yt_dlp/'nin parent'i)
        self.lib_dir = lib_dir
        self.pypi_client = pypi_client or PyPiClient("yt-dlp")

    def get_installed_version(self) -> str:
        import yt_dlp.version
        return yt_dlp.version.__version__

    def check_for_update(self) -> Tuple[bool, ReleaseInfo]:
        release = self.pypi_client.fetch_latest_release()
        installed = self.get_installed_version()
        is_newer = _parse_version(release.version) > _parse_version(installed)
        return is_newer, release

    def install_update(self, release: ReleaseInfo, progress_callback=None) -> None:
        """
        Wheel'i indirir, yt_dlp/ paketini cikarir ve lib_dir/yt_dlp'nin
        yerine guvenli sekilde koyar. Calisan exe'yi DEGIL, sadece data
        klasorunu degistirdigi icin OS dosya kilidi problemi yoktur.
        """
        os.makedirs(self.lib_dir, exist_ok=True)
        staging_new = os.path.join(self.lib_dir, "yt_dlp__new")
        staging_old = os.path.join(self.lib_dir, "yt_dlp__old")
        live_path = os.path.join(self.lib_dir, "yt_dlp")

        # Onceki basarisiz denemeden kalan artiklari temizle
        shutil.rmtree(staging_new, ignore_errors=True)
        shutil.rmtree(staging_old, ignore_errors=True)

        wheel_bytes = self._download_wheel(release, progress_callback)
        self._extract_yt_dlp_package(wheel_bytes, staging_new)

        # Guvenlik: cikarilan paket gercekten calisir bir yt_dlp mi?
        version_file = os.path.join(staging_new, "version.py")
        if not os.path.exists(version_file):
            shutil.rmtree(staging_new, ignore_errors=True)
            raise UpdateError("Indirilen pakette yt_dlp/version.py bulunamadi; kurulum iptal edildi.")

        try:
            if os.path.exists(live_path):
                os.rename(live_path, staging_old)
            os.rename(staging_new, live_path)
        except OSError as exc:
            # Rollback
            if os.path.exists(staging_old) and not os.path.exists(live_path):
                os.rename(staging_old, live_path)
            raise UpdateError(f"yt_dlp klasoru degistirilemedi: {exc}") from exc
        finally:
            shutil.rmtree(staging_old, ignore_errors=True)
            shutil.rmtree(staging_new, ignore_errors=True)

    def _download_wheel(self, release: ReleaseInfo, progress_callback) -> bytes:
        try:
            with urllib.request.urlopen(release.wheel_url, timeout=30) as resp:
                total = release.size or int(resp.headers.get("Content-Length", 0))
                chunks = []
                read = 0
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    chunks.append(chunk)
                    read += len(chunk)
                    if progress_callback and total:
                        progress_callback(int(read * 100 / total))
                data = b"".join(chunks)
        except OSError as exc:
            raise UpdateError(f"yt-dlp indirilemedi: {exc}") from exc

        if release.sha256:
            digest = hashlib.sha256(data).hexdigest()
            if digest != release.sha256:
                raise UpdateError("Indirilen dosyanin butunluk kontrolu (sha256) basarisiz.")
        return data

    @staticmethod
    def _extract_yt_dlp_package(wheel_bytes: bytes, target_dir: str) -> None:
        try:
            with zipfile.ZipFile(io.BytesIO(wheel_bytes)) as zf:
                members = [n for n in zf.namelist() if n.startswith("yt_dlp/")]
                if not members:
                    raise UpdateError("Wheel icinde yt_dlp/ paketi bulunamadi.")
                with tempfile.TemporaryDirectory() as tmp_extract:
                    zf.extractall(tmp_extract, members=members)
                    shutil.move(os.path.join(tmp_extract, "yt_dlp"), target_dir)
        except zipfile.BadZipFile as exc:
            raise UpdateError(f"Indirilen wheel dosyasi bozuk: {exc}") from exc
