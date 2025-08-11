import subprocess
import os
from tkinter import messagebox

class Indirici:
    """
    İndirme işlemlerini yürüten ve yöneten sınıf.
    """
    def __init__(self):
        # yt-dlp'nin varlığını kontrol etmek için basit bir test.
        try:
            subprocess.run(["yt-dlp", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            messagebox.showerror("Hata", "yt-dlp bulunamadı. Lütfen kurduğunuzdan veya PATH'e eklediğinizden emin olun.")
            raise FileNotFoundError("yt-dlp bulunamadı.")
    
    def indir(self, url, kayit_dizini):
        """
        URL'den içerik indirir ve belirtilen dizine kaydeder.
        """
        try:
            if "youtube.com" in url or "youtu.be" in url or "youtube.com/shorts" in url:
                klasor_adi = "YouTube"
            elif "instagram.com" in url:
                klasor_adi = "Instagram"
            else:
                return "Geçersiz URL. Lütfen bir YouTube veya Instagram adresi girin.", False

            hedef_dizin = os.path.join(kayit_dizini, klasor_adi)
            os.makedirs(hedef_dizin, exist_ok=True)
            
            # -o parametresi dosya kaydetme yolunu ve adlandırma formatını belirtir
            komut = ["yt-dlp", "-o", os.path.join(hedef_dizin, "%(title)s.%(ext)s"), url]
            
            subprocess.run(komut, check=True)
            
            return "İndirme tamamlandı!", True
            
        except subprocess.CalledProcessError as e:
            return f"İndirme sırasında bir hata oluştu: {e}", False
        except Exception as e:
            return f"Beklenmedik bir hata oluştu: {e}", False