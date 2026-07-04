# yt-dlp Oto-Güncelleme

Bkz. [[index]] · İlgili: [[mimari]], [[paketleme]]

## Problem

yt-dlp sık güncelleme çıkarır (YouTube değişiklikleri, botlama savaşı). Eskiden `import yt_dlp` pip paketi olarak PyInstaller onefile exe'nin içine statik gömülüyordu — her güncelleme için tüm uygulamanın rebuild + yeniden dağıtımı gerekiyordu.

## Çözüm: Harici Python Paketi Swap

yt-dlp saf Python paketidir (derlenmiş binary değil). Exe'ye gömmek yerine exe'nin **yanında**, kalıcı bir klasörde (`lib/yt_dlp/`) tutulur:

- `core/config.py::get_yt_dlp_lib_dir()` — `ffmpeg` yolu bulma deseniyle tutarlı: önce exe yanındaki `lib/`, sonra proje kökündeki `lib/` (dev fallback), yoksa `None` (normal pip/site-packages `yt_dlp` kullanılır — geliştirici ortamında davranış değişmez).
- `main.py` — diğer TÜM importlardan önce bu klasörü `sys.path.insert(0, ...)` ile ekler. Böylece her `import yt_dlp` (örn. `core/download/yt_dlp_client.py`) bu harici kopyadan çözülür.
- `BaglantiIndirici.spec` / `build_pyinstaller.bat` — `excludes=['yt_dlp']` / `--exclude-module yt_dlp` ile PyInstaller'ın yt_dlp'yi statik gömmesi engellenir; build sonrası pip kurulu yt_dlp, `dist/lib/yt_dlp/` içine kopyalanır (bkz. [[paketleme]]).

**Neden bu şekilde güvenli:** PyInstaller onefile modunda gömülü dosyalar her çalıştırmada `sys._MEIPASS` altında geçici bir dizine açılır — orada "güncelleme" yapılsa bile kalıcı olmaz. Harici `lib/yt_dlp/` klasörü ise normal, kalıcı bir data klasörüdür; OS dosya kilidi sorunu yoktur çünkü değişen şey **çalışan exe değil**, yanındaki bir klasördür.

## Güncelleme Akışı (`core/update/`)

- `pypi_client.py::PyPiClient` — PyPI JSON API'den (`https://pypi.org/pypi/yt-dlp/json`) en son sürüm + wheel URL + sha256 çeker (stdlib `urllib`, ekstra bağımlılık yok).
- `yt_dlp_updater.py::YtDlpUpdater` — `check_for_update()` (tuple bazlı `YYYY.MM.DD[.rev]` sürüm kıyaslama), `install_update()` (wheel indir → sha256 doğrula → zip'ten `yt_dlp/` çıkar → staging klasörüne aç → `os.rename` ile atomik yer değiştirme, hata durumunda rollback).
- `worker.py` — `UpdateCheckWorker` (hafif, sadece kıyaslar) ve `UpdateInstallWorker` (indirir+kurar), ikisi de `QThread` (bkz. [[mimari]] worker deseni).
- `ui/window/controller.py::MainWindowController` — `check_for_yt_dlp_update()` (açılışta otomatik, sessiz hata), `install_yt_dlp_update()` (sadece kullanıcı onayıyla).
- `ui/window/main_window.py` — `show_update_available()` hem `btn_yt_dlp_update` butonunu gösterir hem durum çubuğuna (`set_status`) net bir mesaj yazar.

**Karar — otomatik kontrol + manuel onaylı kurulum:** Açılışta sessizce kontrol edilir (offline'da hata popup'ı çıkmaz), ama indirme/kurulum sadece kullanıcı butona tıklarsa başlar (izinsiz arka plan trafiği yok).

**Önemli davranış notu:** Kurulum diskte anında etkili olur ama çalışan process zaten `yt_dlp`'yi `sys.modules`'a yüklediyse bellek kopyası değişmez (`importlib.reload` güvenilir değil, denenmez) — kullanıcıya her zaman "yeniden başlatın" mesajı gösterilir.

## Testler

`tests/test_pypi_client.py`, `tests/test_yt_dlp_updater.py` — sahte HTTP/wheel ile network olmadan test eder.
