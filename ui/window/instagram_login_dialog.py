"""Instagram giriş penceresi — kullanıcının GERÇEK Chrome'unu sürerek oturum alır.

Gömülü QtWebEngine yerine, kullanıcının kurulu Chrome/Edge'ini ayrı bir profille
ve `--remote-debugging-port` ile açarız. Kullanıcı gerçek tarayıcıda normal giriş
yapar (passkey/Windows Hello/reCAPTCHA hepsi çalışır; Instagram bot saymaz). Biz
Chrome DevTools Protocol (CDP) üzerinden çalışan tarayıcının çerezlerini
HAFIZADAN okuruz (HttpOnly `sessionid` dahil) — diskteki App-Bound Encryption'a
(ABE, yt-dlp #10927) hiç dokunmadan. Çerezler yt-dlp'nin okuyacağı Netscape
`cookies.txt`'e yazılır.

CDP iletişimi PySide6'da gömülü `QtWebSockets` + `QtNetwork` ile yapılır — yeni
bağımlılık yok, QtWebEngine gerekmez.
"""

from __future__ import annotations

import json
import os
import socket
import subprocess

from PySide6.QtCore import QTimer, QUrl, Signal
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtWebSockets import QWebSocket
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from core.instagram import session as ig_session
from core.logger import get_logger

logger = get_logger("instagram_login")

_LOGIN_URL = "https://www.instagram.com/accounts/login/"
_POLL_JSON_MS = 800      # CDP HTTP endpoint / instagram page ws'i bulma araligi
_POLL_COOKIE_MS = 1500   # sessionid gelene kadar cerez yoklama araligi


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class InstagramLoginDialog(QDialog):
    """Gerçek Chrome'u açıp CDP ile Instagram oturum çerezlerini kaydeder."""

    session_saved = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Instagram Giriş")
        self.resize(460, 240)
        self._saved = False
        self._proc: subprocess.Popen | None = None
        self._port = 0
        self._cdp_id = 0
        self._net = QNetworkAccessManager(self)
        self._ws = QWebSocket()
        self._ws.connected.connect(self._on_ws_connected)
        self._ws.textMessageReceived.connect(self._on_ws_message)
        self._ws.errorOccurred.connect(self._on_ws_error)

        self._json_timer = QTimer(self)
        self._json_timer.setInterval(_POLL_JSON_MS)
        self._json_timer.timeout.connect(self._poll_json)
        self._cookie_timer = QTimer(self)
        self._cookie_timer.setInterval(_POLL_COOKIE_MS)
        self._cookie_timer.timeout.connect(self._request_cookies)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        info = QLabel(
            "Instagram girişi için tarayıcınız (Chrome/Edge) açılacak. Açılan "
            "pencerede hesabınıza normal şekilde giriş yapın.\n\n"
            "Giriş algılanınca bu pencere otomatik kapanır ve oturumunuz "
            "indirmeler için kaydedilir. Şifreniz uygulamada saklanmaz."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        self._status = QLabel("Başlatılıyor…")
        self._status.setWordWrap(True)
        layout.addWidget(self._status)
        layout.addStretch(1)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        self._btn_retry = QPushButton("Tarayıcıyı Yeniden Aç")
        self._btn_retry.clicked.connect(self._start_flow)
        button_row.addWidget(self._btn_retry)
        btn_cancel = QPushButton("Vazgeç")
        btn_cancel.clicked.connect(self.reject)
        button_row.addWidget(btn_cancel)
        layout.addLayout(button_row)

        self.finished.connect(self._cleanup)
        QTimer.singleShot(0, self._start_flow)

    # ---- akış ----
    def _start_flow(self):
        self._stop_browser()
        found = ig_session.find_browser_executable()
        if not found:
            self._status.setText(
                "Chrome veya Edge bulunamadı. Giriş için bu tarayıcılardan biri gerekli."
            )
            logger.warning("Tarayıcı bulunamadı (chrome/edge yok)")
            return
        name, exe = found
        self._port = _free_port()
        os.makedirs(ig_session.profile_dir(), exist_ok=True)
        try:
            self._proc = subprocess.Popen(
                [
                    exe,
                    f"--remote-debugging-port={self._port}",
                    f"--user-data-dir={ig_session.profile_dir()}",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--new-window",
                    _LOGIN_URL,
                ]
            )
        except OSError as exc:
            self._status.setText(f"Tarayıcı açılamadı: {exc}")
            logger.exception("Tarayıcı baslatilamadi")
            return
        logger.info("Tarayıcı acildi: %s port=%s", name, self._port)
        self._status.setText("Tarayıcı açıldı. Lütfen giriş yapın…")
        self._json_timer.start()

    def _poll_json(self):
        # CDP HTTP endpoint'ten instagram page hedefinin websocket url'sini bul.
        req = QNetworkRequest(QUrl(f"http://127.0.0.1:{self._port}/json"))
        reply = self._net.get(req)
        reply.finished.connect(lambda: self._on_json_reply(reply))

    def _on_json_reply(self, reply: QNetworkReply):
        try:
            if reply.error() != QNetworkReply.NetworkError.NoError:
                return
            raw = bytes(reply.readAll().data()).decode("utf-8", "ignore")
            pages = json.loads(raw)
        except (ValueError, UnicodeDecodeError):
            return
        finally:
            reply.deleteLater()
        ws_url = None
        for p in pages:
            if p.get("type") == "page" and "instagram.com" in p.get("url", ""):
                ws_url = p.get("webSocketDebuggerUrl")
                break
        if ws_url and self._ws.state().name == "UnconnectedState":
            self._json_timer.stop()
            logger.info("Instagram page CDP ws'e baglaniliyor")
            self._ws.open(QUrl(ws_url))

    def _on_ws_connected(self):
        self._cdp_id += 1
        self._ws.sendTextMessage(json.dumps({"id": self._cdp_id, "method": "Network.enable"}))
        self._status.setText("Giriş bekleniyor…")
        self._cookie_timer.start()
        self._request_cookies()

    def _request_cookies(self):
        if self._ws.state().name != "ConnectedState":
            return
        self._cdp_id += 1
        self._ws.sendTextMessage(json.dumps({"id": self._cdp_id, "method": "Network.getAllCookies"}))

    def _on_ws_message(self, msg: str):
        try:
            data = json.loads(msg)
        except ValueError:
            return
        result = data.get("result")
        if not isinstance(result, dict) or "cookies" not in result:
            return
        cookies = ig_session.cdp_cookies_to_netscape(result["cookies"])
        has_sessionid = any(name == "sessionid" and value.strip() for *_, name, value in cookies)
        if has_sessionid:
            self._save_and_close(cookies)

    def _save_and_close(self, cookies):
        if self._saved:
            return
        self._saved = True
        ig_session.write_netscape_cookies(cookies)
        logger.info("Instagram oturumu kaydedildi (%d cerez)", len(cookies))
        self._status.setText("Giriş kaydedildi.")
        self.session_saved.emit()
        self.accept()

    def _on_ws_error(self, *_args):
        # Kullanıcı tarayıcıyı kapatırsa ya da CDP kopar sa bilgilendir.
        if not self._saved:
            self._status.setText(
                "Tarayıcı bağlantısı koptu. 'Tarayıcıyı Yeniden Aç'a tıklayabilirsiniz."
            )

    # ---- temizlik ----
    def _stop_browser(self):
        self._json_timer.stop()
        self._cookie_timer.stop()
        if self._ws.state().name != "UnconnectedState":
            self._ws.close()
        if self._proc is not None:
            try:
                self._proc.terminate()
            except OSError:
                pass
            self._proc = None

    def _cleanup(self, *_args):
        self._stop_browser()
