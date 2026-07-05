import os
import sys

def get_base_path():
    """
    Uygulamanın çalıştığı temel dizini döndürür.
    PyInstaller ile derlendiğinde çalıştırılabilir dizini doğru bulur.
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller ile derlenmiş
        return os.path.dirname(sys.executable)
    else:
        # Normal python çalışması
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_user_data_dir():
    """
    Kullanici-yazilabilir uygulama veri dizini (~/.baglanti_indirici).

    Kurulu exe Program Files altinda olabilir ve orasi yazilamaz (WinError 5);
    bu yuzden loglar, ayarlar, gecmis ve Instagram oturum verileri burada tutulur.
    core/settings.py, core/history/repository.py ve core/instagram/session.py
    ayni koku kullanir.
    """
    path = os.path.join(os.path.expanduser("~"), ".baglanti_indirici")
    os.makedirs(path, exist_ok=True)
    return path


def get_ffmpeg_path():
    """
    ffmpeg.exe dosyasının yolunu bulur.
    Sırasıyla şuralara bakar:
    1. Çalıştırılabilir dosyanın yanındaki ffmpeg.exe
    2. core klasörünün bir üstündeki (root) ffmpeg.exe
    3. Sistem PATH'indeki ffmpeg
    """
    base_path = get_base_path()
    
    # 0. PyInstaller Bundle (_MEIPASS) kontrolü
    if hasattr(sys, '_MEIPASS'):
        bundled_path = os.path.join(sys._MEIPASS, 'ffmpeg.exe')
        if os.path.exists(bundled_path):
            return bundled_path

    # 1. Base path kontrolü (exe yanı veya proje root)
    possible_path = os.path.join(base_path, 'ffmpeg.exe')
    if os.path.exists(possible_path):
        return possible_path
        
    # 2. Geliştirme ortamı için (eğer core altındaysak bir üste bak)
    dev_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ffmpeg.exe')
    if os.path.exists(dev_path):
        return dev_path

    # 3. Fallback: Sistem path'i veya varsayılan kurulum
    if os.path.exists(r'C:\ffmpeg\bin\ffmpeg.exe'):
        return r'C:\ffmpeg\bin\ffmpeg.exe'
        
    # 4. Sadece komut ismi döndür (sistem path'inde varsa çalışır)
    return 'ffmpeg'

def get_yt_dlp_update_dir():
    """
    yt-dlp oto-guncellemesinin YAZACAGI klasor: kullanici-yazilabilir
    ~/.baglanti_indirici/lib.

    Exe Program Files'a kurulunca exe-yani lib/ yazilamaz (WinError 5); bu yuzden
    guncellenen yt_dlp kopyasi kullanici veri dizinine yazilir. Bu klasordeki
    yt_dlp, exe-yanindaki (salt-okunur, gomulu) kopyaya gore ONCELIKLI okunur
    (bkz. get_yt_dlp_lib_dir).
    """
    path = os.path.join(get_user_data_dir(), 'lib')
    os.makedirs(path, exist_ok=True)
    return path


def get_yt_dlp_lib_dir():
    """
    Harici yt_dlp paketini barindiran 'lib' klasorunun yolunu dondurur (yt_dlp/
    paketinin PARENT dizini, sys.path'e eklenecek olan). Oncelik sirasi:
    1. Kullanici veri dizini ~/.baglanti_indirici/lib/yt_dlp (oto-guncelleme yazar;
       varsa en guncel surumdur) -> get_yt_dlp_update_dir.
    2. Exe yanindaki lib/yt_dlp (frozen: gomulu, salt-okunur yedek).
    3. Proje kokundeki lib/yt_dlp (gelistirme ortaminda opsiyonel).
    4. None -> harici kopya yok; normal 'import yt_dlp' cozumlemesi (pip/site-packages)
       oldugu gibi calissin.
    """
    user_lib = os.path.join(get_user_data_dir(), 'lib')
    if os.path.exists(os.path.join(user_lib, 'yt_dlp', '__init__.py')):
        return user_lib

    base_path = get_base_path()
    candidate = os.path.join(base_path, 'lib')
    if os.path.exists(os.path.join(candidate, 'yt_dlp', '__init__.py')):
        return candidate

    dev_candidate = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lib'
    )
    if os.path.exists(os.path.join(dev_candidate, 'yt_dlp', '__init__.py')):
        return dev_candidate

    return None
