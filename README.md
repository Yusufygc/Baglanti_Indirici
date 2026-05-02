# Bağlantı İndirici 📥

Modern, kullanıcı dostu ve modüler bir PyQt5 tabanlı video/ses indirici uygulaması. YouTube, TikTok, Instagram, Facebook, X (Twitter) ve daha birçok popüler platformdan içerikleri kolayca ve güvenle cihazınıza indirin.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![PyQt5](https://img.shields.io/badge/PyQt5-GUI-green?style=flat-square&logo=qt)
![yt-dlp](https://img.shields.io/badge/yt--dlp-Downloader-red?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)

## 🌟 Temel Özellikler

*   **Çoklu Platform Desteği:** YouTube, TikTok, Instagram, Facebook, X (Twitter) ve diğer birçok site.
*   **Video ve Ses İndirme:** İçerikleri yüksek kaliteli MP4 video veya MP3 ses formatında kaydetme.
*   **Akıllı Klasör Organizasyonu:** İndirilen dosyaları platform adına göre otomatik olarak alt klasörlere (örn. `Downloads/YouTube`) ayırma.
*   **Özelleştirilebilir Adlandırma:** Orijinal başlığı kullanma veya dosyaya özel bir isim belirleme.
*   **Gerçek Zamanlı Takip:** İndirme hızı, kalan süre (ETA) ve ilerleme durumunu gösteren modern durum çubuğu.
*   **Güvenli İptal:** İndirme işlemlerini istenildiği an, hatasız bir şekilde durdurabilme.
*   **Modüler Mimari:** Bakımı kolay, genişletilebilir klasör ve kod yapısı.

## 📸 Kullanıcı Arayüzü

Modern, koyu tema odaklı ve sezgisel bir arayüz deneyimi sunar:
![Baglanti Indirici Arayüzü](https://github.com/Yusufygc/Baglanti_Indirici/blob/main/icons/image.png)

## 📋 Sistem Gereksinimleri

*   **Python:** 3.8 veya üzeri
*   **İşletim Sistemi:** Windows 10/11, macOS, Linux
*   **Gerekli Araçlar:** **FFmpeg** (Video ve ses birleştirme işlemleri için zorunludur)

## 🚀 Kurulum

Projeyi yerel ortamınızda çalıştırmak için aşağıdaki adımları izleyin:

### 1. Depoyu Klonlayın
```bash
git clone https://github.com/Yusufygc/Baglanti_Indirici.git
cd Baglanti_Indirici
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

### 3. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```
*(Gerekli paketler: `PyQt5`, `yt-dlp`)*

### 4. FFmpeg Kurulumu
İndirilen video ve ses dosyalarının düzgün birleştirilebilmesi için sisteminizde FFmpeg bulunmalıdır.

**Windows:**
1. Proje ana dizininde (veya `core` klasörünün bir üstünde) `ffmpeg.exe` bulundurabilirsiniz.
2. Veya sistem `PATH` değişkeninize ekleyebilirsiniz (örn. `C:\ffmpeg\bin\ffmpeg.exe`).

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

### 5. Uygulamayı Başlatın
```bash
python main.py
```

## 💡 Kullanım Kılavuzu

1.  **Bağlantı Ekleme:** İndirmek istediğiniz videonun veya içeriğin URL'sini uygulamadaki "Bağlantı" alanına yapıştırın.
2.  **Dizin Seçimi:** Dosyanın kaydedileceği ana dizini belirleyin (Varsayılan: `Downloads`).
3.  **Dosya Adı:** Dosyanıza özel bir isim vermek isterseniz ilgili alanı doldurun. Boş bırakırsanız orijinal başlık kullanılır.
4.  **Format:** İndirmek istediğiniz türü seçin (`Video` veya `Ses`).
5.  **İndirme:** **İndir** butonuna tıklayın ve işlem durumunu ilerleme çubuğundan takip edin.

## 🗂️ Proje Yapısı

Uygulama, sürdürülebilirliği artırmak için modüler bir yapıda tasarlanmıştır:

```text
Baglanti_Indirici/
├── main.py                 # Uygulama giriş noktası
├── requirements.txt        # Bağımlılık listesi
├── core/                   # Arka plan ve iş mantığı
│   ├── config.py           # Dizin ve FFmpeg yapılandırmaları
│   ├── worker.py           # QThread tabanlı asenkron indirme yöneticisi
│   └── utils.py            # Platform ve URL çözümleme araçları
├── ui/                     # Kullanıcı arayüzü (GUI) bileşenleri
│   ├── main_window.py      # Ana pencere tasarımı
│   ├── components.py       # Özelleştirilmiş modern buton ve input'lar
│   └── styles.py           # CSS stil tanımlamaları
├── icons/                  # İkonlar ve görseller
├── build_pyinstaller.bat   # PyInstaller derleme betiği
└── build_nuitka.bat        # Nuitka derleme betiği
```

## 📦 Uygulamayı Derleme (EXE Oluşturma)

Proje, bağımsız bir çalıştırılabilir dosya (`.exe`) oluşturmak için iki farklı yöntem sunar. Derleme işlemi öncesinde sanal ortamınızın aktif ve modüllerin yüklü olduğundan emin olun.

**Yöntem 1: PyInstaller Kullanımı (Hızlı)**
Ana dizinde bulunan `build_pyinstaller.bat` dosyasına çift tıklayarak veya terminalden çalıştırarak exe oluşturabilirsiniz. Dosya `dist/` klasörü içinde oluşturulacaktır.

**Yöntem 2: Nuitka Kullanımı (Yüksek Performans)**
C tabanlı daha optimize bir derleme için `build_nuitka.bat` dosyasını kullanabilirsiniz. (Nuitka ve bir C derleyicisinin sisteminizde kurulu olması gerekir).

## 🛠️ Sorun Giderme

*   **Platform Desteklenmiyor Hatası:** İlgili sitenin URL yapısı değişmiş olabilir. Terminal üzerinden `pip install --upgrade yt-dlp` komutuyla yt-dlp'yi güncelleyin.
*   **İndirme Başarısız / Birleştirme Hatası:** `ffmpeg.exe` dosyasının projenin ana dizininde olduğundan veya sistem PATH'ine doğru eklendiğinden emin olun.
*   **İptal İşlemi Gecikmesi:** Uygulama iptal komutunu güvenli bir şekilde işler. Devam eden veri akışının kesilmesi birkaç saniye sürebilir.

## 🤝 Katkıda Bulunma

1.  Bu depoyu fork edin.
2.  Yeni bir özellik dalı oluşturun (`git checkout -b feature/yeni-ozellik`).
3.  Değişikliklerinizi commit edin (`git commit -m 'Harika bir özellik eklendi'`).
4.  Dalınızı push edin (`git push origin feature/yeni-ozellik`).
5.  Bir Pull Request (PR) açın.

## 📝 Yasal Uyarı

**Yasal Uyarı:** Bu uygulama yalnızca eğitim ve kişisel kullanım amacıyla geliştirilmiştir. İçerikleri indirirken ilgili platformların kullanım şartlarına ve telif hakkı yasalarına uymak tamamen kullanıcının sorumluluğundadır.
