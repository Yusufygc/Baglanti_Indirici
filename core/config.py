import os
import sys

def get_base_path():
    """
    Uygulamanın çalıştığı temel dizini döndürür.
    Nuitka veya PyInstaller ile derlendiğinde geçici veya çalıştırılabilir dizini doğru bulur.
    """
    if getattr(sys, 'frozen', False):
        # Nuitka veya PyInstaller ile derlenmiş
        return os.path.dirname(sys.executable)
    else:
        # Normal python çalışması
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_ffmpeg_path():
    """
    ffmpeg.exe dosyasının yolunu bulur.
    Sırasıyla şuralara bakar:
    1. Çalıştırılabilir dosyanın yanındaki ffmpeg.exe
    2. core klasörünün bir üstündeki (root) ffmpeg.exe
    3. Sistem PATH'indeki ffmpeg
    """
    base_path = get_base_path()
    
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
