import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional

from .errors import UpdateError

PYPI_JSON_URL = "https://pypi.org/pypi/{package}/json"
TIMEOUT_SECONDS = 10


@dataclass(frozen=True)
class ReleaseInfo:
    version: str
    wheel_url: str
    sha256: Optional[str]
    size: Optional[int]


class PyPiClient:
    def __init__(self, package_name: str = "yt-dlp"):
        self.package_name = package_name

    def fetch_latest_release(self) -> ReleaseInfo:
        url = PYPI_JSON_URL.format(package=self.package_name)
        try:
            with urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, OSError) as exc:
            raise UpdateError(f"PyPI'a ulasilamadi: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise UpdateError(f"PyPI yaniti cozumlenemedi: {exc}") from exc

        version = data.get("info", {}).get("version")
        if not version:
            raise UpdateError("PyPI yanitinda surum bilgisi bulunamadi.")

        wheel_entry = next(
            (f for f in data.get("urls", []) if f.get("packagetype") == "bdist_wheel"),
            None,
        )
        if not wheel_entry:
            raise UpdateError(f"{self.package_name} icin wheel (.whl) dosyasi bulunamadi.")

        digests = wheel_entry.get("digests") or {}
        return ReleaseInfo(
            version=version,
            wheel_url=wheel_entry["url"],
            sha256=digests.get("sha256"),
            size=wheel_entry.get("size"),
        )
