import tkinter as tk
from tkinter import filedialog, ttk
from indirici import Indirici
import threading

class Arayuz(tk.Tk):
    """
    Masaüstü uygulamasının arayüzünü oluşturan sınıf.
    """
    def __init__(self):
        super().__init__()
        self.title("Bağlantı İndirici")
        self.geometry("600x300")
        
        try:
            self.indirici = Indirici()
        except FileNotFoundError:
            self.destroy()
            return

        self._arayuz_olustur()
    
    def _arayuz_olustur(self):
        ana_frame = tk.Frame(self, padx=20, pady=20)
        ana_frame.pack(fill=tk.BOTH, expand=True)

        url_etiket = tk.Label(ana_frame, text="Lütfen indirmek istediğiniz URL'yi girin:")
        url_etiket.pack(pady=(0, 5), anchor="w")

        self.url_giris = tk.Entry(ana_frame, width=80)
        self.url_giris.pack(fill=tk.X, pady=(0, 10))
        self.url_giris.bind("<KeyRelease>", self.url_kontrol)

        self.indirme_tipi = tk.StringVar(value="video")
        self.tip_frame = tk.Frame(ana_frame)
        self.tip_frame.pack(fill=tk.X, pady=(0,10))
        
        tk.Label(self.tip_frame, text="İndirme Tipi:").pack(side=tk.LEFT)
        self.video_radio = tk.Radiobutton(self.tip_frame, text="Video", variable=self.indirme_tipi, value="video")
        self.video_radio.pack(side=tk.LEFT, padx=10)
        self.ses_radio = tk.Radiobutton(self.tip_frame, text="Ses (MP3)", variable=self.indirme_tipi, value="ses")
        self.ses_radio.pack(side=tk.LEFT)
        self.tip_frame.pack_forget()
        
        dizin_frame = tk.Frame(ana_frame)
        dizin_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.dizin_etiket = tk.Label(dizin_frame, text="Kaydedilecek dizin: Seçilmedi")
        self.dizin_etiket.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        dizin_buton = tk.Button(dizin_frame, text="Dizin Seç", command=self.dizin_sec)
        dizin_buton.pack(side=tk.RIGHT)
        
        self.kayit_dizini = ""

        indir_buton = tk.Button(ana_frame, text="İndir", command=self.baslat_thread)
        indir_buton.pack(fill=tk.X, pady=(10, 0))

        self.progress_bar = ttk.Progressbar(ana_frame, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=(10, 0))
        
        durum_frame = tk.Frame(ana_frame)
        durum_frame.pack(pady=(10, 0), fill=tk.X)
        self.durum_etiket = tk.Label(durum_frame, text="", fg="blue", justify="left")
        self.durum_etiket.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def url_kontrol(self, event=None):
        url = self.url_giris.get()
        if "youtube.com" in url or "youtu.be" in url:
            self.tip_frame.pack(fill=tk.X, pady=(0,10))
        else:
            self.tip_frame.pack_forget()
            
    def dizin_sec(self):
        self.kayit_dizini = filedialog.askdirectory()
        if self.kayit_dizini:
            self.dizin_etiket.config(text=f"Kaydedilecek dizin: {self.kayit_dizini}")
            
    def baslat_thread(self):
        url = self.url_giris.get()
        if not url:
            self.durum_etiket.config(text="Lütfen bir URL girin!", fg="red")
            return
        
        if not self.kayit_dizini:
            self.durum_etiket.config(text="Lütfen bir dizin seçin!", fg="red")
            return

        self.durum_etiket.config(text="İndirme başlatılıyor...", fg="orange")
        self.progress_bar["value"] = 0
        self.update_idletasks()
        
        indirme_tipi = self.indirme_tipi.get()

        self.thread = threading.Thread(target=self.indir_islemi, args=(url, self.kayit_dizini, indirme_tipi))
        self.thread.start()

    def progress_guncelle(self, value):
        self.progress_bar["value"] = value
        self.durum_etiket.config(text=f"İndiriliyor: %{value:.2f}")
        self.update_idletasks()

    def indir_islemi(self, url, kayit_dizini, indirme_tipi):
        sonuc, basari = self.indirici.indir(url, kayit_dizini, self.progress_guncelle, indirme_tipi)
        
        if basari:
            self.durum_etiket.config(text=sonuc, fg="green")
            self.progress_bar["value"] = 100
            self.url_giris.delete(0, 'end') # URL kutusunu temizle
            self.url_kontrol() # İndirme seçeneklerini gizle
        else:
            self.durum_etiket.config(text=sonuc, fg="red")
            self.progress_bar["value"] = 0
        self.update_idletasks()