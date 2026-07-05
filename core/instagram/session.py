"""Instagram oturum (çerez) saklama — saf, GUI'siz mantık.

Bu modül Qt import ETMEZ; testler GUI kurulu olmadan çalışabilir. Gerçek giriş
akışı (kullanıcının gerçek Chrome'unu CDP ile sürerek çerez okuma)
`ui/window/instagram_login_dialog.py` içindedir ve buradaki
`write_netscape_cookies`/`cookies_path`/`cdp_cookies_to_netscape` fonksiyonlarını
kullanarak yt-dlp'nin okuyacağı `cookies.txt` dosyasını üretir.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

_IG_COOKIE_DOMAINS = ("instagram.com", ".instagram.com")

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
    """CDP ile açılan Chrome için ayrı, kalıcı `--user-data-dir`.

    Kullanıcının ana Chrome profiline dokunmaz (CDP zaten ana profile
    remote-debugging bağlanmayı yasaklar) ve oturum burada kalıcı olur; ikinci
    girişte kullanıcı yeniden giriş yapmak zorunda kalmaz.
    """
    return _PROFILE_DIR


def find_browser_executable() -> tuple[str, str] | None:
    """Kurulu Chromium tabanlı tarayıcıyı bulur; `(ad, exe_yolu)` veya `None`.

    Chrome önce denenir (CDP + gerçek tarayıcı = Instagram bot saymaz), sonra
    Edge. Saf: yalnızca dosya sistemine bakar.
    """
    program_files = os.environ.get("PROGRAMFILES", r"C:\Program Files")
    program_files_x86 = os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")
    local_appdata = os.environ.get("LOCALAPPDATA", os.path.join(Path.home(), "AppData", "Local"))
    candidates = (
        ("chrome", os.path.join(program_files, "Google", "Chrome", "Application", "chrome.exe")),
        ("chrome", os.path.join(program_files_x86, "Google", "Chrome", "Application", "chrome.exe")),
        ("chrome", os.path.join(local_appdata, "Google", "Chrome", "Application", "chrome.exe")),
        ("edge", os.path.join(program_files, "Microsoft", "Edge", "Application", "msedge.exe")),
        ("edge", os.path.join(program_files_x86, "Microsoft", "Edge", "Application", "msedge.exe")),
    )
    for name, path in candidates:
        if os.path.isfile(path):
            return name, path
    return None


def cdp_cookies_to_netscape(cdp_cookies) -> list[tuple]:
    """CDP `Network.getAllCookies` çerezlerini `write_netscape_cookies` demetlerine çevirir.

    Yalnızca `.instagram.com` çerezleri alınır. Her CDP çerezi:
    `{name, value, domain, path, expires(float, -1=session), secure, httpOnly}`.
    Dönen: `(domain, path, secure, expiry, name, value)` demetleri (saf fonksiyon).
    """
    result: list[tuple] = []
    for c in cdp_cookies:
        domain = str(c.get("domain", ""))
        if not any(domain.endswith(d) or domain == d.lstrip(".") for d in _IG_COOKIE_DOMAINS):
            continue
        expires = c.get("expires", 0)
        expiry = int(expires) if isinstance(expires, (int, float)) and expires and expires > 0 else 0
        result.append(
            (
                domain,
                c.get("path", "/") or "/",
                bool(c.get("secure", False)),
                expiry,
                str(c.get("name", "")),
                str(c.get("value", "")),
            )
        )
    return result


def has_session() -> bool:
    """Geçerli bir Instagram oturumu (sessionid içeren cookies dosyası) var mı."""
    return _contains_sessionid(_COOKIES_PATH)


def clear_session(clear_profile: bool = True) -> None:
    """Kayıtlı oturumu siler (cookies dosyası + opsiyonel CDP tarayıcı profili)."""
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
