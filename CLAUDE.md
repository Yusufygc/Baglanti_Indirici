# Proje ve LLM Wiki Anayasası

Bu projede `docs/wiki/` bir bilgi tabanıdır (LLM Wiki). Sadece kod yazmak değil, alınan kararları, mimariyi ve bağlamı bu wiki üzerinde güncel ve bağlantılı tutmak da görevin parçasıdır.

## Zorunlu Çalışma Akışı

- **Önce oku:** Kod yazmadan, mimari karar vermeden veya proje hakkında detaylı bir soruya cevap vermeden önce `docs/wiki/index.md`'yi oku; gerekirse oradaki `[[bağlantı]]`'ları takip ederek ilgili alt sayfaları incele. Projeyi sıfırdan keşfetme, birikmiş bilgiyi kullan.
- **Proaktif güncelleme:** Yeni bir bağımlılık eklendiğinde, bir yapılandırma/mimari karar alındığında veya karmaşık bir sistem tasarlandığında, ilgili wiki sayfasını güncelle veya yeni sayfa oluştur — bunu hafızada tutup unutma.
- **Bağlantısallık:** Her yeni wiki sayfasında Obsidian tarzı `[[sayfa_adi]]` ile ilgili sayfalara atıf yap. Öksüz (hiçbir yere bağlanmayan) sayfa bırakma; `docs/wiki/index.md`'ye mutlaka ekle.

## Kritik Dosyalar

- `docs/wiki/index.md` — tüm wiki'nin içerik haritası, kategorilere ayrılmış sayfa listesi.
- `docs/wiki/log.md` — kronolojik değişiklik kaydı, en yeni giriş en üstte: `## [YYYY-AA-GG] [İŞLEM_TİPİ] | Kısa Açıklama`.
- `docs/wiki/rules.md` — commit mesajı kuralları ve kod kalitesi standartları (bkz. bu dosya, her commit/kod değişikliğinde geçerli).

## Operasyon Komutları

- **[INGEST]** ("Bunu ingest et"): Kaynağı oku/analiz et → yeni wiki sayfası oluştur veya mevcut sayfayı güncelle → `index.md`'ye link ekle → `log.md`'ye kaydet.
- **[QUERY]** (detaylı proje sorusu): Önce `index.md` üzerinden ilgili sayfaları bul ve oku, genel bilgiyle değil wiki'deki bağlamla cevap ver. Cevap kalıcı bir mimari karar taşıyorsa, wiki'ye yeni sayfa olarak ekle.
- **[LINT]** ("Wiki'yi lint et"): `docs/wiki/` içindeki çelişkileri, eskimiş kararları, öksüz sayfaları ve kırık `[[bağlantı]]`ları tara; rapor sun, onay sonrası düzelt.

## Commit ve Kod Kuralları

Bkz. `docs/wiki/rules.md` — özellikle: commit mesajlarına AI/asistan referansı eklenmez, format `tip: kısa açıklama` (Türkçe), yalnızca kullanıcı açıkça istediğinde commit/push yapılır.
