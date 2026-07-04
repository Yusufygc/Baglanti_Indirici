# Tema Sistemi (Koyu/Açık)

Bkz. [[index]] · İlgili: [[mimari]]

## Yapı

- `ui/themeing/theme.py` — `DARK_THEME` ve `LIGHT_THEME` sözlükleri (aynı anahtar seti: `background`, `surface`, `text`, `accent`, `border`, ...), `THEMES = {"dark": ..., "light": ...}`.
- `ui/themeing/style_sections.py` — her stil fonksiyonu (`global_styles`, `text_styles`, `container_styles`, `button_styles`, ...) artık `t` (aktif tema sözlüğü) parametresi alır; `main_stylesheet(theme_name="dark")` doğru sözlüğü seçip tüm bölümleri birleştirir.
- `ui/themeing/styles.py::StyleManager.get_main_stylesheet(theme_name)` — dışa açılan tek giriş noktası.
- `core/settings.py` — `load_theme()` / `save_theme()`: tercih `~/.baglanti_indirici/settings.json` içinde kalıcı tutulur (geçersiz/okunamaz değerde `"dark"` varsayılan).

## Toggle Akışı

`ui/window/main_window.py`:

- `MainWindow.__init__` içinde `self._theme_name = load_theme()` → `_init_ui()` → `_apply_theme()`.
- Toggle butonu (`btn_theme_toggle`, header'ın **sol üst köşesinde**, `objectName="themeToggleButton"`) `_on_theme_toggle()`'ı tetikler: tema adını çevirir, `save_theme()` çağırır, `_apply_theme()`'i tekrar çalıştırır.
- `_apply_theme()` üç şey yapar: `setStyleSheet(StyleManager.get_main_stylesheet(...))`, buton ikonunu günceller (`_THEME_TOGGLE_ICON = {"dark": "☀", "light": "🌙"}`), ve `_refresh_input_placeholders()` ile tüm `ModernInput` placeholder renklerini yeni temaya göre günceller (placeholder rengi `QPalette` ile ayarlandığı için QSS cascade'i otomatik yakalamaz, elle tazelenmesi gerekir).

## Bilinen Tuzaklar (Çözülmüş Hatalar)

1. **"Kutu" görünümü:** Genel `QWidget { background-color: ... }` kuralı her `QLabel`'a da uygulanıyordu; `#statusBar` (koyu `background_dark`) içindeki `#statusBarText`/`#footerText` etiketleri kendi (`background` rengi farklı) dikdörtgenini boyayıp kutu gibi görünüyordu. Çözüm: bu selektörlere `background: transparent` eklendi. Ayrıca `MainWindow.set_status()` içindeki inline `setStyleSheet()` çağrısına da `background: transparent` eklendi (cascade'e güvenmemek için).
2. **İkon kırpılması:** `themeToggleButton` başta `secondaryButton` stilini paylaşıyordu (`padding: 8px 14px`); 44-46px sabit genişlikte bu padding içeriği ~16px'e düşürüp emoji glifini kırpıyordu. Çözüm: `#themeToggleButton` için ayrı, `padding: 0` olan bir QSS kuralı tanımlandı.
3. **`QFontDatabase` çökmesi:** `FontManager` (`ui/assets/font_manager.py`) `QFontDatabase()` çağırır; bu, `QApplication` oluşturulmadan çağrılırsa **native crash** (Python exception değil) verir. Test/doğrulama scriptleri her zaman önce bir `QApplication` örneği oluşturmalı — bu yüzden `ui.themeing.styles` gibi modülleri `QApplication` olmadan bare script ile test etmeyin.

## Renk Paleti

Accent (cyan `#12C8E8`) her iki temada da sabit tutulur (marka tutarlılığı). Koyu tema near-black (`#0A0B10`) hedefler; açık tema beyaz yüzeyli (`#FFFFFF`), yüksek kontrastlı metin (`#161A22`) kullanır. `ModernButton` primary tipte sabit cyan glow (`QGraphicsDropShadowEffect`) uygular — her iki temada da kullanılır.
