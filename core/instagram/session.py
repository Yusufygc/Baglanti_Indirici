"""Instagram oturum (çerez) saklama — saf, GUI'siz mantık.

Bu modül PyQt/PyQtWebEngine import ETMEZ; testler GUI kurulu olmadan çalışabilir.
Gerçek giriş penceresi (QtWebEngine) `ui/window/instagram_login_dialog.py`
içindedir ve buradaki `write_netscape_cookies`/`cookies_path` fonksiyonlarını
kullanarak yt-dlp'nin okuyacağı `cookies.txt` dosyasını üretir.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

# Login duvarı mesajı — tek kaynak. Hem core/download/yt_dlp_client.py
# (_friendly_error) hem ui/window/controller.py (otomatik yönlendirme) kullanır.
INSTAGRAM_LOGIN_REQUIRED_MSG = (
    "Instagram bu içerik için giriş (login) yapılmasını istiyor. "
    "Herkese açık olmayan gönderiler artık giriş yapmadan indirilemiyor."
)

_BASE_DIR = os.path.join(Path.home(), ".baglanti_indirici")
_COOKIES_PATH = os.path.join(_BASE_DIR, "instagram_cookies.txt")
_PROFILE_DIR = os.path.join(_BASE_DIR, "webprofile")


def cookies_path() -> str:
    """yt-dlp'ye `cookiefile` olarak verilecek Netscape cookies.txt yolu."""
    return _COOKIES_PATH


def profile_dir() -> str:
    """QWebEngineProfile kalıcı depolama dizini (oturum tarayıcıda da yaşasın)."""
    return _PROFILE_DIR


def has_session() -> bool:
    """Geçerli bir Instagram oturumu (sessionid içeren cookies dosyası) var mı."""
    return _contains_sessionid(_COOKIES_PATH)


def clear_session(clear_profile: bool = True) -> None:
    """Kayıtlı oturumu siler (cookies dosyası + opsiyonel WebEngine profili)."""
    try:
        if os.path.isfile(_COOKIES_PATH):
            os.remove(_COOKIES_PATH)
    except OSError:
        pass
    if clear_profile:
        shutil.rmtree(_PROFILE_DIR, ignore_errors=True)


def write_netscape_cookies(cookies, path: str | None = None) -> str:
    """Çerezleri Netscape `cookies.txt` formatında yazar.

    `cookies`: `(domain, path, secure, expiry, name, value)` demetleri/dizileri.
    yt-dlp `cookiefile` seçeneği tam olarak bu formatı okur.
    """
    target = path or _COOKIES_PATH
    os.makedirs(os.path.dirname(target), exist_ok=True)
    lines = ["# Netscape HTTP Cookie File", "# baglanti_indirici tarafindan olusturuldu", ""]
    for domain, cookie_path, secure, expiry, name, value in cookies:
        include_subdomains = "TRUE" if str(domain).startswith(".") else "FALSE"
        secure_flag = "TRUE" if secure else "FALSE"
        expiry_field = str(int(expiry)) if expiry else "0"
        lines.append(
            "\t".join(
                [
                    domain,
                    include_subdomains,
                    cookie_path or "/",
                    secure_flag,
                    expiry_field,
                    name,
                    value,
                ]
            )
        )
    with open(target, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    return target


def _contains_sessionid(path: str) -> bool:
    if not os.path.isfile(path):
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("#") or not line.strip():
                    continue
                fields = line.rstrip("\n").split("\t")
                # Netscape formatı: ... name(6.), value(7.)
                if len(fields) >= 7 and fields[5] == "sessionid" and fields[6].strip():
                    return True
    except OSError:
        return False
    return False
