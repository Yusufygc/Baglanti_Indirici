# Hata Yönetimi ve Loglama

Bkz. [[index]] · İlgili: [[mimari]]

## Kök Neden: "Çöktü" Raporu

Kullanıcı, derlenmiş exe'de Instagram/YouTube URL'lerinden indirme denerken uygulamanın hiçbir hata göstermeden çöktüğünü bildirdi. Kod incelemesi ve canlı doğrulama ile kök neden bulundu:

`ui/window/main_window.py::_start_download()` (Qt slot) → `ui/window/controller.py::enqueue_download()` → `core/queue/service.py::DownloadQueueService.enqueue()` → `core/platform/registry.py::PlatformRegistry.normalize_url()` zincirinde **hiçbir try/except yoktu**. `normalize_url` içindeki `urllib.parse.urlparse()` çağrısı belirli bozuk URL biçimlerinde (örn. geçersiz IPv6 parantez notasyonu — `http://[bozuk` gibi kopyala-yapıştır artefaktları) `ValueError: Invalid IPv6 URL` fırlatıyordu. Bu, bir Qt slot'u içinde yakalanmamış bir Python exception'ıydı — **Qt (PyQt5/PySide6), slot içinde yakalanmamış exception'larda `sys.excepthook`'u çağırır ve varsayılan davranış process'i kapatır**. `--windowed` modda bu, sessiz bir çöküş olarak görünür. (Proje artık PySide6 kullanıyor; bu davranış aynı, `install_excepthook()` hâlâ gerekli.)

**Doğrulama:** `_verify_crash_fix.py` (geçici) ile `http://[bozuk` URL'si canlı denendi, `~/.baglanti_indirici/logs/app.log`'da tam olarak `core/platform/registry.py:27` satırında `ValueError: Invalid IPv6 URL` yakalandı — hipotez kanıtlandı.

## Çözüm

1. **Somut boşluk kapatıldı:** `ui/window/controller.py::enqueue_download()` artık `queue_service.enqueue()` çağrısını try/except'e alıyor; hata durumunda loglanıp `view.set_status(..., error=True)` ile kullanıcıya gösteriliyor, `None` dönüyor — akış devam ediyor, uygulama çökmüyor.
2. **Genel güvenlik ağı:** `core/logger.py::install_excepthook()` global `sys.excepthook`'u override eder — artık ÖNGÖRÜLEMEYEN başka bir yakalanmamış exception da (herhangi bir Qt slot'unda veya `QThread.run()` içinde) process'i sonlandırmaz, sadece loglanır ve event loop çalışmaya devam eder. `main.py`'de `_register_external_yt_dlp()`'ten hemen sonra, `QApplication` oluşturulmadan önce kurulur.
3. **Sessiz hata kaybı giderildi:** `core/download/worker.py::DownloadQueueWorker.run()` ve `core/update/worker.py` içindeki mevcut `except` bloklarına loglama eklendi — indirme/güncelleme hataları artık sadece UI'da geçici bir mesaj olarak gösterilip kaybolmuyor, `app.log`'a da kalıcı olarak yazılıyor.

## `core/logger.py`

- `get_logger(name: str) -> logging.Logger` — `"baglanti_indirici.<name>"` adıyla logger döner. İlk çağrıda `RotatingFileHandler` (`<exe_dizini>/logs/app.log`, 2MB × 3 yedek, UTF-8) tek seferlik kurulur. **Log konumu `~/.baglanti_indirici/` değil, `core/config.py::get_base_path()`** — yani exe'nin (frozen) veya proje kökünün (dev) yanındaki `logs/` klasörü. Kullanıcının log dosyasını kolayca bulup paylaşabilmesi için bilerek kullanıcı profili yerine uygulama dizinine konuldu.
- `install_excepthook()` — `sys.excepthook` ve `threading.excepthook`'u ayarlar (ikincisi `QThread` için no-op'tur ama düşük maliyetli ek güvenlik — Qt, virtual method reimplementation'lardan (örn. `QThread.run()`) sızan exception'ları zaten `sys.excepthook` üzerinden yönlendirir).
- `enable_native_crash_dump()` — `faulthandler.enable(file=..., all_threads=True)` ile Python exception olarak YAKALANAMAYAN native çökmeleri (segfault, access violation) `logs/native_crash.log`'a yazar. Dosya nesnesi modül seviyesinde referansta tutulur (GC tarafından kapatılmasın diye). `main.py`'de `install_excepthook()`'tan hemen sonra çağrılır.

## Kullanım Deseni

Yeni bir modülde loglama eklerken:
```python
from core.logger import get_logger
logger = get_logger("modul_adi")
...
except Exception as exc:
    logger.exception("Kisa aciklama: baglam=%s", deger)
```
`logger.exception(...)` otomatik olarak traceback'i de log dosyasına yazar (`exc_info` gerekmez, `except` bloğu içinde çağrıldığı sürece).

## Test

`tests/test_logger.py` — logger yapılandırması ve excepthook'un exception'ı yutup process'i sonlandırmadığını doğrular. `tests/test_controller_error_handling.py` — `enqueue_download`'ın bozuk URL/servis hatasında çökmediğini, `view.set_status(error=True)` çağrıldığını doğrular (bildirilen çöküş senaryosunun regresyon testi).

## Takip: "Instagram reels kuyruğa alıyor ama çöküyor" Raporu

Yukarıdaki düzeltme sonrası kullanıcı Instagram reels'in kuyruğa girip sonra çöktüğünü bildirdi. `app.log`'daki gerçek kayıt incelendi — asıl indirme denemesi `yt_dlp.utils.DownloadError` ile düzgün başarısız oluyordu ("Instagram sent an empty media response", Instagram'ın kendisi login istiyor — gerçek bir çökme değil, normal başarısız indirme). Ama derinlemesine inceleme sırasında **iki farklı, gerçek hata** bulundu:

1. **"queued"/"running" ham İngilizce sızıntısı** — `ui/window/main_window.py::_queue_row()` (aktif kuyruk satırı) yanlışlıkla `_history_summary()`'yi çağırıyordu; o fonksiyonun `status_labels` sözlüğünde sadece COMPLETED/FAILED/CANCELLED çevirisi vardı, QUEUED/RUNNING yoktu, fallback `job.status.value` ham İngilizce metni gösteriyordu. `_history_row()` da tam tersi hatayla gereksiz genişletilmiş `_job_summary()`'yi çağırıyordu. İki fonksiyon doğru yerlere bağlandı, fallback da `"Bilinmiyor"` yapıldı (asla ham İngilizce çıkmasın diye).

2. **`ModuleNotFoundError` riski (build'de gizli, whack-a-mole)** — yt_dlp `--exclude-module` ile build'den hariç tutulunca, `import yt_dlp` çalışma zamanında `optparse`, sonra `http.cookies` gibi stdlib modüllerini bulamıyordu (PyInstaller analiz etmediği için bunları paketlemiyordu). **Bu, potansiyel olarak HER indirme denemesini etkileyebilecek bir hataydı** (platform fark etmeksizin). Çözüm: bkz. [[yt_dlp_oto_guncelleme]] — yt_dlp artık exclude edilmiyor, normal analiz edilip yedek olarak gömülüyor.

**Dahil edilen ek güvenlik katmanı:** `enable_native_crash_dump()` (faulthandler) — eğer bir sonraki "çöktü" raporu native bir crash'se (Python exception olarak hiç yakalanamayan), `logs/native_crash.log`'da iz kalır.

**Sonraki adım:** Kullanıcıdan bir dahaki "çöktü" durumunda `logs/app.log` ve `logs/native_crash.log` dosyalarını (artık uygulama dizininde, kolay bulunur) paylaşması istendi — kesin teşhis için gerekli.

## "Video inmiyor" — Instagram Login Duvarı (gerçek kök neden)

Kullanıcı "Instagram reels inmiyor, eskiden inebiliyordu" diye bildirdi. Kapsamlı canlı test + yt-dlp bug tracker incelemesiyle kök neden kesin olarak bulundu: **sorun uygulamada veya kodda değil — Instagram, 2-3 Temmuz 2026 civarı API'sini değiştirip gönderiler/reels için giriş (login) zorunlu hale getirdi.**

**Kanıt zinciri (hepsi bu oturumda doğrulandı):**
1. **Sıfır-cookie testi:** Başarısız reel URL'si, hiçbir cookie olmadan (kodun orijinal davranışı) da `"Instagram sent an empty media response"` veriyor → cookie ile ilgili hiçbir ekleme sebep değil.
2. **Sahte-ID testi:** Var olmayan bir reel ID'si (`C8yEXaMPLE1`) bile aynı "empty media response"u veriyor → Instagram bu IP'den **tüm kimliksiz erişimi** blokluyor; post bazlı değil, genel login duvarı.
3. **YouTube kontrolü:** YouTube cookie'siz sorunsuz iniyor (canlı: "Me at the zoo", 11 format) → uygulama genel olarak sağlam, yalnızca Instagram etkileniyor.
4. **yt-dlp bug tracker (GitHub API ile):** #17074 ("empty media response WITHOUT cookies") ve #17124, 2-3 Temmuz 2026'da açılıp kapandı; dünya çapında kullanıcılar *"everything worked correctly yesterday"*, *"just stopped to work"* diyor. Bakımcı (bashonly): extractor'da anlamlı değişiklik yok — sorun Instagram tarafında.
5. **Chrome cookie'si de okunamıyor:** #10927 — Chrome v127+ çerezleri "Application-Bound Encryption" ile şifreliyor, yt-dlp bunu çözemiyor (kodda ABE desteği yok); Firefox da kurulu değil. Yani cookie tabanlı otomatik yaklaşım bu makinede zaten çalışmıyor.

**Denenen ve geri alınan yaklaşım:** Kısa süreliğine `cookiesfrombrowser` (önce Chrome, sonra Firefox) fallback zinciri eklendi. Sorunu çözmedi (yukarıdaki #10927 + Firefox-yok) ve kullanıcıya gürültülü İngilizce hatalar gösterdi (`Could not copy Chrome cookie database`, `Failed to decrypt with DPAPI`). Kullanıcı kararıyla **tamamen geri alındı**.

**Uygulanan çözüm — temiz no-cookie + net Türkçe mesaj:**
- `core/download/yt_dlp_client.py` cookie'siz orijinal haline döndürüldü; `build_options()` içinde `cookiesfrombrowser` yok. Public içerik (YouTube dahil) eskisi gibi çalışır.
- `download()` → `_run()` + `_friendly_error(exc)`: hata mesajında login duvarı izleri (`_LOGIN_REQUIRED_MARKERS = ("empty media response", "login required", ...)`) varsa, ham İngilizce yerine net Türkçe döndürür: *"Instagram bu içerik için giriş (login) yapılmasını istiyor. Herkese açık olmayan gönderiler artık giriş yapmadan indirilemiyor (Instagram tarafındaki bir kısıt)."* Diğer tüm hatalar olduğu gibi geçer.
- Test: `tests/test_yt_dlp_client.py` — empty-media hatası → Türkçe mesaj; alakasız hata (HTTP 404) → olduğu gibi geçer. Canlı olarak da doğrulandı.

**Kalıcı çözüm (uygulandı, 5 Temmuz 2026 uçtan uca doğrulandı):** Login-gerekli Instagram içeriği için kullanıcının kendi Chrome/Edge tarayıcısı CDP ile sürülüp oturum çerezleri (HttpOnly `sessionid`) hafızadan okunur (gömülü QtWebEngine denendi ama Instagram'ın giriş duvarını geçemedi) — kullanıcı bir kez giriş yapar, çerezler saklanıp yt-dlp'ye `cookiefile` olarak verilir. Detay ve mimari: [[instagram_login]]. `_friendly_error`'ın gösterdiği net Türkçe mesaj hâlâ geçerli (oturum yoksa/dolmuşsa kullanıcı giriş yapmaya yönlendirilir).
