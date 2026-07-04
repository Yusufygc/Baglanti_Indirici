# Instagram Uygulama-İçi Giriş (Gömülü QtWebEngine)

Bkz. [[index]] · İlgili: [[hata_yonetimi_ve_loglama]], [[yt_dlp_oto_guncelleme]], [[paketleme]], [[mimari]]

## Problem

Instagram, 2-3 Temmuz 2026'da API'sini değiştirip reels/gönderiler için giriş (login) zorunlu hale getirdi (detay: [[hata_yonetimi_ve_loglama]] "Instagram Login Duvarı"). Login-gerekli içerik, geçerli oturum çerezi olmadan hiçbir yolla inmiyor. Tarayıcıdan otomatik çerez okuma güvenilmez: Chrome v127+ çerezleri "Application-Bound Encryption" ile şifreliyor (yt-dlp #10927, çözülmemiş), Firefox her makinede kurulu değil.

## Çözüm: Gömülü Giriş Penceresi + Kalıcı Oturum

Kullanıcı, uygulama içinde **bir kez** Instagram'a giriş yapar; oturum saklanır ve sonraki indirmelerde otomatik kullanılır — tekrar giriş gerekmez (Instagram oturumu doğal olarak sonlanana kadar).

### Neden QtWebEngine şart
Instagram'ın `sessionid` çerezi **HttpOnly** — JavaScript / `document.cookie` ile okunamaz. Motor seviyesinde çerez erişimi gerekir. `QWebEngineProfile.cookieStore()` HttpOnly çerezleri de yakalayabildiği için gömülü `QtWebEngine` kullanılır (WebView2/pywebview gibi hafif alternatifler HttpOnly yüzünden çalışmaz). Uygulama zaten PyQt5; `PyQtWebEngine` doğal entegrasyon.

### Bileşenler

- **`core/instagram/session.py`** (saf, GUI'siz — test edilebilir; PyQt import etmez):
  - `cookies_path()` → `~/.baglanti_indirici/instagram_cookies.txt` (hassas veri: exe yanı değil kullanıcı profili — `core/settings.py` konvansiyonu).
  - `profile_dir()` → `~/.baglanti_indirici/webprofile` (QWebEngineProfile kalıcı depolama).
  - `has_session()` → cookies dosyasında dolu bir `sessionid` satırı var mı.
  - `clear_session()` → cookies dosyası + WebEngine profilini siler.
  - `write_netscape_cookies(cookies, path)` → çerezleri yt-dlp'nin okuduğu Netscape `cookies.txt` formatında yazar (saf fonksiyon).
  - `INSTAGRAM_LOGIN_REQUIRED_MSG` — login duvarı mesajının **tek kaynağı** (hem `yt_dlp_client._friendly_error` hem `controller._handle_failed_job` kullanır).
- **`ui/window/instagram_login_dialog.py`** (`InstagramLoginDialog(QDialog)`, GUI): PyQtWebEngine SADECE burada ve **lazy** import edilir (buton tıklanınca). Kalıcı `QWebEngineProfile` (`ForcePersistentCookies`) + `QWebEngineView` ile Instagram login sayfası yüklenir. `cookieStore().cookieAdded` sinyaliyle `.instagram.com` çerezleri toplanır; dolu bir `sessionid` görülünce hepsi `cookies.txt`'e yazılıp pencere kapanır.
- **`core/download/yt_dlp_client.py::build_options()`**: `request.platform == "Instagram"` ve `has_session()` ise `options["cookiefile"] = cookies_path()` eklenir.
- **UI/Controller**: Header'da "Instagram Giriş" butonu (`main_window._open_instagram_login`, oturum varsa etiket "Instagram ✓"). Ayrıca `controller._handle_failed_job` login duvarına takılınca kullanıcıyı yönlendirir; oturum varsa ama yine takıldıysa (süresi dolmuş) `clear_session()` çağırıp yeniden giriş ister.

### Güvenlik
- Uygulama Instagram **şifresini asla görmez/saklamaz** — kullanıcı Instagram'ın gerçek login sayfasına yazar.
- Saklanan `cookies.txt` = geçerli oturum token'ı (hesaba erişim sağlar). Kullanıcı profili dizininde tutulur. Bu tür araçlarda standart; `clear_session()` / "Çıkış Yap" ile temizlenebilir.

## Başlangıç Gereksinimi

`main.py`'de `QApplication` oluşturulmadan **önce** `QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)` çağrılır — QtWebEngine bu olmadan açılırken çökebilir. QtWebEngine yalnızca giriş penceresi açıldığında yüklenir (lazy); app başlangıcı hafif kalır.

## Paketleme Etkisi

QtWebEngine yüzünden build **onedir**'e geçti (onefile'da QtWebEngineProcess.exe güvenilmez). Detay: [[paketleme]].

## Testler

`tests/test_instagram_session.py` — Netscape format, `has_session`/`clear_session`, `sessionid` tespiti. `tests/test_yt_dlp_client.py` — Instagram + oturum varken `cookiefile` ekleniyor, yoksa/başka platformda eklenmiyor. Giriş penceresi (QtWebEngine + ağ) manuel doğrulanır.
