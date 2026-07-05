# Kompakt Mod (Yuvarlak Bubble)

Bkz. [[index]] · İlgili: [[mimari]], [[tema_sistemi]]

## Problem

Kullanıcı bazen sadece hızlıca bir link yapıştırıp indirmeyi başlatmak istiyor; tam pencereyi açık tutmak/büyük tutmak gereksiz. İstenen: uygulama küçük yuvarlak bir simgeye küçülsün, ekranın bir köşesinde her zaman erişilebilir dursun, fare üzerine gelince yanında bir URL kutusu açılsın.

## Çözüm: Ayrı, Frameless Bubble Penceresi (MainWindow'u Frameless Yapmadan)

`MainWindow` (`ui/window/main_window.py`) düz `QWidget`, native çerçeveli, Windows'a özel koyu-başlık-çubuğu hack'i var (`_apply_dark_title_bar`). Bu pencereyi frameless bir bubble'a "büzmek" yerine **ayrı bir `CompactBubble(QWidget)` penceresi** kullanılır: kompakt moda geçişte `MainWindow.hide()` + bubble `.show()`; tam pencereye dönüşte tersi. `MainWindow` **yok edilmez, sadece gizlenir** — böylece alanlarındaki (URL, klasör, format, dosya adı) "son kullanılan ayarlar" hafızada kalır.

**Sıfır indirme-mantığı tekrarı:** Bubble'da URL gönderildiğinde tek satır çalışır: `self.url_input.setText(url); self._start_download()` — `MainWindow._start_download()` (main_window.py:725) ile birebir aynı yol. Yeni persistence/state yok.

### Bileşenler

- **`ui/window/compact_bubble.py`** (`CompactBubble(QWidget)`):
  - Pencere bayrakları: `Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool` (her zaman üstte, görev çubuğunda ikon yok).
  - `WA_TranslucentBackground` + **elle `paintEvent` ile yuvarlak/hap dolgusu** (`painter.drawRoundedRect(self.rect(), h/2, h/2)`). **Önemli:** QSS `border-radius`/`background-color` ile denendi ama üst-düzey frameless+translucent pencerede resize-animasyonu sonrası genişleyen alan boyanmıyordu (sağ taraf şeffaf kalıyordu — Qt/QSS arkaplan önbelleği eski boyuta kilitleniyor). `paintEvent` her resize'da yeniden çizildiği için bu sorunu tamamen bypass eder.
  - Daraltılmış: sabit 56×56 (tam daire, `radius = height/2 = 28`). Genişletilmiş: 360×56 hap şekli — `QHBoxLayout` ile [56px ikon][`ModernInput`]. **Layout margin tuzağı:** sağ kenar boşluğu layout `setContentsMargins`'e değil, `#compactUrlInput` QSS `padding`'ine konur; margin layout'ta olsaydı input gizliyken bile genişliği şişirip daireyi ovale çevirirdi (56→70px tespit edilip düzeltildi).
  - Hover: `enterEvent`/`leaveEvent` + `QPropertyAnimation(b"geometry")`. Ekran kenarına yakınsa (sağ kenar taşması) genişleme sola doğru yapılır.
  - Sürükleme: `mousePressEvent`/`mouseMoveEvent`/`mouseReleaseEvent` standart frameless-drag deseni, yalnızca ikon alanında aktif (ikon `WA_TransparentForMouseEvents` ile olayları `self`'e devrediyor; input alanı interaktif kalır, metin seçimiyle çakışmaz).
  - Çift tıklama (ikon üzerinde) → `restore_requested` sinyali → tam pencereye dönüş.
  - `url_submitted(str)` sinyali → `MainWindow._handle_compact_url`.
- **`ui/window/main_window.py`**: header'da yeni "◎" butonu (`btn_compact_mode`, `themeToggleButton` stiliyle aynı kare görünüm) → `_enter_compact_mode` (lazy `CompactBubble` oluşturur, `MainWindow.hide()`) / `_exit_compact_mode` (bubble gizlenir, pencere geri gösterilir). Tema değişince (`_apply_theme`) bubble varsa `apply_theme` ile senkronize edilir.
- **Sonuç geri bildirimi (yeşil/kırmızı):** indirme bitince bubble'ın dairesi rengini geçici değiştirir. **Dikkat — gerçek tetikleme noktası `ui/window/controller.py::MainWindowController._on_job_updated`'dır** (`job.status == COMPLETED/FAILED` iken `self.view.flash_compact_result(True/False)` çağrılır), `MainWindow.handle_finished`/`handle_error` DEĞİL — o metodlar hiçbir yerde `.connect()` edilmeyen ölü koddur (bir önceki deneme yanlışlıkla oraya bağlanmıştı ve hiç çalışmadı). `MainWindow.flash_compact_result(success)` → bubble görünüyorsa `CompactBubble.flash_result(success)` → daire rengi `LOG_COLORS["success"]` (yeşil) veya `LOG_COLORS["error"]` (kırmızı) olur + beyaz tik/çarpı glifi, ~1.6sn sonra normal accent rengine döner.
- **`ui/themeing/style_sections.py::compact_bubble_styles(t)`**: yalnızca `#compactBubbleIcon`/`#compactUrlInput` (şeffaf/kenarsız, `text_button` rengiyle kontrast — `#primaryButton`'ın accent-üzeri metin rengiyle aynı desen). `main_stylesheet()`'e KATILMAZ (global `QWidget{background-color}` kuralı translucent pencereyi bozardı).

### Doğrulama

Otomatik ekran görüntüsü ile doğrulandı: daraltılmış hal tam daire (artefaktsız), genişletilmiş hal dolu hap şekli + okunur placeholder metni. Uçtan uca akış (gerçek `MainWindow` + `CompactBubble`, offscreen değil) script ile test edildi: kompakt moda geçince ana pencere gizleniyor, bubble'a yazılan URL gönderiminde `controller.queue_service` üzerinde iş doğru URL ile oluşuyor, restore ile ana pencere geri geliyor. 62 test etkilenmedi (yeni dosyaya dokunan birim testi yok — UI görsel, manuel/ekran-görüntüsü doğrulaması esas).

### Kapsam Dışı (v1)

Bubble konumu yalnızca **aynı oturum içinde** hatırlanır (uygulama yeniden başlatıldığında sağ-alt köşeye döner). Kalıcı konum (`settings.json`'a `{x,y}`) kolay bir sonraki adım, talep gelirse eklenir.
