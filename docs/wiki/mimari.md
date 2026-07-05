# Mimari

Bkz. [[index]] için genel harita.

PySide6 masaüstü uygulaması; UI ve iş mantığı ayrı katmanlarda tutulur.

## Katmanlar

```
main.py                 # Giris noktasi, QApplication + harici yt_dlp sys.path kaydi
core/
├── config.py            # get_base_path / get_ffmpeg_path / get_yt_dlp_lib_dir
├── settings.py           # Kalici kullanici tercihleri (tema) - bkz. [[tema_sistemi]]
├── domain/                # Saf veri modelleri (DownloadOptions, DownloadJob, JobStatus...)
├── download/              # YoutubeDL entegrasyonu, worker (QThread), progress hook zinciri
├── queue/                 # DownloadQueueService - FIFO indirme kuyrugu
├── history/               # SQLite tabanli gecmis repository (~/.baglanti_indirici/history.sqlite3)
├── update/                # yt-dlp oto-guncelleme - bkz. [[yt_dlp_oto_guncelleme]]
├── platform/              # Platform algilama (YouTube/TikTok/Instagram/...)
├── instagram/             # Instagram oturum/cerez saklama (saf) - bkz. [[instagram_login]]
└── web/                   # Web media extractor
ui/
├── window/                # MainWindow (view) + MainWindowController
├── themeing/               # Renk paleti, QSS uretimi - bkz. [[tema_sistemi]]
├── widgets/                # ModernCard, ModernButton, ModernInput, SegmentControl
└── assets/                 # Font yonetimi, ikonlar
tests/                    # pytest, PySide6 gerektirmeyen modüller icin GUI'siz calisir
```

## Kritik Prensip: Controller/Worker Ayrımı

`ui/window/controller.py` (`MainWindowController`) UI ile iş mantığı arasındaki köprüdür. Ağır işler (indirme, güncelleme kontrolü/kurulumu) `QThread` alt sınıflarında (`core/download/worker.py`, `core/update/worker.py`) çalışır; UI thread'i asla bloklanmaz. Yeni bir arka plan işi eklerken bu deseni tekrarla: `WorkerSignals` (QObject + Signal) + `QThread.run()` + controller'da `_ensure_worker`/`factory` enjeksiyonu (test edilebilirlik için).

## Test Edilebilirlik Notu

`core/*/__init__.py` dosyaları bilerek PySide6 gerektiren `worker.py` modüllerini re-export **etmez** (örn. `core/download/__init__.py`, `core/update/__init__.py`). Böylece `tests/` klasöründeki testler PySide6 kurulu olmayan ortamlarda da çalışabilir. Worker sınıfları her zaman `from core.X.worker import Y` şeklinde doğrudan alt modülden import edilir (bkz. `ui/window/controller.py`).

## Kuyruk ve Geçmiş Semantiği

- **Geçmiş yalnızca başarıyla tamamlanan (`COMPLETED`) indirmeleri içerir.** `HistoryRepository.list_recent()` SQL düzeyinde `WHERE status = 'completed'` ile filtreler; `ui/window/main_window.py::render_history()` de savunma amaçlı yalnızca `COMPLETED` işleri gösterir. Başarısız/iptal işler geçmişe düşmez.
- **İptal edilen iş kalıntı bırakmaz.** `DownloadQueueService.mark_cancelled()` işi hem bellekten (`_jobs`) hem geçmiş veritabanından (`HistoryRepository.delete(job_id)`) tamamen siler; yalnızca UI'a durum bildirmek için iş nesnesini döndürür.
- **İptalde yarım dosya temizliği.** `DownloadEngine`, progress hook'ta yt-dlp'nin `tmpfilename`/`filename` yollarını biriktirir; `CancelledDownload` yakalandığında `_cleanup_partial_files()` ile `.part`, `.ytdl`, `.temp` ve fragment (`.part-Frag*`) dosyalarını indirilenler klasöründen siler — iptal sonrası bozuk dosya kalmaz.
- **Enter ile kuyruğa alma:** URL veya dosya adı alanında Enter (`returnPressed`) `_start_download`'ı tetikler.

## Hata Yönetimi ve Loglama
Bkz. [[hata_yonetimi_ve_loglama]] — global `sys.excepthook` güvenlik ağı ve `core/logger.py`.

## Build/Dağıtım
Bkz. [[paketleme]].
