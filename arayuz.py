import tkinter as tk
from tkinter import filedialog
from indirici import Indirici # indirici.py dosyasındaki sınıfı içe aktar

class Arayuz(tk.Tk):
    """
    Masaüstü uygulamasının arayüzünü oluşturan sınıf.
    """
    def __init__(self):
        super().__init__()
        self.title("Bağlantı İndirici")
        self.geometry("600x250")
        
        try:
            self.indirici = Indirici()
        except FileNotFoundError:
            self.destroy() # Eğer yt-dlp bulunamazsa pencereyi kapat
            return

        self._arayuz_olustur()
    
    def _arayuz_olustur(self):
        ana_frame = tk.Frame(self, padx=20, pady=20)
        ana_frame.pack(fill=tk.BOTH, expand=True)

        url_etiket = tk.Label(ana_frame, text="Lütfen indirmek istediğiniz URL'yi girin:")
        url_etiket.pack(pady=(0, 5), anchor="w")

        self.url_giris = tk.Entry(ana_frame, width=80)
        self.url_giris.pack(fill=tk.X, pady=(0, 10))

        dizin_frame = tk.Frame(ana_frame)
        dizin_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.dizin_etiket = tk.Label(dizin_frame, text="Kaydedilecek dizin: Seçilmedi")
        self.dizin_etiket.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        dizin_buton = tk.Button(dizin_frame, text="Dizin Seç", command=self.dizin_sec)
        dizin_buton.pack(side=tk.RIGHT)
        
        self.kayit_dizini = ""

        indir_buton = tk.Button(ana_frame, text="İndir", command=self.baslat_indirici)
        indir_buton.pack(fill=tk.X, pady=(10, 0))

        self.durum_etiket = tk.Label(ana_frame, text="", fg="blue")
        self.durum_etiket.pack(pady=(10, 0))

    def dizin_sec(self):
        self.kayit_dizini = filedialog.askdirectory()
        if self.kayit_dizini:
            self.dizin_etiket.config(text=f"Kaydedilecek dizin: {self.kayit_dizini}")
            
    def baslat_indirici(self):
        url = self.url_giris.get()
        if not url:
            self.durum_etiket.config(text="Lütfen bir URL girin!", fg="red")
            return
        
        if not self.kayit_dizini:
            self.durum_etiket.config(text="Lütfen bir dizin seçin!", fg="red")
            return

        self.durum_etiket.config(text="İndirme başlatılıyor...", fg="orange")
        self.update_idletasks()
        
        sonuc, basari = self.indirici.indir(url, self.kayit_dizini)
        
        if basari:
            self.durum_etiket.config(text=sonuc, fg="green")
        else:
            self.durum_etiket.config(text=sonuc, fg="red")