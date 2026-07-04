"""Instagram uygulama-içi giriş penceresi (gömülü QtWebEngine).

PyQtWebEngine SADECE bu modülde import edilir ve bu modül yalnızca kullanıcı
"Instagram Giriş" butonuna bastığında (lazy) import edilir. Böylece app
başlangıcı ve testler QtWebEngine'e bağımlı olmaz.

Akış: kullanıcı Instagram'ın GERÇEK login sayfasına girer (şifre uygulamada
tutulmaz). Motor seviyesindeki çerez deposu (`QWebEngineCookieStore`) HttpOnly
`sessionid` dahil tüm .instagram.com çerezlerini yakalar; dolu bir `sessionid`
görülünce çerezler yt-dlp'nin okuyacağı Netscape `cookies.txt`'e yazılır.
"""

from __future__ import annotations

import os

from PyQt5.QtCore import QTimer, QUrl, pyqtSignal
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineProfile, QWebEngineView

from core.instagram import session as ig_session

_LOGIN_URL = "https://www.instagram.com/accounts/login/"
_IG_DOMAINS = ("instagram.com", ".instagram.com")

# Gercek masaustu Chrome user-agent'i: QtWebEngine'in varsayilan UA'sinda
# "QtWebEngine" gecer ve Meta bunu bot sanip reCAPTCHA guvenlik duvari gosterir.
# Normal Chrome UA ile giris formu dogrudan gelir.
_DESKTOP_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
)


class InstagramLoginDialog(QDialog):
    """Instagram girişi yapıp oturum çerezlerini kaydeden modal pencere."""

    session_saved = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Instagram Giriş")
        self.resize(520, 700)
        self._cookies: dict[tuple[str, str], tuple] = {}
        self._saved = False
        self._load_attempts = 0
        self._max_attempts = 4

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        info = QLabel(
            "Instagram hesabınıza giriş yapın. Giriş bilgileriniz uygulamada "
            "saklanmaz; yalnızca oturum çerezi indirmeler için kaydedilir."
        )
        info.setWordWrap(True)
        info.setContentsMargins(12, 10, 12, 10)
        layout.addWidget(info)

        os.makedirs(ig_session.profile_dir(), exist_ok=True)
        # Kalici, adli profil: oturum tarayicida da yasasin (yeniden acinca girisli).
        self._profile = QWebEngineProfile("baglanti_indirici_instagram", self)
        self._profile.setPersistentStoragePath(ig_session.profile_dir())
        self._profile.setCachePath(os.path.join(ig_session.profile_dir(), "cache"))
        self._profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
        self._profile.setHttpUserAgent(_DESKTOP_USER_AGENT)

        self._cookie_store = self._profile.cookieStore()
        self._cookie_store.cookieAdded.connect(self._on_cookie_added)

        self._view = QWebEngineView(self)
        # Profil ile page olustur. ONEMLI: page'in parent'i PROFIL olmali - boylece
        # profil yok edilirken page ONCE silinir. Aksi halde "Release of profile
        # requested but WebEnginePage still not deleted. Expect troubles!" cikar ve
        # kapanista cokme riski olur.
        from PyQt5.QtWebEngineWidgets import QWebEnginePage
        self._page = QWebEnginePage(self._profile, self._profile)
        self._view.setPage(self._page)
        self._view.loadStarted.connect(self._on_load_started)
        self._view.loadFinished.connect(self._on_load_finished)
        layout.addWidget(self._view, stretch=1)
        # Kapanista page'i profilden once acikca temizle (kesin cozum).
        self.finished.connect(self._cleanup)

        button_row = QHBoxLayout()
        button_row.setContentsMargins(12, 8, 12, 12)
        self._status = QLabel("Giriş bekleniyor…")
        button_row.addWidget(self._status, stretch=1)
        btn_logout = QPushButton("Çıkış Yap")
        btn_logout.clicked.connect(self._on_logout)
        button_row.addWidget(btn_logout)
        self._btn_reload = QPushButton("Yeniden Yükle")
        self._btn_reload.clicked.connect(self._start_load)
        button_row.addWidget(self._btn_reload)
        layout.addLayout(button_row)

        # Ilk yuklemeyi event loop basladiktan SONRA tetikle: dogrudan __init__
        # icinde load() bazen "sayfaya erisilemiyor" ile basarisiz oluyor.
        QTimer.singleShot(0, self._start_load)

    def _start_load(self):
        self._load_attempts += 1
        self._status.setText("Sayfa yükleniyor…")
        self._view.load(QUrl(_LOGIN_URL))

    def _on_load_started(self):
        self._status.setText("Sayfa yükleniyor…")

    def _on_load_finished(self, ok: bool):
        if ok:
            self._load_attempts = 0
            self._status.setText("Giriş bekleniyor…")
            return
        if self._load_attempts < self._max_attempts:
            self._status.setText(
                f"Sayfaya ulaşılamadı, yeniden deneniyor… ({self._load_attempts}/{self._max_attempts})"
            )
            QTimer.singleShot(1500, self._start_load)
        else:
            self._status.setText("Sayfaya ulaşılamadı. 'Yeniden Yükle'ye tıklayın veya interneti kontrol edin.")

    def _on_cookie_added(self, cookie):
        domain = bytes(cookie.domain()).decode("utf-8", "ignore")
        if not any(domain.endswith(d) or domain == d.lstrip(".") for d in _IG_DOMAINS):
            return
        name = bytes(cookie.name()).decode("utf-8", "ignore")
        value = bytes(cookie.value()).decode("utf-8", "ignore")
        path = bytes(cookie.path()).decode("utf-8", "ignore") or "/"
        secure = cookie.isSecure()
        expiry = 0
        expiration = cookie.expirationDate()
        if expiration.isValid():
            expiry = int(expiration.toSecsSinceEpoch())
        self._cookies[(domain, name)] = (domain, path, secure, expiry, name, value)

        if name == "sessionid" and value.strip():
            self._save_and_close()

    def _save_and_close(self):
        if self._saved:
            return
        self._saved = True
        ig_session.write_netscape_cookies(list(self._cookies.values()))
        self._status.setText("Giriş kaydedildi.")
        self.session_saved.emit()
        self.accept()

    def _on_logout(self):
        ig_session.clear_session()
        self._cookies.clear()
        self._status.setText("Oturum temizlendi.")

    def _cleanup(self, *_args):
        # Page'i view'dan ayirip profilden ONCE sil (lifecycle uyarisi/cokme onlemi).
        try:
            self._view.stop()
            self._view.setPage(None)
            if self._page is not None:
                self._page.deleteLater()
                self._page = None
        except RuntimeError:
            pass  # zaten silinmisse
