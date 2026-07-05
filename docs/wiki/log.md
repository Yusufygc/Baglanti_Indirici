# Değişiklik Günlüğü

Kronolojik kayıt, en yeni en üstte. Format: `## [YYYY-AA-GG] [İŞLEM_TİPİ] | Kısa Açıklama`

## [2026-07-05] FIX | Kompakt bubble: tamamlanma geri bildirimi yanlis sinyale bagliydi, yesil/kirmizi cember yapildi

Onceki FIX'te eklenen "indirme tamamlaninca tik" ozelligi **hic calismiyordu**: `MainWindow.handle_finished`'a baglanmisti ama bu metod **hicbir yerde `.connect()` edilmiyor** — olu kod. Gercek tamamlanma akisi `MainWindowController._on_job_updated(job)` (`job.status` kontrolu ile `self.view.set_status(...)` cagirir), tamamen farkli bir yol. Kok neden: mimari yanlis anlasilmis, yanlis metoda kanca atilmis.

Cozum + kullanici istegi dogrultusunda gelistirme: `_on_job_updated`'a `JobStatus.COMPLETED` -> `self.view.flash_compact_result(True)`, `JobStatus.FAILED` -> `self.view.flash_compact_result(False)` eklendi (controller.py). `MainWindow.flash_compact_result` bubble goruluyorsa `CompactBubble.flash_result(success)` cagirir. Bubble tarafinda `flash_success()` -> `flash_result(bool)` oldu: **cemberin arkaplan rengi** basaridaysa yesil (`LOG_COLORS["success"]`), basarisizsa kirmizi (`LOG_COLORS["error"]`) olur (+ tik/carpi glifi, beyaz - hem yesil hem kirmizi zeminde okunur), `_SUCCESS_MS` (1.6sn) sonra normal accent rengine doner. `paintEvent` artik `self._flash_color or self._accent_color` kullanir.

Gercek `MainWindowController._on_job_updated` cagirilarak (mock degil, GERCEK kod yolu) dogrulandi: COMPLETED -> `#2ecc71` (yesil), FAILED -> `#ff4757` (kirmizi), restore -> `None` (normale doner). 62 test etkilenmedi.

## [2026-07-05] FIX | Kompakt bubble: surukleme kalici olsun, kucuk ikon, indirme tamamlaninca tik

Kullanici geri bildirimi uzerine [[kompakt_mod]] duzeltildi:

1. **Surukleyip birakinca eski konuma sicrama (kok neden bulundu):** ikonu tutmak icin uzerine gelmek zaten `enterEvent` ile hover-genislemeyi tetikliyor; kullanici surukleyip biraktiktan sonra fare ayrilinca `_collapse()` surukleme ONCESI konuma (statik `_collapsed_pos` onbellegi) donuyordu. Cozum: statik onbellek kaldirildi, konum HER ZAMAN `mapToGlobal(icon.pos())` ile canli hesaplanir (`_icon_global_pos()`); artik ikon ekranda gercekten HERHANGI bir yere suruklenip birakilabiliyor, sonraki hover/collapse dongusu o konumu korur.
2. **Ikon boyutu kucultuldu:** daraltilmis daire 56px -> 40px (ikon pixmap 28->20). Kucultme sirasinda ikinci bir gizli bug bulundu: collapse animasyonu bitene kadar URL input'u GORUNUR tutuluyordu, QLineEdit'in kendi minimum genisligi pencerenin hedef 40px'e kucalmasini engelleyip ~90px'te kilitliyordu (layout min-size clamp). Cozum: input artik animasyon BASLAMADAN ONCE gizleniyor.
3. **Indirme tamamlaninca gorsel geri bildirim:** `MainWindow.handle_finished` artik bubble goruluyorsa `CompactBubble.flash_success()` cagirir - ikon 1.6sn boyunca tik (✓) gosterir, sonra otomatik normal app ikonuna doner.

Sol-genisleme (ekran kenari) durumu icin layout sirasi (`_set_layout_order`) dinamik olarak ters cevrilip ikonun anchor konumu HER durumda sabit kaliyor. Script ile dogrulandi: surukle->birak->collapse tam beklenen (x,y,40,40) konuma donuyor (eskiden 90px'te kiliteleniyordu). 62 test etkilenmedi.

## [2026-07-05] FEATURE | Kompakt mod (yuvarlak bubble + hover-expand URL girisi)

Yeni `ui/window/compact_bubble.py::CompactBubble` — header'daki yeni "◎" butonuyla ana pencere gizlenip yerine kucuk (56x56), her zaman ustte, surunebilir yuvarlak bir bubble gosterilir. Fare uzerine gelince hap sekline genisleyip bir URL girisi acar; Enter'a basinca `MainWindow._start_download()` (ayni yol, sifir tekrar) cagrilir, o an ayarli format/klasor/dosya adiyla indirme otomatik baslar. Cift tiklama tam pencereye donusu tetikler.

Teknik not: QSS `border-radius`/`background-color` ile denenen ilk yaklasim, ust-duzey frameless+`WA_TranslucentBackground` pencerede resize-animasyonu sonrasi genisleyen alani boyamiyordu (sag taraf seffaf kaliyordu) — cozum: dolgu `paintEvent` ile elle `QPainter.drawRoundedRect` ile cizildi (her resize'da yeniden boyanir, cache sorunu yok). Ayrica layout margin tuzagi bulundu: sag bosluk layout `setContentsMargins`'e konursa input gizliyken bile genisligi sisirip daireyi ovale ceviriyordu (56->70px), duzeltme: bosluk `#compactUrlInput` QSS padding'ine tasindi.

Ekran-goruntusu ile dogrulandi (daraltilmis tam daire, genisletilmis dolu hap sekli) + gercek `MainWindow`+`CompactBubble` uctan uca script testi (kompakt moda gecis, URL gonderimi ile dogru is kuyruga eklenmesi, restore). 62 test etkilenmedi. Detay: [[kompakt_mod]].

## [2026-07-05] FIX | YouTube format secimi dusuk kalitede takiliyordu (format string sirasi)

`core/platform/registry.py::youtube_format_policy` format string'i `"best[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best"` idi. yt-dlp `/` ile ayrilan secenekleri SOLDAN SAGA dener ve ilk ESLESENI kullanir (en yukseginı degil). YouTube neredeyse her zaman dusuk cozunurluklu (~360-720p) bir progressive (video+ses birlesik) mp4 sundugundan `best[ext=mp4]` hep ilk eslesip seciliyordu; asil yuksek cozunurluklu (1080p/4K) ayrik video+ses (DASH) akislarina hic dusulmuyordu. Ozellikle Shorts'ta belirgindi (dusuk format 18/360p secilirdi).

Cozum: sira ters cevrildi -> `"bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"`. Once gercek en-yuksek ayrik akislar denenir (ffmpeg zaten projede var, merge sorunsuz), yalnizca uygun DASH akisi yoksa progressive'e/best'e duser.

Dogrulama (gercek Shorts URL, `simulate=True`): eski siralama `format 18 (360p, avc1, progressive)` seciyordu; yeni siralama `399 (yuksek cozunurluk, av01, video-only) + 140 (m4a, audio-only)` seciyor (merge edilir). Not: `DownloadOptions.quality` alani (`core/domain/models.py`) hala kullanilmiyor/dead — kullaniciya kalite secimi acan bir UI yok, ayri bir gorev.

## [2026-07-05] CHANGE | Aktif font profili "system" (Segoe UI) yapildi (kullanici tercihi)

PyQt5->PySide6 (Qt5->Qt6) gecisi font RENDER'ini degistirdi: eski Qt5'te variable font `Inter Variable` yuklenmeyip UI Segoe UI'a dusuyordu (statik `JetBrains Mono` ise yukleniyordu); Qt6 gercek Inter'i uyguladigi icin gorunum degisti. Kullanici eski (Segoe UI) gorunumu istedi. `font_profiles.py`'ye `system` profili eklendi (`ui_families=("Segoe UI",)`, `mono_families=("JetBrains Mono","Consolas")`) ve `ACTIVE_FONT_PROFILE="system"` yapildi — eski gorunum birebir. Diger profiller (modern/elegant/classic/playful) korundu. Not: font AILELERI/dosyalari degistirilmedi, yalnizca aktif profil; `font_manager.py`'ye kisa sure eklenen tani logu geri alindi.

## [2026-07-05] FIX | yt-dlp guncelleme kullanici dizinine yazsin + durum cubugu tasmasi

Kurulu exe'de iki sorun: (1) **yt-dlp oto-guncelleme `[WinError 5] Erisim engellendi`** veriyordu — guncelleyici exe-yani `lib/yt_dlp`'ye (Program Files, salt-okunur) yaziyordu. Cozum: `core/config.py::get_yt_dlp_update_dir()` eklendi; guncelleme her zaman yazilabilir `~/.baglanti_indirici/lib`'e yazilir, `get_yt_dlp_lib_dir()` bu dizini gomulu (exe-yani) kopyaya gore ONCELIKLI okur (`update/worker.py` hedefi degistirildi). Uctan uca dogrulandi: 2026.7.4 indirildi/kuruldu. (2) **Durum cubugu yazilari ust uste biniyordu** ("yazilar bozulmus") — uzun guncelleme/hata metni dar pencerede butonla/versiyonla cakisiyordu. Cozum: `lbl_status_bar` yatayda `QSizePolicy.Ignored` + stretch (metin layout'u itmez, kirpilir), guncelleme mesaji kisaltildi, `set_status` uzun metni `QFontMetrics.elidedText` ile "…" yapiyor (tam metin tooltip'te). Not: fontlar ASLINDA saglamdi (`Inter Variable` yukleniyor — log ile dogrulandi); "bozuk" gorunen durum cubugu tasmasiydi. `font_manager.py`'ye tani logu eklendi. Detay: [[yt_dlp_oto_guncelleme]], [[hata_yonetimi_ve_loglama]].

## [2026-07-05] FIX | PySide6 6.8 LTS'e sabitlendi (derlenen exe acilista QtWidgets DLL cokmesi)

PyInstaller ile derlenen exe acilista `ImportError: DLL load failed while importing QtWidgets: Belirtilen yordam bulunamadi` (procedure not found) ile cokuyordu. Teshis: venv'de import sorunsuz, bundle DLL/pyd dosyalari venv ile birebir ayni (sha256 SAME), tek tek yukleniyor — ama frozen calisma aninda shiboken/Qt6 baglamasi initialize olamiyordu. Kok neden: **PySide6 6.11.1 (bleeding-edge) + PyInstaller 6.21 uyumsuzlugu**. Cozum: PySide6 6.8 LTS'e (6.8.3) dusuruldu; `requirements.txt` `PySide6>=6.8,<6.9` olarak sabitlendi. 62 test geciyor, frozen exe temiz aciliyor (log: "Uygulama basladi"). Not: PyQt5 kalintisi (`~yqt5` bozuk dist-info) da venv'den temizlendi. Detay: [[paketleme]], [[mimari]].

## [2026-07-05] FIX | Loglar kullanici-yazilabilir dizine (Program Files kurulumunda acilis cokmesi)

Inno Setup installer ile Program Files'a kurulan exe acilista `PermissionError [WinError 5]` ile cokuyordu: `core/logger.py` log klasorunu `get_base_path()` (exe yani = `C:\Program Files\Baglanti Indirici\logs`) altinda acmaya calisiyordu, Program Files yazilamaz. Cozum: `core/config.py`'ye `get_user_data_dir()` (`~/.baglanti_indirici`) eklendi; loglar artik oraya yaziliyor — ayarlar (`settings.py`), gecmis (`history/repository.py`) ve Instagram oturumu (`session.py`) ile ayni kok. Detay: [[hata_yonetimi_ve_loglama]], [[paketleme]].

## [2026-07-05] FEATURE | Instagram login: gomulu QtWebEngine terk, kullanicinin gercek Chrome'u + CDP

Gomulu tarayici (once PyQt5, sonra PySide6 QtWebEngine) Instagram giris duvarini gecemedi: PyQt5 reCAPTCHA'ya, PySide6 Qt6 ise risk-tabanli giris zorlamasina (`is_from_rle` -> passkey/WebAuthn; gomulu motor WebAuthn yapamiyor) takildi, dogrudan login'e geri atiyordu. Kesin cozum: gomulu tarayiciyi tamamen birak, kullanicinin **kendi kurulu Chrome/Edge**'ini ayri bir `--user-data-dir` + `--remote-debugging-port` ile ac; kullanici gercek tarayicida normal giris yapar (passkey/reCAPTCHA hepsi calisir), uygulama **Chrome DevTools Protocol** (CDP) ile calisan tarayicinin cerezlerini HAFIZADAN okur (HttpOnly `sessionid` dahil) — diskteki App-Bound Encryption'a (ABE, yt-dlp #10927) hic dokunmadan. CDP icin `QtWebSockets`+`QtNetwork` (PySide6-Essentials) kullanilir; QtWebEngine artik kullanilmiyor. `instagram_login_dialog.py` bastan yazildi (CDP surucusu); `session.py`'ye `find_browser_executable()` + `cdp_cookies_to_netscape()` eklendi; `main.py`'den QtWebEngine'e ozel `AA_ShareOpenGLContexts` kaldirildi. 62 test geciyor. **5 Temmuz 2026: uctan uca dogrulandi — login basarili, login-gerekli reels indi.** Detay: [[instagram_login]], [[paketleme]], [[mimari]].

## [2026-07-05] REFACTOR | Tum proje PyQt5 -> PySide6'ya tasindi (Qt6)

Gomulu PyQt5 QtWebEngine login, Meta reCAPTCHA'sini gecemedi (PyQt5 Qt 5.15'e / Chromium ~87'ye kilitli). Ilk plan: tum projeyi PySide6'ya (Qt6, guncel Chromium) tasiyip gomulu login'i yeni motorla denemek. 8 dosya: import swap (`PyQt5` -> `PySide6`), `pyqtSignal`->`Signal`, `pyqtSlot`->`Slot`, `.exec_()`->`.exec()`, `QFontDatabase` statik cagri. Bagimlilik: `PyQt5`/`PyQtWebEngine` kaldirildi, `PySide6>=6.8` eklendi. (Not: Qt6 QtWebEngine de giris duvarini gecemedi; nihai cozum icin ustteki CDP girisine bakiniz — PySide6 gecisi kalici oldu, gomulu QtWebEngine ise terk edildi.) Detay: [[mimari]].

## [2026-07-04] FEATURE | Instagram uygulama-ici login (gomulu QtWebEngine) + kalici oturum

Instagram login duvari icin gercek cozum: uygulama-ici gomulu QtWebEngine giris penceresi. Kullanici bir kez giris yapar (sifre uygulamada tutulmaz), oturum cerezleri (HttpOnly sessionid dahil) yakalanip Netscape cookies.txt'e yazilir, yt-dlp'ye `cookiefile` olarak verilir. Yeni: `core/instagram/session.py` (saf), `ui/window/instagram_login_dialog.py` (QtWebEngine, lazy import). Header'a "Instagram Giris" butonu; login duvarina takilan indirmede controller otomatik yonlendiriyor (oturum dolmussa temizleyip yeniden giris istiyor). QtWebEngine icin `main.py`'de `AA_ShareOpenGLContexts` + build **onedir**'e gecti (onefile'da QtWebEngine guvenilmez), `installer.iss` tum klasoru paketliyor. `PyQtWebEngine` bagimliligi eklendi. Detay: [[instagram_login]], [[paketleme]].

## [2026-07-04] FIX | Gecmis sadece tamamlananlar, iptal kalintisi temizligi, Enter ile kuyruga alma

Kullanici istekleri: (1) basarisiz/iptal isler gecmise dusmesin - `HistoryRepository.list_recent()` SQL'de `WHERE status='completed'` ile filtrelendi, `render_history()` de sadece COMPLETED gosteriyor. (2) Enter ile kuyruga alma - `url_input` ve `filename_input`'a `returnPressed -> _start_download` baglandi. (3) Iptal edilen isin kalintisi silinsin - `DownloadQueueService.mark_cancelled()` isi bellekten ve gecmis DB'sinden (yeni `HistoryRepository.delete()`) tamamen siliyor; ayrica `DownloadEngine` progress hook'ta yt-dlp `tmpfilename`/`filename` yollarini biriktirip `CancelledDownload`'da `.part`/`.ytdl`/`.temp`/fragment dosyalarini indirilenler klasorunden siliyor (bozuk dosya kalmiyor). Detay: [[mimari]] "Kuyruk ve Gecmis Semantigi".

## [2026-07-04] FIX | Instagram cookie kodu geri alindi, gercek kok neden Instagram API degisikligi

"Instagram reels inmiyor" raporu derinlemesine incelendi. Bu oturumda cozum diye eklenen `cookiesfrombrowser` (Chrome/Firefox) fallback zinciri hem gurultu cikardi hem sorunu cozmedi. Kanitlanmis gercek kok neden: **Instagram 2-3 Temmuz 2026 civari API'sini degistirip reels/gonderiler icin login zorunlu hale getirdi** - kod/uygulama sorunu degil. Kanit: (1) ayni reel hic cookie olmadan da "empty media response" veriyor, (2) sahte/var olmayan reel ID'si bile ayni hatayi veriyor (genel login duvari, post bazli degil), (3) YouTube cookie'siz sorunsuz iniyor, (4) yt-dlp bug tracker #17074/#17124 (2-3 Temmuz) dunya capinda ayni sikayetle dolu, bakimci extractor'da degisiklik olmadigini dogruluyor, (5) Chrome cookie'si zaten okunamiyor (#10927 ABE), Firefox kurulu degil. Kullanici karari: cookie karmasasi tamamen geri alindi (temiz no-cookie orijinal hal), `_friendly_error()` ile login-duvari hatasi net Turkce mesaja cevrildi. Gercek cozum (uygulama-ici QtWebEngine login) ayri/sonraki gorev olarak ertelendi. Detay: [[hata_yonetimi_ve_loglama]].

## [2026-07-04] FIX | UI ceviri hatasi, gizli ModuleNotFoundError riski, native crash yakalama

Devam eden "Instagram reels cokuyor" raporu incelenirken uc ayri sorun bulundu: (1) `_queue_row`/`_history_row` birbirine ters `_job_summary`/`_history_summary` cagiriyordu, aktif kuyrukta ham Ingilizce "queued"/"running" gorunuyordu - fonksiyonlar dogru yerlere baglandi, fallback "Bilinmiyor" yapildi. (2) yt_dlp `--exclude-module` ile build'den harici tutuldugu icin PyInstaller onun stdlib bagimliliklarini (`optparse`, `http.cookies`) algilayamiyordu - HER indirmeyi etkileyebilecek gizli bir hata; yt_dlp artik exclude edilmiyor, normal analiz edilip yedek olarak gomuluyor (harici, guncellenebilir kopya yine de sys.path onceligiyle her zaman kazaniyor - canli test ile kanitlandi). (3) `faulthandler` eklendi (`logs/native_crash.log`) - Python exception olarak yakalanamayan native cokmeler icin. Log konumu da `~/.baglanti_indirici/` yerine uygulama dizinine (`logs/`) tasindi, kolay bulunsun diye. Detay: [[hata_yonetimi_ve_loglama]], [[yt_dlp_oto_guncelleme]].

## [2026-07-04] FIX | Exe çökmesi giderildi, loglama sistemi eklendi

Kullanıcı Instagram/YouTube URL'lerinden indirirken exe'nin sessizce çöktüğünü bildirdi. Kök neden: `enqueue_download` zincirinde (`controller.py` → `queue/service.py` → `platform/registry.py::normalize_url`) try/except yoktu; bozuk URL'lerde `urllib.parse.urlparse` fırlattığı `ValueError` bir Qt slot'unda yakalanmadan PyQt5'i sonlandırıyordu (doğrulandı: `http://[bozuk` ile canlı reprodüksiyon). `core/logger.py` eklendi (dosya tabanlı loglama + global `sys.excepthook` güvenlik ağı), somut boşluk try/except ile kapatıldı, worker'lardaki sessiz hata kayıpları loglamaya bağlandı. Detay: [[hata_yonetimi_ve_loglama]].

## [2026-07-04] LINT | Wiki tutarlılık kontrolü ve düzeltme

`docs/wiki/` tarandı: bağlantı bütünlüğü sorunsuz (kırık link/öksüz sayfa yok). İki bulgu düzeltildi: [[rules]] içindeki commit tipi listesi gerçek git geçmişiyle uyumlu hale getirildi (`build` kaldırıldı — hiç kullanılmamış; `core` eklendi — en çok kullanılan tip, 8 commit). `log.md`'deki kendine referans (`[[log]]` self-link) düz metne çevrildi.

## [2026-07-04] INGEST | LLM Wiki sistemi kuruldu

`docs/wiki/` bilgi tabanı oluşturuldu: [[index]], [[rules]], log.md (bu dosya), [[mimari]], [[yt_dlp_oto_guncelleme]], [[tema_sistemi]], [[paketleme]]. Proje köküne `CLAUDE.md` eklendi (wiki'yi her oturumda önce okuma kuralı).

## [2026-07-04] MAINT | Commit geçmişinden AI referansı temizlendi

Son 3 commit'in mesajlarındaki `Co-Authored-By: Claude Sonnet 5` satırı `git filter-branch --msg-filter` ile kaldırıldı (ağaç/içerik değişmedi, sadece mesaj). Kullanıcı onayıyla `git push --force-with-lease origin main` yapıldı. Kural [[rules]]'a eklendi: bundan sonra commit mesajlarına AI referansı yazılmaz.

## [2026-07-04] FEATURE | Tema toggle ikon kırpma düzeltmesi + Inno Setup installer

`#themeToggleButton` için ayrı, `padding: 0` stil eklendi (bkz. [[tema_sistemi]] bilinen tuzaklar). `installer.iss` ile Türkçe Inno Setup kurulum sihirbazı eklendi (bkz. [[paketleme]]). Temiz `.venv` ile yeni exe derlendi, `dist/lib/yt_dlp/` yenilendi.

## [2026-07-04] FIX | Durum çubuğu kutu görünümü ve güncelleme bildirimi

`#statusBarText`/`#footerText` etiketleri genel `QWidget` arka plan kuralından "kutu" gibi görünüyordu; `background: transparent` eklendi. yt-dlp güncellemesi bulunduğunda artık durum çubuğu metni de bilgilendiriyor (bkz. [[tema_sistemi]]).

## [2026-07-04] FEATURE | yt-dlp oto-güncelleme + koyu/açık tema sistemi

yt-dlp exe içine gömülmekten çıkarılıp harici, güncellenebilir `lib/yt_dlp/` klasörüne taşındı; PyPI tabanlı oto-güncelleme eklendi (bkz. [[yt_dlp_oto_guncelleme]]). Arayüze koyu/açık tema toggle'ı ve daha koyu varsayılan palet eklendi (bkz. [[tema_sistemi]]).

## [2026-07-04] MAINT | Build ortamı temizlendi, Nuitka kaldırıldı

Conda ortamındaki DLL ayrışması sorunu (`sqlite3.dll` vb. bulunamıyor) nedeniyle build için temiz `.venv` (python.org Python) standart alındı. Nuitka desteği (`build_nuitka.bat`, paket, README referansları) tamamen kaldırıldı — tek build yolu PyInstaller (bkz. [[paketleme]]).
