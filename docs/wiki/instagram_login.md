# Instagram Giriş (Kullanıcının Gerçek Chrome'u + CDP)

Bkz. [[index]] · İlgili: [[hata_yonetimi_ve_loglama]], [[yt_dlp_oto_guncelleme]], [[paketleme]], [[mimari]]

## Problem

Instagram, 2-3 Temmuz 2026'da API'sini değiştirip reels/gönderiler için giriş (login) zorunlu hale getirdi (detay: [[hata_yonetimi_ve_loglama]] "Instagram Login Duvarı"). Login-gerekli içerik, geçerli oturum çerezi olmadan hiçbir yolla inmiyor. İki teknik engel var:

1. **`sessionid` çerezi HttpOnly** — JavaScript / `document.cookie` ile okunamaz; motor seviyesinde çerez erişimi gerekir.
2. **Chrome App-Bound Encryption (ABE, v127+)** — diskteki çerezleri DPAPI üstü bir katmanla şifreler; yt-dlp bunu çözemez (#10927, "Failed to decrypt with DPAPI"). Bu makinede hem Chrome hem Edge için çözme başarısız oluyor.

## Çözüm: Kullanıcının GERÇEK tarayıcısını CDP ile sür

Gömülü tarayıcı **kullanılmaz**. Uygulama, kullanıcının kurulu Chrome (yoksa Edge) tarayıcısını **ayrı bir profille** ve `--remote-debugging-port` ile açar. Kullanıcı gerçek tarayıcıda normal giriş yapar — passkey / Windows Hello / reCAPTCHA / WebAuthn hepsi çalışır ve Instagram bunu bot saymaz (gerçek Chromium, gerçek parmak izi). Uygulama, çalışan tarayıcının çerezlerini **Chrome DevTools Protocol (CDP)** ile HAFIZADAN okur (HttpOnly `sessionid` dahil) — diske ve ABE'ye hiç dokunmadan.

Kullanıcı **bir kez** giriş yapar; profil kalıcı olduğundan sonraki açılışlarda tekrar giriş gerekmez.

### Neden gömülü QtWebEngine terk edildi
İlk iki deneme başarısız oldu: (1) PyQt5 QtWebEngine (Qt 5.15, Chromium ~87) reCAPTCHA'ya takıldı; (2) PySide6 QtWebEngine (Qt6, güncel Chromium) da Instagram'ın **risk-tabanlı giriş zorlaması** (`is_from_rle` → passkey/WebAuthn adımı) duvarını geçemedi — gömülü motor WebAuthn yapamıyor ("user agent does not support public key credentials") ve doğrudan login'e geri atıyordu. Kullanıcının **kendi** tarayıcısı bu adımların hepsini doğal olarak geçtiği için tek sağlam yol bu oldu. Proje yine PySide6 (Qt6); ama artık **QtWebEngine kullanılmıyor** — CDP için gereken `QtWebSockets` + `QtNetwork` PySide6-Essentials içinde gelir, yeni bağımlılık yok.

### Akış (CDP)
1. `find_browser_executable()` → `chrome.exe` (tercih) yoksa `msedge.exe`.
2. `subprocess.Popen([exe, --remote-debugging-port=PORT, --user-data-dir=profile_dir(), --no-first-run, --no-default-browser-check, --new-window, LOGIN_URL])`.
   - **Ayrı `--user-data-dir` şart:** Chrome ~2024'ten beri çalışan varsayılan profile remote-debugging bağlanmayı yasaklar. Ayrı profil hem bunu çözer hem kullanıcının ana profiline dokunmaz hem oturumu kalıcı kılar.
3. `QNetworkAccessManager` ile `http://127.0.0.1:PORT/json` yoklanır (`_json_timer`, 800ms) → içinde "instagram.com" olan `page` hedefinin `webSocketDebuggerUrl`'i bulunur.
   - **Önemli:** tarayıcı-seviyesi (`/json/version`) `getAllCookies` 0 çerez döner; **page hedefine** bağlanmak şart.
4. `QWebSocket` o page hedefine bağlanır → `Network.enable` → `Network.getAllCookies` (`_cookie_timer`, 1500ms poll).
5. Sonuçtaki çerezler `cdp_cookies_to_netscape()` ile süzülür/dönüştürülür; dolu bir `sessionid` görülünce `write_netscape_cookies()` ile `cookies.txt`'e yazılır, pencere kapanır, `session_saved` sinyali yayılır.

### Bileşenler

- **`core/instagram/session.py`** (saf, GUI'siz — test edilebilir; Qt import ETMEZ):
  - `cookies_path()` → `~/.baglanti_indirici/instagram_cookies.txt` (hassas veri: exe yanı değil kullanıcı profili).
  - `profile_dir()` → `~/.baglanti_indirici/webprofile` — CDP ile açılan Chrome'un `--user-data-dir`'i (kalıcı oturum).
  - `find_browser_executable()` → `(ad, exe_yolu)` veya `None`; PROGRAMFILES / PROGRAMFILES(X86) / LOCALAPPDATA altında chrome.exe (önce) sonra msedge.exe arar.
  - `cdp_cookies_to_netscape(cdp_cookies)` → CDP çerezlerini (`{name,value,domain,path,expires,secure,httpOnly}`) yalnızca `.instagram.com` için `(domain, path, secure, expiry, name, value)` demetlerine çevirir; `expires` ≤0 (session) → expiry 0.
  - `has_session()` → cookies dosyasında dolu bir `sessionid` satırı var mı.
  - `clear_session()` → cookies dosyası + CDP profilini siler.
  - `write_netscape_cookies(cookies, path)` → yt-dlp'nin okuduğu Netscape `cookies.txt` (saf fonksiyon).
  - `INSTAGRAM_LOGIN_REQUIRED_MSG` — login duvarı mesajının **tek kaynağı** (`yt_dlp_client._friendly_error` + `controller._handle_failed_job`).
- **`ui/window/instagram_login_dialog.py`** (`InstagramLoginDialog(QDialog)`, GUI): yukarıdaki CDP akışını sürer. `QNetworkAccessManager` + `QWebSocket` + iki `QTimer`. UI: bilgi etiketi, durum etiketi, "Tarayıcıyı Yeniden Aç" + "Vazgeç". Pencere kapanınca `_cleanup` timer'ları durdurur, ws'i kapatır, tarayıcı sürecini `terminate` eder.
- **`core/download/yt_dlp_client.py::build_options()`**: `request.platform == "Instagram"` ve `has_session()` ise `options["cookiefile"] = cookies_path()`.
- **UI/Controller**: Header'da "Instagram Giriş" butonu (`main_window._open_instagram_login`, oturum varsa etiket "Instagram ✓"). `controller._handle_failed_job` login duvarına takılınca yönlendirir; oturum dolmuşsa `clear_session()` + yeniden giriş.

### Güvenlik
- Uygulama Instagram **şifresini asla görmez/saklamaz** — kullanıcı, kendi tarayıcısında Instagram'ın gerçek login sayfasına yazar.
- Saklanan `cookies.txt` = geçerli oturum token'ı (hesaba erişim sağlar). Kullanıcı profili dizininde tutulur; `clear_session()` ile temizlenir.
- `--user-data-dir` ayrı profil olduğundan uygulama kullanıcının günlük Chrome profiline/verisine erişmez.

## Paketleme Etkisi

QtWebEngine artık kullanılmadığından CDP yolu paketleme açısından hafiftir (`QtWebSockets`/`QtNetwork` Essentials'ta). Build hâlâ **onedir** (mevcut installer akışı klasörü paketliyor). Detay: [[paketleme]].

## Testler

`tests/test_instagram_session.py` — Netscape format, `has_session`/`clear_session`, `sessionid` tespiti, `cdp_cookies_to_netscape` süzme/dönüşüm, roundtrip, `find_browser_executable` (chrome tercihi + yok durumu). `tests/test_yt_dlp_client.py` — Instagram + oturum varken `cookiefile` ekleniyor. CDP giriş akışı (gerçek Chrome + ağ) manuel doğrulanır — 5 Temmuz 2026'da uçtan uca doğrulandı (login → reels indi).
