# Paketleme ve Dağıtım

Bkz. [[index]] · İlgili: [[yt_dlp_oto_guncelleme]], [[mimari]]

## Build Ortamı

**Conda değil, temiz venv kullan.** Conda Python DLL'leri `Library\bin` altına ayırır; PyInstaller bunları bulamaz ve `sqlite3.dll`, `ffi.dll`, `liblzma.dll` gibi bağımlılıklar için elle `--add-binary` yaması gerektirir (native crash: `ImportError: DLL load failed while importing _sqlite3`). Standart python.org Python ile kurulan `.venv` bu sorunu hiç yaşamaz ve daha küçük/temiz bir exe üretir.

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt pyinstaller
```

**PySide6 6.8 LTS'e sabit (`requirements.txt`: `>=6.8,<6.9`).** 6.11.x ile derlenen exe acilista `ImportError: DLL load failed while importing QtWidgets: procedure not found` veriyor (venv'de import sorunsuz, bundle dosyalari birebir ayni, ama frozen'da shiboken/Qt6 baglamasi initialize olamiyor — PySide6 6.11 + PyInstaller 6.21 uyumsuzlugu). 6.8 LTS kararli. Ayrica venv'de PyQt5 kalintisi (eski migration'dan) birakma; bozuk `~yqt5` dist-info PyInstaller'i bozabilir.

## PyInstaller (`build_pyinstaller.bat`)

- **`--onedir --windowed`** (onefile DEĞİL), ikon `icons/icon.ico`, veri: `icons/`, `ui/assets/fonts/`.
- **Neden onedir:** Dağıtım Inno Setup installer ile yapılır (bkz. `installer.iss`) ve tüm `BaglantiIndirici/` klasörünü paketler; onedir bu akışa uyar ve harici güncellenebilir `lib/yt_dlp/` kopyasını exe'nin yanında tutmayı kolaylaştırır. (Not: Instagram girişi artık gömülü `QtWebEngine` değil, kullanıcının kendi Chrome'unu CDP ile sürüyor — bkz. [[instagram_login]] — yani QtWebEngine bağımlılığı yok; teknik olarak onefile de mümkün, ancak mevcut installer akışı için onedir korunuyor. CDP için gereken `QtWebSockets`/`QtNetwork` PySide6-Essentials'ta, PyInstaller PySide6 hook'larıyla otomatik toplanır.)
- **Taşınabilirlik:** onedir'de çıplak exe tek başına taşınamaz (klasörüne bağımlı). "Her yerden çalıştırma" installer'ın kurduğu kısayolla veya TÜM `BaglantiIndirici/` klasörünü kopyalayarak olur.
- `--add-binary "ffmpeg.exe;."` — ffmpeg pakete dahil (onedir klasör kökünde, `_MEIPASS`'ten çözülür).
- `yt_dlp` **exclude edilmiyor** — normal analiz edilip gömülü yedek olarak dahil edilir (bkz. [[yt_dlp_oto_guncelleme]]).
- Build sonrası script, pip kurulu `yt_dlp`'yi **`dist/BaglantiIndirici/lib/yt_dlp/`** içine kopyalar (onedir'de `get_base_path()` = exe klasörü; harici güncellenebilir kopya orada aranır).
- Çıktı: `dist/BaglantiIndirici/` klasörü (exe + QtWebEngine runtime + `lib/yt_dlp/`). QtWebEngine nedeniyle boyut önemli ölçüde büyür (~300MB+).

**Not:** Nuitka desteği kaldırıldı (tek build yolu PyInstaller). `build_nuitka.bat` artık yok.

## Inno Setup (`installer.iss`)

Proje kökündeki `installer.iss`, **tüm `dist/BaglantiIndirici/` klasörünü** (exe + QtWebEngine runtime + `lib/yt_dlp`) `{app}`'e paketleyip Windows kurulum sihirbazı üretir:

```powershell
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

- `[Files]`: `Source: "dist\BaglantiIndirici\*"; ... recursesubdirs createallsubdirs` (tek exe değil, onedir klasörünün tamamı).
- Çıktı: `installer_output/BaglantiIndirici_Setup.exe` (gitignore'da, `*.exe` kuralına takılır).
- Türkçe dil dosyası (`compiler:Languages\Turkish.isl`), masaüstü kısayolu seçeneği (task), Start Menu grubu, kurulum sonrası "çalıştır" seçeneği içerir.
- `AppId` GUID sabit tutulmalı — değişirse Windows aynı uygulamanın güncellemesi yerine ayrı bir kurulum olarak görür.

## Gitignore Notları

`*.exe`, `*.bat`, `*.spec`, `build/`, `dist/` gitignore'dadır (bazı `.bat`/`.spec` dosyaları yine de repo'da force-add edilmiş olabilir — `git status --ignored` ile kontrol et). `installer_output/` de `*.exe` kuralına takılıp otomatik yok sayılır.
