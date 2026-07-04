# Bağlantı İndirici — Wiki İçerik Haritası

Bu dosya wiki'nin giriş noktasıdır. Kod yazmadan, mimari karar vermeden veya soru yanıtlamadan önce bu dosya okunur; gerektiğinde alt sayfalara `[[bağlantı]]` üzerinden geçilir. Çalışma kuralları için bkz. [[rules]].

## Mimari

- [[mimari]] — Katman yapısı (core/, ui/, tests/), sorumluluk ayrımı, veri akışı.
- [[yt_dlp_oto_guncelleme]] — yt-dlp'nin exe dışına taşınması ve PyPI tabanlı oto-güncelleme sistemi (`core/update/`).
- [[tema_sistemi]] — Koyu/açık tema paleti, toggle mekanizması, kalıcı tercih (`ui/themeing/`, `core/settings.py`).

## Build & Dağıtım

- [[paketleme]] — PyInstaller ile tek-dosya exe üretimi ve Inno Setup ile Windows kurulum sihirbazı.

## Süreç

- [[rules]] — Commit mesajı kuralları ve kod kalitesi standartları.
- [[log]] — Kronolojik değişiklik kaydı (en yeni en üstte).

## Hızlı Referans

| Konu | Sayfa | Kritik Dosyalar |
|---|---|---|
| yt-dlp güncelleme | [[yt_dlp_oto_guncelleme]] | `core/update/`, `core/config.py`, `main.py` |
| Tema | [[tema_sistemi]] | `ui/themeing/theme.py`, `ui/window/main_window.py`, `core/settings.py` |
| Build | [[paketleme]] | `build_pyinstaller.bat`, `installer.iss` |
| Kurallar | [[rules]] | — |
