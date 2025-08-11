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
    
    def indir(self, url, kayit_dizini, progress_callback):
        """
        URL'den içerik indirir ve belirtilen dizine kaydeder.
        progress_callback: İlerleme bilgisini geri döndüren fonksiyon.
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
            
            komut = ["yt-dlp", "-o", os.path.join(hedef_dizin, "%(title)s.%(ext)s"), url]

            # subprocess.Popen ile komut çıktısını anlık yakala
            proc = subprocess.Popen(komut, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            
            # İlerleme çubuğunu güncellemek için çıktıyı oku
            for line in proc.stdout:
                progress_match = re.search(r"\[download\]\s+(\d+\.?\d*)%", line)
                if progress_match:
                    progress_value = float(progress_match.group(1))
                    progress_callback(progress_value)
            
            proc.wait() # İşlemin bitmesini bekle
            
            if proc.returncode != 0:
                raise subprocess.CalledProcessError(proc.returncode, komut)
            
            return "İndirme tamamlandı!", True
            
        except subprocess.CalledProcessError as e:
            return f"İndirme sırasında bir hata oluştu: {e}", False
        except Exception as e:
            return f"Beklenmedik bir hata oluştu: {e}", False