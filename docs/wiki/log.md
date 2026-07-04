# Değişiklik Günlüğü

Kronolojik kayıt, en yeni en üstte. Format: `## [YYYY-AA-GG] [İŞLEM_TİPİ] | Kısa Açıklama`

## [2026-07-04] INGEST | LLM Wiki sistemi kuruldu

`docs/wiki/` bilgi tabanı oluşturuldu: [[index]], [[rules]], [[log]], [[mimari]], [[yt_dlp_oto_guncelleme]], [[tema_sistemi]], [[paketleme]]. Proje köküne `CLAUDE.md` eklendi (wiki'yi her oturumda önce okuma kuralı).

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
