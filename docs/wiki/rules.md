# Kurallar — Commit ve Kod Kalitesi

Bkz. [[index]]

## Commit Mesajı Kuralları

Format: `tip: kısa açıklama` (Türkçe, büyük harfle başlamayan tip, ~50-70 karakter özet).

Kullanılan tipler (repo geçmişinden): `feat`, `fix`, `ui`, `tests`, `icons`, `build`, `docs`.

- Başlık satırı özet, gövde (varsa) **neden** yapıldığını açıklar — kod zaten **ne** yaptığını gösterir, tekrar etme.
- Kök neden biliniyorsa `fix` commit'lerinde mutlaka belirt (örn. "genel QWidget arka plan kuralı etikete de sızıyordu").
- **AI/asistan referansı eklenmez** — `Co-Authored-By` veya benzeri satır commit mesajına yazılmaz.
- Birbiriyle alakasız değişiklikler (örn. bağımsız bir bug fix + yeni bir özellik) ayrı commit'lere bölünür; tek bir oturumda üretilen ama birbirine bağlı (aynı özelliğin parçaları) değişiklikler tek commit'te toplanabilir.
- Sadece kullanıcı açıkça istediğinde commit/push yapılır — istenmeden proaktif commit atılmaz.
- `git push --force` / `--force-with-lease` yalnızca kullanıcı açıkça onayladıktan sonra ve sebebi net şekilde anlatıldıktan sonra çalıştırılır (bkz. [[log]] içindeki geçmiş bir örnek).

## Kod Kalitesi Standartları

- **Yorum yazma, gerekmedikçe:** Sadece "neden" açık olmayan yerlerde (gizli bir kısıt, ince bir invariant, belirli bir hatanın workaround'u) tek satırlık yorum eklenir. "Ne yaptığını" anlatan yorumlar yazılmaz — iyi isimlendirme zaten bunu gösterir.
- **Aşırı mühendislik yok:** Görev neyi gerektiriyorsa o kadar kod. Varsayımsal gelecek ihtiyaçlar için soyutlama eklenmez. Üç benzer satır, erken soyutlamadan iyidir.
- **Mevcut deseni tekrar et:** Yeni bir arka plan işi eklerken `core/*/worker.py` desenini (QThread + WorkerSignals + factory enjeksiyonu) kopyala — bkz. [[mimari]].
- **Test edilebilirlik için PyQt5 izolasyonu:** `core/*/__init__.py` dosyaları PyQt5 gerektiren `worker.py` modüllerini re-export etmez; worker sınıfları `from core.X.worker import Y` ile doğrudan alt modülden import edilir. Bu sayede `tests/` PyQt5 kurulu olmayan ortamda da çalışır.
- **Build ortamı:** Conda değil, temiz `.venv` (python.org Python) kullan — bkz. [[paketleme]].
- **Değişiklik sonrası doğrulama:** UI değişikliklerinde uygulamayı gerçekten çalıştırıp (offscreen veya görünür) crash olmadığını doğrula; sadece syntax/type check yeterli değildir. `QApplication` oluşturulmadan `QFontDatabase`/diğer Qt GUI sınıfları çağrılmaz (native crash riski) — bkz. [[tema_sistemi]] bilinen tuzaklar.
- **Minimal diff:** Sadece istenen değişikliğe dokunulur; ilgisiz refactor/temizlik aynı commit'e karıştırılmaz.
