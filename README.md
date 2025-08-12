# Bağlantı İndirici 📥

Modern ve kullanıcı dostu bir PyQt5 tabanlı video/ses indirici uygulaması. YouTube, TikTok, Instagram, Facebook ve X (Twitter) gibi popüler platformlardan video ve ses dosyalarını kolayca indirin.

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

## 🌟 Özellikler

### 🎯 Temel Özellikler
- **Çoklu Platform Desteği**: YouTube, TikTok, Instagram, Facebook, X (Twitter)
- **Video ve Ses İndirme**: İstediğiniz formatta içerik indirin
- **Özel Dosya Adlandırma**: Dosyalarınıza özel isim verebilirsiniz
- **Akıllı Klasör Organizasyonu**: Platform bazında otomatik klasör oluşturma
- **Gerçek Zamanlı İlerleme**: İndirme durumunu canlı takip edin
- **İptal Edilebilir İndirmeler**: İstediğiniz zaman indirmeyi durdurun

### 🎨 Kullanıcı Arayüzü
- **Modern Tasarım**: Koyu tema ile göz yormayan arayüz
- **Sezgisel Kullanım**: Basit ve anlaşılır kontroller
- **Detaylı Log Sistemi**: Her adımı takip edebileceğiniz log ekranı
- **İlerleme Çubuğu**: Görsel indirme durumu göstergesi
- **Hızlı Erişim**: İndirme klasörünü tek tıkla açın

## 📋 Sistem Gereksinimleri

### Minimum Gereksinimler
- **Python**: 3.7 veya üzeri
- **İşletim Sistemi**: Windows 10/11, macOS 10.14+, Ubuntu 18.04+
- **RAM**: 2 GB (4 GB önerilir)
- **Disk Alanı**: 500 MB boş alan

### Gerekli Bileşenler
- **FFmpeg**: Video/ses işleme için
- **Python Kütüphaneleri**: PyQt5, yt-dlp

## 🚀 Kurulum

### 1. Depoyu Klonlayın
```bash
git clone https://github.com/yourusername/baglanti-indirici.git
cd baglanti-indirici
```

### 2. Sanal Ortam Oluşturun (Önerilen)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Gerekli Paketleri Yükleyin
```bash
pip install -r requirements.txt
```

**requirements.txt** dosyası:
```
PyQt5==5.15.9
yt-dlp==2023.12.30
```

### 4. FFmpeg Kurulumu

#### Windows
1. [FFmpeg resmi sitesinden](https://ffmpeg.org/download.html#build-windows) indirin
2. Dosyaları `C:\ffmpeg\` klasörüne çıkarın
3. `indirici.py` dosyasındaki `ffmpeg_path` değişkenini kontrol edin:
```python
ffmpeg_path = r'C:\ffmpeg\bin\ffmpeg.exe'
```
yaralanabileceginiz youtube linki = https://www.youtube.com/watch?v=KBnyOH1o5Ms

#### macOS
```bash
# Homebrew ile
brew install ffmpeg

# MacPorts ile
sudo port install ffmpeg
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

### 5. Uygulamayı Çalıştırın
```bash
python main.py
```

## 📖 Kullanım Kılavuzu

### Temel Kullanım
1. **URL Girin**: İndirmek istediğiniz videonun bağlantısını yapıştırın
2. **Klasör Seçin**: İndirme konumunu belirleyin (varsayılan: Downloads)
3. **Format Seçin**: Video veya Ses seçeneğinden birini seçin
4. **Dosya Adı** (İsteğe bağlı): Özel bir isim verebilirsiniz
5. **İndir**: İndirme işlemini başlatın

### Desteklenen Platformlar ve URL Formatları

| Platform | Örnek URL | Video | Ses |
|----------|-----------|-------|-----|
| YouTube | `https://www.youtube.com/watch?v=...` | ✅ | ✅ |
| TikTok | `https://www.tiktok.com/@user/video/...` | ✅ | ✅ |
| Instagram | `https://www.instagram.com/p/...` | ✅ | ✅ |
| Facebook | `https://www.facebook.com/watch?v=...` | ✅ | ✅ |
| X (Twitter) | `https://twitter.com/user/status/...` | ✅ | ✅ |

### Dosya Adlandırma Sistemi
- **Video**: `dosya_adi_video.mp4` veya `orijinal_baslik_video.mp4`
- **Ses**: `dosya_adi_audio.mp3` veya `orijinal_baslik_audio.mp3`

### Klasör Organizasyonu
```
Downloads/
├── YouTube/
│   ├── video1_video.mp4
│   └── music1_audio.mp3
├── TikTok/
│   └── dance_video.mp4
└── Instagram/
    └── story_video.mp4
```

## 🔧 Yapılandırma

### FFmpeg Yolu Ayarlama
`indirici.py` dosyasında FFmpeg yolunu sisteminize göre ayarlayın:

```python
# Windows için
ffmpeg_path = r'C:\ffmpeg\bin\ffmpeg.exe'

# macOS/Linux için (genellikle PATH'de)
ffmpeg_path = 'ffmpeg'
```

### Video Kalite Ayarları
İndirme kalitesini değiştirmek için `indirici.py` dosyasındaki format ayarlarını düzenleyebilirsiniz:

```python
# Yüksek kalite video için
'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'

# Düşük kalite video için
'format': 'worstvideo+worstaudio/worst'
```

### Ses Kalite Ayarları
```python
'postprocessors': [{
    'key': 'FFmpegExtractAudio',
    'preferredcodec': 'mp3',
    'preferredquality': '320',  # 128, 192, 256, 320
}]
```

## 🗂️ Proje Yapısı

```
baglanti-indirici/
├── main.py              # Ana uygulama başlatıcı
├── arayuz.py            # PyQt5 kullanıcı arayüzü
├── indirici.py          # İndirme işlemleri ve yt-dlp entegrasyonu
├── requirements.txt     # Python bağımlılıkları
├── README.md           # Bu dosya
└── .gitignore          # Git ignore kuralları
```

### Dosya Açıklamaları

#### `main.py`
Uygulamanın giriş noktası. PyQt5 uygulamasını başlatır.

#### `arayuz.py`
- **UygulamaArayuzu**: Ana PyQt5 widget sınıfı
- Modern CSS stilleri ile tasarlanmış kullanıcı arayüzü
- Sinyal/slot mekanizması ile thread güvenli iletişim
- Kullanıcı etkileşimleri ve arayüz güncellemeleri

#### `indirici.py`
- **Indirici**: QThread tabanlı indirme sınıfı
- **IndiriciSinyalleri**: PyQt5 sinyalleri için yardımcı sınıf
- yt-dlp entegrasyonu ve FFmpeg yapılandırması
- Platform algılama ve klasör organizasyonu

## ⚙️ Gelişmiş Özellikler

### Thread Güvenli Mimari
Uygulama, indirme işlemlerini ana UI thread'den ayrı bir thread'de çalıştırır:
- UI donmaz ve yanıt vermeye devam eder
- Gerçek zamanlı ilerleme güncellemeleri
- Güvenli indirme iptali

### Sinyal/Slot İletişimi
```python
# Sinyal tanımlamaları
platform_belirlendi = pyqtSignal(str)
ilerleme_guncellendi = pyqtSignal(int, str)
indirme_bitti = pyqtSignal()

# Slot bağlantıları
self.indirici_thread.sinyaller.ilerleme_guncellendi.connect(self.ilerleme_guncelle)
```

### Hata Yönetimi
- Ağ bağlantı hatalarını yakalar
- Geçersiz URL'leri tespit eder
- FFmpeg eksikliği durumunda uyarır
- Disk alanı yetersizliği kontrolü

## 🐛 Sorun Giderme

### Yaygın Sorunlar ve Çözümleri

#### 1. FFmpeg Bulunamadı Hatası
```
Hata: ffmpeg could not be found
```
**Çözüm**: 
- FFmpeg'in doğru şekilde kurulu olduğundan emin olun
- `indirici.py` dosyasındaki `ffmpeg_path` yolunu kontrol edin

#### 2. SSL Sertifika Hatası
```
Hata: SSL certificate verify failed
```
**Çözüm**: 
```python
# yt-dlp seçeneklerine ekleyin
'--no-check-certificate': True
```

#### 3. Platform Desteklenmiyor
```
Hata: Geçersiz veya desteklenmeyen URL
```
**Çözüm**: 
- URL'nin doğru formatta olduğunu kontrol edin
- Platform desteği için `platform_belirle()` fonksiyonunu güncelleyin

#### 4. İndirme Çok Yavaş
**Çözüm**: 
- İnternet bağlantınızı kontrol edin
- Video kalite ayarlarını düşürün
- Farklı bir DNS sunucusu deneyin

### Log Analizi
Uygulama, detaylı log mesajları sağlar:
- **Yeşil**: Başarılı işlemler
- **Kırmızı**: Hata mesajları
- **Turuncu**: Uyarı ve iptal mesajları
- **Beyaz**: Bilgi mesajları

## 🤝 Katkıda Bulunma

### Geliştirme Ortamı Kurulumu
1. Depoyu fork edin
2. Geliştirme dalı oluşturun: `git checkout -b feature/yeni-ozellik`
3. Değişikliklerinizi yapın
4. Testlerinizi çalıştırın
5. Commit yapın: `git commit -am 'Yeni özellik eklendi'`
6. Push yapın: `git push origin feature/yeni-ozellik`
7. Pull Request oluşturun

### Kod Standartları
- PEP 8 Python kod standardına uyun
- Türkçe ve İngilizce yorumlar ekleyin
- Docstring'leri güncel tutun
- Type hint'leri kullanın

## 📝 Değişiklik Günlüğü

### v1.0.0 (12/08/2025)
- ✅ İlk sürüm yayınlandı
- ✅ YouTube, TikTok, Instagram desteği
- ✅ Video/Ses indirme seçenekleri
- ✅ Modern PyQt5 arayüzü


## 📄 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakınız.

## 🙏 Teşekkürler

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Güçlü indirme motoru
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - Modern GUI framework
- [FFmpeg](https://ffmpeg.org/) - Multimedya işleme

## 📞 İletişim

- **GitHub Issues**: Hata raporları ve özellik istekleri için
- **Email**: yusufygc118@gmail.com


## ⭐ Projeyi Beğendiyseniz

Bu projenin yararlı olduğunu düşünüyorsanız, lütfen ⭐ vererek destek olun!

---

**Not**: Bu uygulama eğitim amaçlıdır. İçerikleri indirirken telif hakkı yasalarına ve platform kullanım şartlarına uyun.
