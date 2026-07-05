# Baglanti Indirici

Baglanti Indirici, PySide6 (Qt6) ve yt-dlp uzerine kurulu modern bir video/ses indirme uygulamasidir. Uygulama tek link indirme akisini, kuyruk sistemi, kalici gecmis, platform profilleri, Instagram girisi, kompakt mod ve web fallback mekanizmasi ile genisletilebilir bir mimariye tasir.

Proje Windows odakli gelistirilmis olsa da Python, PySide6, yt-dlp ve FFmpeg bulunan macOS/Linux sistemlerinde de calisabilecek sekilde tasarlanmistir (Instagram girisi ve derlenmis exe/installer akisi Windows'a ozeldir).

## Icerik

- [Temel Ozellikler](#temel-ozellikler)
- [Desteklenen Platformlar](#desteklenen-platformlar)
- [Kurulum](#kurulum)
- [Kullanim](#kullanim)
- [Instagram Girisi](#instagram-girisi)
- [Kompakt Mod](#kompakt-mod)
- [yt-dlp Oto-Guncelleme](#yt-dlp-oto-guncelleme)
- [Proje Mimarisi](#proje-mimarisi)
- [Veri Saklama](#veri-saklama)
- [Gelistirme](#gelistirme)
- [Test](#test)
- [Paketleme](#paketleme)
- [Sorun Giderme](#sorun-giderme)
- [Guvenlik ve Gizlilik](#guvenlik-ve-gizlilik)
- [Yasal Not](#yasal-not)

## Temel Ozellikler

- Video indirme: Desteklenen platformlardan video icerigi indirir.
- Ses indirme: Ses modunda MP3 cikti uretir.
- Playlist destegi: Playlist modunda birden fazla icerigi sirali olarak indirir.
- Kuyruk sistemi: Birden fazla baglanti kuyruga eklenebilir ve varsayilan olarak sirayla calisir.
- Kalici gecmis: Tamamlanan, iptal edilen ve basarisiz indirmeler SQLite veritabaninda saklanir.
- Tekrar deneme: Gecmis sayfasindaki isler yeniden kuyruga alinabilir.
- Klasorde gosterme: Tamamlanan islerin hedef klasoru uygulamadan acilabilir.
- Platform profilleri: Platform algilama, vurgu rengi ve format politikasi kayit tabanli tanimlanir.
- Web fallback: yt-dlp bir web URL'sini dogrudan desteklemezse sayfa icindeki medya kaynaklari aranir.
- Iptal destegi: Kuyrukta bekleyen veya calisan is iptal edilebilir.
- Koyu/acik tema: PySide6 uzerinde ozel kartlar, butonlar, segment kontrolu ve scrollbar stilleri kullanilir; tema tercihi kalicidir.
- Instagram girisi: Kullanicinin kendi Chrome/Edge'ini Chrome DevTools Protocol (CDP) ile surerek login-gerekli icerikleri (reels vb.) indirebilir; sifre uygulamada saklanmaz.
- Kompakt mod: Uygulama kucuk, her zaman ustte, surunebilir yuvarlak bir bubble'a kucultulebilir; fare uzerine gelince URL girisi acilir, indirme otomatik baslar, tamamlaninca cember yesil/kirmizi yanip soner.
- yt-dlp oto-guncelleme: Uygulama acilista PyPI'daki en yeni yt-dlp surumunu kontrol eder, kullanici onayiyla harici, guncellenebilir bir kopyayi indirip kurar.
- Cokme guvenligi: Global `sys.excepthook` ve dosya tabanli loglama (`~/.baglanti_indirici/logs/app.log`) ile yakalanmamis hatalar kaydedilir.
- Kullanici gizliligi: Varsayilan kayit konumu arayuzde `C:\Users\<user>\Downloads` gibi maskelenir.

## Desteklenen Platformlar

Platform algilama `core/platform/registry.py` icindeki `PlatformRegistry` ve `PlatformProfile` yapilari ile yonetilir.

Varsayilan profiller:

- YouTube / youtu.be
- TikTok
- Instagram
- Facebook / fb.watch
- X (Twitter)
- Pinterest / pin.it
- Twitch
- SoundCloud
- Genel Web URL'leri

yt-dlp cok daha fazla siteyi destekledigi icin, listede olmayan fakat yt-dlp tarafindan desteklenen HTTP/HTTPS sayfalari `Web` profili ile denenir.

## Sistem Gereksinimleri

- Python 3.10 veya uzeri
- PySide6 6.8.x (Qt6; `>=6.8,<6.9` ile sabitlenmistir — bkz. [Sorun Giderme](#sorun-giderme))
- yt-dlp 2025.1.1+ (uygulama acilista PyPI uzerinden oto-guncelleme sunar)
- FFmpeg
- Windows 10/11, macOS veya Linux
- Instagram girisi icin: kurulu Chrome veya Edge (Windows'a ozel ozellik)

FFmpeg video/ses birlestirme ve MP3 donusturme islemleri icin gereklidir.

## Kurulum

### 1. Depoyu alin

```bash
git clone https://github.com/Yusufygc/Baglanti_Indirici.git
cd Baglanti_Indirici
```

Yerel calisma klasorunuz farkliysa komutlari proje kok dizininde calistirin.

### 2. Sanal ortam olusturun

Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Bagimliliklari yukleyin

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Gelistirme modunda test bagimliliklariyla kurmak icin:

```bash
python -m pip install -e ".[dev]"
```

### 4. FFmpeg kurun

Windows icin secenekler:

- FFmpeg resmi indirme sayfasini acin: https://ffmpeg.org/download.html
- `Windows EXE Files` bolumunden hazir Windows build sayfalarindan birini secin:
  - gyan.dev builds: https://www.gyan.dev/ffmpeg/builds/
  - BtbN builds: https://github.com/BtbN/FFmpeg-Builds/releases
- Kolay kurulum icin gyan.dev sayfasindan `release essentials` zip paketini indirin.
- Zip dosyasini acin ve icindeki `bin\ffmpeg.exe` dosyasini bulun.
- En basit yontem: `ffmpeg.exe` dosyasini proje kok dizinine kopyalayin.
- Alternatif yontem: zip icindeki klasoru `C:\ffmpeg` olarak yerlestirin. Bu durumda beklenen yol `C:\ffmpeg\bin\ffmpeg.exe` olur.
- Daha genel yontem: `C:\ffmpeg\bin` klasorunu Windows `PATH` degiskenine ekleyin.

Windows PATH ekleme ozeti:

1. Baslat menusunde `Ortam degiskenleri` aratin.
2. `Sistem ortam degiskenlerini duzenle` ekranini acin.
3. `Ortam Degiskenleri` butonuna basin.
4. Kullanici veya sistem `Path` degiskenini secip `Duzenle` deyin.
5. `Yeni` ile `C:\ffmpeg\bin` yolunu ekleyin.
6. Terminali kapatip yeniden acin.
7. Kurulumu dogrulayin:

```powershell
ffmpeg -version
```

Uygulama icin en pratik secenek proje kokune `ffmpeg.exe` kopyalamaktir. Bu durumda PATH ayari gerekmez.

macOS:

```bash
brew install ffmpeg
```

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install ffmpeg
```

Uygulama FFmpeg'i su sirayla arar:

1. PyInstaller bundle icindeki `ffmpeg.exe`
2. Uygulama kok dizinindeki `ffmpeg.exe`
3. Gelistirme ortamindaki proje kok dizini
4. `C:\ffmpeg\bin\ffmpeg.exe`
5. Sistem `PATH` icindeki `ffmpeg`

## Uygulamayi Calistirma

```bash
python main.py
```

Conda ortami kullaniyorsaniz:

```bash
conda run -n BaglantiIndir python main.py
```

## Kullanim

### Ana Sayfa

1. `Baglanti` alanina indirmek istediginiz URL'yi yapistirin.
2. Uygulama platformu otomatik algilar ve uygun rozeti gosterir.
3. `Kayit Konumu` alanindan hedef klasoru secin. Gosterilen kullanici yolu maskelenir, gercek yol uygulama icinde kullanilir.
4. Istege bagli dosya adi girin. Bos birakilirsa yt-dlp basligi kullanilir.
5. Format secin:
   - `Video`: Video olarak indirir.
   - `Ses (MP3)`: Ses olarak indirir ve MP3'e donusturur.
   - `Playlist`: Playlist iceriklerini sirali indirir.
6. `Kuyruga Ekle` butonuna basin.
7. Aktif kuyruk kartindan bekleyen/calisan isleri takip edin.
8. Gerekirse isleri iptal edin.

### Gecmis Sayfasi

Sag ustteki `Gecmis` butonu ile gecmis sayfasina gecilir.

Gecmis sayfasinda:

- Tamamlanan, iptal edilen ve basarisiz indirmeler listelenir.
- Kayitlar URL yerine video basligi veya dosya adiyla gosterilir.
- `Tekrar Dene` ile is yeniden kuyruga eklenir.
- `Klasorde Goster` ile hedef klasor acilir.
- `Gecmisi Temizle` ile tum gecmis silinir.
- `Ana Sayfa` butonu ile indirme ekranina donulur.

## Instagram Girisi

Instagram 2026 Temmuz'unda API'sini degistirip reels/gonderiler icin giris (login) zorunlu hale getirdi. Uygulama bunu su sekilde cozer:

1. Header'daki `Instagram Giris` butonuna tiklayin.
2. Uygulama, kurulu Chrome'unuzu (yoksa Edge) **ayri bir profille** acar.
3. Acilan gercek tarayicida hesabiniza normal sekilde giris yapin (passkey/2FA/reCAPTCHA sorunsuz calisir — gercek tarayici oldugu icin Instagram bunu bot saymaz).
4. Giris algilanir algilanmaz pencere otomatik kapanir; oturum cerezleri (HttpOnly `sessionid` dahil) Chrome DevTools Protocol (CDP) ile hafizadan okunup kaydedilir.

Sifreniz **uygulamada hicbir zaman saklanmaz** — yalnizca oturum cerezleri (`~/.baglanti_indirici/instagram_cookies.txt`) tutulur. Oturum bir kez alindiktan sonra tekrar giris istenmez (dogal olarak sonlanana kadar). Detay: `docs/wiki/instagram_login.md`.

## Kompakt Mod

Header'daki "◎" butonuna tiklayarak uygulama kucuk, yuvarlak, her zaman ekranin en ustunde duran bir bubble'a kucultulebilir:

- Bubble ekranin herhangi bir yerine surunebilir; birakildigi yerde kalir.
- Fare uzerine geldiginde yanindan bir URL girisi acilir.
- Bir link yapistirip Enter'a basinca, o an ayarli format/klasor/dosya adiyla indirme otomatik baslar (tam pencereyi acmaya gerek yok).
- Indirme tamamlaninca cember gecici olarak yesile, basarisiz olursa kirmiziya doner, sonra normal rengine geri gelir.
- Cift tiklama ile tam pencereye donulur.

Detay: `docs/wiki/kompakt_mod.md`.

## yt-dlp Oto-Guncelleme

yt-dlp siklikla guncellenen bir kutuphanedir (platformlarin API degisikliklerine karsi). Uygulama acilista PyPI'daki en yeni surumu kontrol eder; yeni bir surum varsa durum cubugunda bildirim gosterilir, kullanici onayiyla indirilip `~/.baglanti_indirici/lib/yt_dlp/` icine kurulur — uygulamanin kendisini yeniden derlemeye gerek kalmadan. Detay: `docs/wiki/yt_dlp_oto_guncelleme.md`.

## Proje Mimarisi

Proje, UI ve is mantigini ayri tutacak sekilde katmanlara ayrilmistir.

```text
Baglanti_Indir/
├── main.py
├── pyproject.toml
├── requirements.txt
├── installer.iss
├── build_pyinstaller.bat
├── core/
│   ├── config.py
│   ├── logger.py
│   ├── settings.py
│   ├── domain/
│   ├── download/
│   ├── history/
│   ├── instagram/
│   ├── platform/
│   ├── queue/
│   ├── update/
│   ├── web/
│   └── utils.py
├── ui/
│   ├── assets/
│   ├── themeing/
│   ├── widgets/
│   └── window/
│       ├── main_window.py
│       ├── controller.py
│       ├── compact_bubble.py
│       └── instagram_login_dialog.py
├── icons/
├── docs/wiki/
└── tests/
```

### `main.py`

Uygulama giris noktasi. `QApplication` olusturur, fontlari yukler, `MainWindow` nesnesini baslatir.

### `core/domain`

Saf veri modellerini icerir.

Onemli tipler:

- `DownloadOptions`: Indirme klasoru, mod, dosya adi, playlist durumu ve gelecekteki kalite ayarlari.
- `DownloadJob`: Kuyruktaki veya gecmisteki tek indirme isi.
- `DownloadMode`: `video` ve `ses` modlari.
- `JobStatus`: `queued`, `running`, `completed`, `failed`, `cancelled`.
- `PlatformProfile`: Platform adi, domain eslesmeleri, renk ve format politikasi.

### `core/platform`

Platform algilama ve format politikalarini yonetir.

- `registry.py`: Yeni mimari. `PlatformRegistry` ve varsayilan `PlatformProfile` kayitlari burada.
- `service.py`: Geriye uyumlu facade. Eski `PlatformService.detect(...)` ve `format_options(...)` API'lerini korur.

Yeni platform eklemek icin `default_profiles()` listesine yeni `PlatformProfile` eklemek yeterlidir.

Ornek:

```python
PlatformProfile("Example", ("example.com",), "#12C8E8")
```

### `core/download`

Tek bir indirme isinin calisma mantigini icerir.

- `engine.py`: Tek isi calistiran asil indirme motoru. yt-dlp ve web fallback akisini yonetir.
- `service.py`: Eski testleri ve kodlari bozmamak icin `DownloadEngine` uzerinde compatibility facade.
- `yt_dlp_client.py`: yt-dlp ayarlarini uretir ve indirme komutunu calistirir.
- `worker.py`: PySide6 `QThread` tabanli worker siniflari. Kuyruk islerini arka planda calistirir.
- `progress.py`: yt-dlp progress verisini UI icin okunabilir yuzde/metin formatina cevirir.
- `errors.py`: Indirme hata tipi.

### `core/queue`

Kuyruk yonetimini yapar.

`DownloadQueueService`:

- `enqueue(...)`: Yeni isi kuyruga ekler.
- `next_job()`: Siradaki isi calismaya alir.
- `mark_progress(...)`: Ilerleme bilgisini gunceller.
- `mark_completed(...)`: Isi tamamlandi olarak isaretler.
- `mark_failed(...)`: Isi basarisiz olarak isaretler.
- `mark_cancelled(...)`: Isi iptal edildi olarak isaretler.
- `retry(...)`: Gecmisteki isi yeniden kuyruga alir.
- `pause_queue()` / `resume_queue()`: Kuyruk calismasini duraklatir veya surdurur.

Varsayilan eszamanli indirme sayisi `max_concurrent=1` olarak ayarlanmistir. Mimari ileride paralel indirme icin hazirdir.

### `core/history`

Kalici indirme gecmisini saklar.

`HistoryRepository` standart Python `sqlite3` kullanir. Ek veritabani bagimliligi yoktur.

Gecmis verisi varsayilan olarak kullanici profilinde saklanir:

```text
~/.baglanti_indirici/history.sqlite3
```

### `core/instagram`

Instagram oturum (cerez) saklama — saf, GUI'siz mantik (Qt import etmez, testler GUI'siz calisir).

- `session.py`: `cookies_path()`, `has_session()`, `clear_session()`, `write_netscape_cookies()`, `find_browser_executable()`, `cdp_cookies_to_netscape()`. Gercek CDP-Chrome surme akisi `ui/window/instagram_login_dialog.py` icindedir.

### `core/update`

yt-dlp'nin PyPI uzerinden oto-guncellenmesini yonetir.

- `yt_dlp_updater.py`: `YtDlpUpdater` — surum kontrolu, wheel indirme, guvenli (staging + rename) kurulum.
- `pypi_client.py`: PyPI JSON API'sinden en son surum bilgisini ceker.
- `worker.py`: `UpdateCheckWorker` / `UpdateInstallWorker` — `QThread` tabanli, arka planda calisir.

### `core/web`

yt-dlp'nin desteklemedigi genel web sayfalari icin medya kaynagi arar.

`WebMediaExtractor`:

- Dogrudan `.mp4`, `.webm`, `.m3u8` gibi medya URL'lerini tanir.
- HTML icindeki `video`, `source`, `a` ve `iframe` kaynaklarini tarar.
- Script icindeki medya URL'lerini regex ile yakalar.
- Iframe icinde sinirli derinlikte arama yapar.

### `ui/window`

Ana pencere ve UI kontrol akisini icerir.

- `main_window.py`: PySide6 widget agaci, ana sayfa, gecmis sayfasi, aktif kuyruk, kompakt mod toggle ve UI event handler'lari.
- `controller.py`: UI ile kuyruk/gecmis/worker katmani arasindaki koordinasyon. Is durumu (`JobStatus`) degisince (`_on_job_updated`) view'i gunceller — indirme tamamlanma/hata bildirimlerinin **gercek** tetikleme noktasi burasidir.
- `compact_bubble.py`: `CompactBubble` — yuvarlak, her zaman ustte, surunebilir mini pencere (bkz. [Kompakt Mod](#kompakt-mod)).
- `instagram_login_dialog.py`: `InstagramLoginDialog` — kullanicinin Chrome'unu CDP ile surerek Instagram girisi (bkz. [Instagram Girisi](#instagram-girisi)).
- `view_state.py`: UI durum enum'u.

Ana pencere `QStackedWidget` kullanir:

- Sayfa 1: Indirme formu ve aktif kuyruk.
- Sayfa 2: Gecmis listesi.

### `ui/themeing`

Tema token'lari ve stylesheet parcalari.

- `theme.py`: Renk ve font boyutu token'lari.
- `style_sections.py`: Global, metin, kart, input, buton, kontrol ve scrollbar stilleri.
- `styles.py`: Tum stil parcalarini birlestiren `StyleManager`.
- `font_profiles.py`: Aktif font profilini belirler.

### `ui/widgets`

Tekrar kullanilabilir PySide6 bilesenleri.

- `ModernCard`
- `HeaderLabel`
- `ModernButton`
- `ModernInput`
- `SegmentControl`

### `ui/assets`

Font ve ikon yukleme yardimcilari.

- `font_manager.py`: Uygulama fontlarini yukler ve font stack uretir.
- `icons.py`: SVG/ICO ikonlarini PySide6 icin hazirlar.

## Veri Saklama

Uygulama, exe Program Files gibi salt-okunur bir dizine kurulsa bile calisir cunku TUM kullanici verisi kullanici profilindeki `~/.baglanti_indirici/` altinda tutulur:

- Indirilen dosyalar: Kullanici tarafindan secilen hedef klasore yazilir (varsayilan `~/Downloads`).
- Gecmis veritabani: `~/.baglanti_indirici/history.sqlite3`.
- Ayarlar (tema tercihi vb.): `~/.baglanti_indirici/settings.json`.
- Uygulama loglari: `~/.baglanti_indirici/logs/app.log` (+ `native_crash.log`).
- Instagram oturum cerezleri: `~/.baglanti_indirici/instagram_cookies.txt`, CDP tarayici profili `~/.baglanti_indirici/webprofile/`.
- yt-dlp oto-guncelleme kopyasi: `~/.baglanti_indirici/lib/yt_dlp/` (exe yanindaki gomulu kopyaya gore oncelikli okunur).

Gecmis tablosu su bilgileri saklar:

- Is kimligi
- Orijinal URL
- Normalize URL
- Platform
- Indirme ayarlari
- Durum
- Olusturma/baslama/bitis zamanlari
- Hedef klasor
- Hata mesaji
- Video basligi
- Ilerleme yuzdesi
- Son durum mesaji

Not: Arayuzde kullanici profil yolu maskelenir. Ornegin Windows'ta gercek yol yerine `C:\Users\<user>\Downloads` gorunur.

## Gelistirme

### Kod stili

Proje Python 3.10 hedefler. `pyproject.toml` icinde Ruff icin temel ayarlar bulunur:

```toml
[tool.ruff]
line-length = 100
target-version = "py310"
```

### Yeni platform ekleme

1. `core/platform/registry.py` dosyasini acin.
2. `default_profiles()` listesine yeni `PlatformProfile` ekleyin.
3. Gerekirse platforma ozel format politikasi yazin.
4. `tests/test_platform_registry.py` veya `tests/test_platforms.py` icine test ekleyin.

### Yeni indirme secenegi ekleme

1. `core/domain/models.py` icindeki `DownloadOptions` modeline alan ekleyin.
2. `core/download/yt_dlp_client.py` icindeki yt-dlp option uretimini guncelleyin.
3. UI kontrolunu `ui/window/main_window.py` veya uygun yeni widget icinde ekleyin.
4. Kuyruk ve gecmis testlerini guncelleyin.

### UI tema degistirme

Renk ve font boyutlari icin `ui/themeing/theme.py` dosyasini kullanin. Stil detaylari `ui/themeing/style_sections.py` icindedir.

Font profili icin:

```python
# ui/themeing/font_profiles.py
ACTIVE_FONT_PROFILE = "modern"
```

Mevcut profiller:

- `playful`
- `modern`
- `elegant`
- `classic`
- `italic_classic`

## Test

Tum testleri calistirmak icin:

```bash
python -m pytest
```

Beklenen kapsam:

- Platform algilama ve format politikasi
- Platform registry davranisi
- Download engine web fallback davranisi
- Eski `DownloadService` facade uyumlulugu
- Kuyruk siralama, iptal ve retry davranisi
- SQLite gecmis repository davranisi
- Progress formatter
- Web media extractor
- Font profilleri
- Instagram oturum (cerez) saklama ve CDP cerez donusumu
- Controller hata yonetimi (gecersiz URL, kuyruga ekleme basarisizligi)

Son dogrulama sirasinda test paketi:

```text
62 passed
```

## Paketleme

### PyInstaller (onedir)

```powershell
.\build_pyinstaller.bat
```

Cikti `dist\BaglantiIndirici\` klasorune yazilir (**onedir**, onefile degil). Script ayrica pip kurulu `yt_dlp`'yi `dist\BaglantiIndirici\lib\yt_dlp\` icine harici, guncellenebilir bir kopya olarak ekler.

Paketlemeden once:

- Sanal ortam aktif olmali (conda degil — bkz. `docs/wiki/paketleme.md`).
- `PySide6` (6.8.x, `requirements.txt`'te sabit) ve `yt-dlp` kurulu olmali.
- FFmpeg (`ffmpeg.exe`) proje kokunde bulunmali (build'e `--add-binary` ile gomulur).

### Inno Setup ile Kurulum Sihirbazi

`dist\BaglantiIndirici\` olustuktan sonra, Inno Setup Compiler (ISCC) ile:

```powershell
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

Cikti `installer_output\BaglantiIndirici_Setup.exe` — Turkce kurulum sihirbazi, masaustu kisayolu secenegi, `dist\BaglantiIndirici\` klasorunun tamamini paketler.

**Not:** Exe/installer yalnizca acikca istendiginde derlenir; her kod degisikliginde otomatik derleme yapilmaz.

## Sorun Giderme

### `ModuleNotFoundError: No module named 'PySide6'`

Bagimliliklar kurulu degildir.

```bash
python -m pip install -r requirements.txt
```

### Derlenmis exe acilista `DLL load failed while importing QtWidgets` ile cokuyor

PySide6 6.9+ ile derlenen exe'ler PyInstaller 6.21 ile bilinen bir uyumsuzluk yasar (shiboken/Qt6 baglamasi frozen ortamda initialize olamiyor). `requirements.txt` bu yuzden `PySide6>=6.8,<6.9` (6.8 LTS) ile sabitlenmistir — surumu yukseltmeyin.

### Derlenmis exe kurulunca (Program Files) acilista `PermissionError [WinError 5]` veya guncelleme hatasi veriyor

Program Files salt-okunur oldugu icin exe-yani klasorlere yazma denemesi basarisiz olur. Uygulama artik TUM kullanici verisini (loglar, ayarlar, yt-dlp guncellemesi) `~/.baglanti_indirici/` altina yazar (bkz. [Veri Saklama](#veri-saklama)); bu hata guncel bir surumde gorulmemelidir.

### FFmpeg bulunamiyor

`ffmpeg.exe` dosyasini proje kok dizinine koyun veya sistem `PATH` degiskenine ekleyin.

Kontrol:

```bash
ffmpeg -version
```

### Indirme basarisiz

Olasiliklar:

- URL platform tarafindan desteklenmiyor olabilir.
- yt-dlp surumu eski olabilir.
- Platform giris/cerez/bolge kisiti uyguluyor olabilir.
- FFmpeg eksik olabilir.

yt-dlp guncelleme:

```bash
python -m pip install --upgrade yt-dlp
```

### Web fallback kaynak bulamiyor

Bazi siteler medya URL'lerini JavaScript, token, DRM veya oturum kontrolleri arkasinda saklar. Bu durumda `WebMediaExtractor` sayfada indirilebilir kaynak bulamayabilir.

### Uygulama acilirken QSS uyarilari

PySide6/Qt6 her CSS ozelligini desteklemez. Stil eklerken sadece Qt stylesheet tarafindan desteklenen ozellikleri kullanin. Placeholder rengi gibi ozellikler widget/palette uzerinden verilmelidir.

### Instagram girisi "Chrome veya Edge bulunamadi" diyor

Instagram girisi kurulu Chrome (tercih edilir) veya Edge gerektirir. Bulunan yollar: `Program Files`, `Program Files (x86)`, `LOCALAPPDATA` altindaki standart kurulum konumlaridir; farkli bir konuma kuruluysa algilanamaz.

### Instagram girisi normal tarayicida da login'e geri donuyor

Bu, uygulamanin degil **Instagram hesabinin** sorunu olabilir (risk-tabanli giris kilidi / yanlis sifre / cok deneme). Once hesaba normal Chrome'unuzda giris yapabildiginizi dogrulayin; oradan basarili olursa uygulamadaki giris de calisir.

### Gecmis temizlenmiyor gibi gorunuyor

Gecmis sayfasinda `Gecmisi Temizle` butonunu kullanin. Veritabani dosyasi manuel silinecekse uygulama kapaliyken silin:

```text
~/.baglanti_indirici/history.sqlite3
```

## Guvenlik ve Gizlilik

- Uygulama indirme URL'lerini gecmis veritabaninda saklar.
- Arayuz, kullanici profil yolunu maskeler; gercek indirme yolu sadece islem icin kullanilir.
- Indirilen iceriklerin yasal kullanimi kullanicinin sorumlulugundadir.
- Uygulama platform giris bilgisi veya parola yonetmez/saklamaz. Instagram girisinde sifre uygulamaya hic ulasmaz (kullanici kendi tarayicisina yazar); yalnizca oturum cerezleri (`sessionid` dahil) diskte tutulur — bu, hesaba erisim sagladigi icin hassastir, `Instagram Giris` akisindan cikis/temizleme ile silinebilir.

## Yol Haritasi

Planlanan veya kolay eklenebilir gelistirmeler:

- Paralel indirme sayisi ayari
- Kalite secenekleri: 1080p, 720p, en iyi, dusuk boyut (secilebilir; su an her zaman en yuksek kalite denenir)
- Ses bitrate secimi
- Altyazi indirme
- Kapak gorseli indirme
- Ayarlar sayfasi
- Gecmis arama ve filtreleme
- Otomatik retry politikasi
- Daha ayrintili hata siniflandirmasi
- Platform profili editoru
- Kompakt bubble konumunun yeniden baslatmalar arasi hatirlanmasi (su an yalnizca ayni oturum icinde korunur)

## Yasal Not

Bu proje egitim ve kisisel kullanim amaciyla gelistirilmistir. Indirdiginiz iceriklerde ilgili platformlarin kullanim sartlarina, telif hakki kurallarina ve yerel mevzuata uymak tamamen kullanicinin sorumlulugundadir.
