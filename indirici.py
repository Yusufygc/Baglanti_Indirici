import subprocess
import os
import re
from tkinter import messagebox

class Indirici:
    """
    İndirme işlemlerini yürüten ve yöneten sınıf.
    """
    def __init__(self):
        try:
            subprocess.run(["yt-dlp", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            messagebox.showerror("Hata", "yt-dlp bulunamadı. Lütfen kurduğunuzdan veya PATH'e eklediğinizden emin olun.")
            raise FileNotFoundError("yt-dlp bulunamadı.")
    
    def indir(self, url, kayit_dizini, progress_callback, indirme_tipi="video"):
        """
        URL'den içerik indirir ve belirtilen dizine kaydeder.
        indirme_tipi: 'video' veya 'ses' olabilir.
        """
        try:
            klasor_adi = ""
            if "youtube.com" in url or "youtu.be" in url or "youtube.com/shorts" in url:
                klasor_adi = "YouTube"
            elif "instagram.com" in url:
                klasor_adi = "Instagram"
            elif "twitter.com" in url or "x.com" in url:
                klasor_adi = "Twitter"
            elif "tiktok.com" in url:
                klasor_adi = "TikTok"
            else:
                # Diğer platformlar için genel bir klasör oluştur
                klasor_adi = "İndirilenler"

            # Kullanıcının seçtiği dizin adı, oluşturulacak klasörle aynıysa yeni bir alt klasör oluşturma
            if os.path.basename(kayit_dizini).lower() == klasor_adi.lower():
                hedef_dizin = kayit_dizini
            else:
                hedef_dizin = os.path.join(kayit_dizini, klasor_adi)

            os.makedirs(hedef_dizin, exist_ok=True)
            
            # yt-dlp komutunu indirme tipine göre oluştur
            komut = ["yt-dlp"]
            
            # Güvenlik ve kalite ayarları
            komut.extend(["--no-check-certificate"])  # SSL sorunları için
            
            if indirme_tipi == "ses":
                komut.extend([
                    "--extract-audio", 
                    "--audio-format", "mp3",
                    "--audio-quality", "192K"  # Ses kalitesi
                ])
                # Ses dosyaları için dosya adı formatı
                komut.extend(["-o", os.path.join(hedef_dizin, "%(title)s.%(ext)s")])
            else:
                # Video için format seçimi (en iyi kalite)
                komut.extend(["-f", "best[height<=1080]"])  # 1080p'ye kadar
                komut.extend(["-o", os.path.join(hedef_dizin, "%(title)s.%(ext)s")])
            
            # Güvenli dosya adları için
            komut.extend(["--restrict-filenames"])
            
            komut.append(url)

            proc = subprocess.Popen(
                komut, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                universal_newlines=True,
                encoding='utf-8',
                errors='replace'
            )
            
            # Progress tracking
            progress_value = 0
            
            for line in proc.stdout:
                # Progress pattern'ini yakala
                progress_match = re.search(r"\[download\]\s+(\d+\.?\d*)%", line)
                if progress_match:
                    progress_value = float(progress_match.group(1))
                    progress_callback(progress_value)
                
                # Merge pattern'ini de yakala (video + audio birleştirme)
                elif "[ffmpeg]" in line and "Merging" in line:
                    progress_callback(95)  # Birleştirme sırasında %95 göster
            
            proc.wait()
            
            if proc.returncode != 0:
                raise subprocess.CalledProcessError(proc.returncode, komut)
            
            # Son progress güncellemesi
            progress_callback(100)
            return "İndirme başarıyla tamamlandı!", True
            
        except subprocess.CalledProcessError as e:
            error_msg = f"İndirme sırasında bir hata oluştu (Kod: {e.returncode})"
            
            # Yaygın hata durumları için özel mesajlar
            if e.returncode == 1:
                error_msg += "\nURL geçerli değil veya video bulunamadı."
            elif e.returncode == 2:
                error_msg += "\nYt-dlp parametrelerinde hata var."
            else:
                error_msg += f"\nDetay: {e}"
                
            return error_msg, False
            
        except PermissionError:
            return "Dosya kaydetme izni yok. Lütfen farklı bir dizin seçin.", False
            
        except OSError as e:
            return f"Dosya sistemi hatası: {e}", False
            
        except Exception as e:
            return f"Beklenmedik bir hata oluştu: {e}", False