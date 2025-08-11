# ttk'dan widget'ları import etmek yerine ttkbootstrap'tan import edin
import tkinter as tk
from tkinter import filedialog
from indirici import Indirici
import threading

# ttkbootstrap kütüphanesini içeri aktarın
import ttkbootstrap as ttk
from ttkbootstrap.constants import * # ALL, SUCCESS, INFO, DANGER gibi sabitleri içe aktarır

class Arayuz(ttk.Window): # tk.Tk yerine ttk.Window kullanın
    def __init__(self):
        super().__init__(themename="superhero") # 'superhero' temasıyla başlatıyoruz. Başka temalar da seçebilirsiniz.
        self.title("Bağlantı İndirici")
        self.geometry("600x300")
        
        try:
            self.indirici = Indirici()
        except FileNotFoundError:
            self.destroy()
            return

        self._arayuz_olustur()
    
    def _arayuz_olustur(self):
        # Arayüz elemanlarını ttk.Frame, ttk.Button vb. olarak değiştirin.
        ana_frame = ttk.Frame(self, padding=20)
        ana_frame.pack(fill=tk.BOTH, expand=True)

        # Label yerine ttk.Label kullanın
        url_etiket = ttk.Label(ana_frame, text="Lütfen indirmek istediğiniz URL'yi girin:")
        url_etiket.pack(pady=(0, 5), anchor="w")

        # Entry yerine ttk.Entry kullanın
        self.url_giris = ttk.Entry(ana_frame, width=80)
        self.url_giris.pack(fill=tk.X, pady=(0, 10))
        self.url_giris.bind("<KeyRelease>", self.url_kontrol)

        self.indirme_tipi = tk.StringVar(value="video")
        self.tip_frame = ttk.Frame(ana_frame)
        self.tip_frame.pack(fill=tk.X, pady=(0,10))
        
        ttk.Label(self.tip_frame, text="İndirme Tipi:").pack(side=tk.LEFT)
        # Radiobutton yerine ttk.Radiobutton kullanın
        self.video_radio = ttk.Radiobutton(self.tip_frame, text="Video", variable=self.indirme_tipi, value="video")
        self.video_radio.pack(side=tk.LEFT, padx=10)
        self.ses_radio = ttk.Radiobutton(self.tip_frame, text="Ses (MP3)", variable=self.indirme_tipi, value="ses")
        self.ses_radio.pack(side=tk.LEFT)
        self.tip_frame.pack_forget()
        
        dizin_frame = ttk.Frame(ana_frame)
        dizin_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.dizin_etiket = ttk.Label(dizin_frame, text="Kaydedilecek dizin: Seçilmedi")
        self.dizin_etiket.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Button yerine ttk.Button kullanın
        dizin_buton = ttk.Button(dizin_frame, text="Dizin Seç", command=self.dizin_sec, bootstyle="info") # bootstyle ile renk verebilirsiniz
        dizin_buton.pack(side=tk.RIGHT)
        
        self.kayit_dizini = ""

        # Button yerine ttk.Button kullanın
        indir_buton = ttk.Button(ana_frame, text="İndir", command=self.baslat_thread, bootstyle="success")
        indir_buton.pack(fill=tk.X, pady=(10, 0))

        # Progressbar için ttk.Progressbar zaten kullanıyorduk
        self.progress_bar = ttk.Progressbar(ana_frame, orient="horizontal", length=400, mode="determinate", bootstyle="success")
        self.progress_bar.pack(fill=tk.X, pady=(10, 0))
        
        durum_frame = ttk.Frame(ana_frame)
        durum_frame.pack(pady=(10, 0), fill=tk.X)
        self.durum_etiket = ttk.Label(durum_frame, text="", justify="left", bootstyle="info") # Renkler de bootstyle ile ayarlanabilir
        self.durum_etiket.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def url_kontrol(self, event=None):
        """URL giriş alanındaki değişiklikleri kontrol eder"""
        url = self.url_giris.get().strip()
        
        # URL'ye göre indirme tipini göster/gizle
        if url and ('youtube.com' in url or 'youtu.be' in url):
            self.tip_frame.pack(fill=tk.X, pady=(0,10), before=self.tip_frame.master.children['!frame2'])
        else:
            self.tip_frame.pack_forget()
    
    def dizin_sec(self):
        self.kayit_dizini = filedialog.askdirectory()
        if self.kayit_dizini:
            self.dizin_etiket.config(text=f"Kaydedilecek dizin: {self.kayit_dizini}")
            
    def baslat_thread(self):
        # ... (bu metodda değişiklik yok)
        # Sadece hata mesajı renklerini bootstyle ile uyumlu hale getirebiliriz
        url = self.url_giris.get()
        if not url:
            self.durum_etiket.config(text="Lütfen bir URL girin!", bootstyle="danger")
            return
        
        if not self.kayit_dizini:
            self.durum_etiket.config(text="Lütfen bir dizin seçin!", bootstyle="danger")
            return

        self.durum_etiket.config(text="İndirme başlatılıyor...", bootstyle="warning")
        self.progress_bar["value"] = 0
        self.update_idletasks()
        
        indirme_tipi = self.indirme_tipi.get()

        self.thread = threading.Thread(target=self.indir_islemi, args=(url, self.kayit_dizini, indirme_tipi))
        self.thread.start()

    def progress_guncelle(self, value):
        self.progress_bar["value"] = value
        self.durum_etiket.config(text=f"İndiriliyor: %{value:.2f}", bootstyle="info")
        self.update_idletasks()

    def indir_islemi(self, url, kayit_dizini, indirme_tipi):
        sonuc, basari = self.indirici.indir(url, kayit_dizini, self.progress_guncelle, indirme_tipi)
        
        if basari:
            self.durum_etiket.config(text=sonuc, bootstyle="success")
            self.progress_bar["value"] = 100
            self.url_giris.delete(0, 'end')
            self.url_kontrol()
        else:
            self.durum_etiket.config(text=sonuc, bootstyle="danger")
            self.progress_bar["value"] = 0
        self.update_idletasks()