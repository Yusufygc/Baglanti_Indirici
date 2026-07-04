# Paketleme ve Dağıtım

Bkz. [[index]] · İlgili: [[yt_dlp_oto_guncelleme]], [[mimari]]

## Build Ortamı

**Conda değil, temiz venv kullan.** Conda Python DLL'leri `Library\bin` altına ayırır; PyInstaller bunları bulamaz ve `sqlite3.dll`, `ffi.dll`, `liblzma.dll` gibi bağımlılıklar için elle `--add-binary` yaması gerektirir (native crash: `ImportError: DLL load failed while importing _sqlite3`). Standart python.org Python ile kurulan `.venv` bu sorunu hiç yaşamaz ve daha küçük/temiz bir exe üretir.

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt pyinstaller
```

## PyInstaller (`build_pyinstaller.bat`)

- **`--onedir --windowed`** (onefile DEĞİL), ikon `icons/icon.ico`, veri: `icons/`, `ui/assets/fonts/`.
- **Neden onedir:** Instagram giriş penceresi `QtWebEngine` kullanır (bkz. [[instagram_login]]); QtWebEngine onefile'da güvenilmez (`QtWebEngineProcess.exe` bulunamıyor, yavaş açılış). onedir'de tüm bağımlılıklar (DLL'ler, `QtWebEngineProcess.exe`, kaynaklar) exe'nin yanında klasörde durur. PyInstaller'ın PyQt5 hook'ları QtWebEngine'i otomatik toplar (`instagram_login_dialog.py` import grafiğinde olduğu için).
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
