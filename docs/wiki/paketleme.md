# Paketleme ve Dağıtım

Bkz. [[index]] · İlgili: [[yt_dlp_oto_guncelleme]], [[mimari]]

## Build Ortamı

**Conda değil, temiz venv kullan.** Conda Python DLL'leri `Library\bin` altına ayırır; PyInstaller bunları bulamaz ve `sqlite3.dll`, `ffi.dll`, `liblzma.dll` gibi bağımlılıklar için elle `--add-binary` yaması gerektirir (native crash: `ImportError: DLL load failed while importing _sqlite3`). Standart python.org Python ile kurulan `.venv` bu sorunu hiç yaşamaz ve daha küçük/temiz bir exe üretir.

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt pyinstaller
```

## PyInstaller (`build_pyinstaller.bat`)

- `--onefile --windowed`, ikon `icons/icon.ico`, veri: `icons/`, `ui/assets/fonts/`.
- `--add-binary "ffmpeg.exe;."` — ffmpeg exe içine gömülür.
- `--exclude-module "yt_dlp"` — yt-dlp'nin gömülmesini engeller (bkz. [[yt_dlp_oto_guncelleme]]).
- Build sonrası script, build ortamındaki pip kurulu `yt_dlp` paketini `dist/lib/yt_dlp/` içine kopyalar (`python -c "import yt_dlp, os; print(os.path.dirname(yt_dlp.__file__))"`).
- Çıktı: `dist/BaglantiIndirici.exe` + `dist/lib/yt_dlp/`.

**Not:** Nuitka desteği kaldırıldı (tek build yolu PyInstaller). `build_nuitka.bat` artık yok.

## Inno Setup (`installer.iss`)

Proje kökündeki `installer.iss`, `dist/BaglantiIndirici.exe` ve `dist/lib/yt_dlp/*` dosyalarını alıp Windows kurulum sihirbazı üretir:

```powershell
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

- Çıktı: `installer_output/BaglantiIndirici_Setup.exe` (gitignore'da, `*.exe` kuralına takılır).
- Türkçe dil dosyası (`compiler:Languages\Turkish.isl`), masaüstü kısayolu seçeneği (task), Start Menu grubu, kurulum sonrası "çalıştır" seçeneği içerir.
- `AppId` GUID sabit tutulmalı — değişirse Windows aynı uygulamanın güncellemesi yerine ayrı bir kurulum olarak görür.

## Gitignore Notları

`*.exe`, `*.bat`, `*.spec`, `build/`, `dist/` gitignore'dadır (bazı `.bat`/`.spec` dosyaları yine de repo'da force-add edilmiş olabilir — `git status --ignored` ile kontrol et). `installer_output/` de `*.exe` kuralına takılıp otomatik yok sayılır.
