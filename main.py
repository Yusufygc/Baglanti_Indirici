import sys


def _register_external_yt_dlp():
    """
    yt_dlp'yi exe icine gomulu olmaktan cikarip harici, guncellenebilir
    lib/yt_dlp klasorunden yuklemek icin sys.path'i ayarlar.
    Diger TUM proje importlarindan ONCE calismalidir.
    """
    from core.config import get_yt_dlp_lib_dir
    lib_dir = get_yt_dlp_lib_dir()
    if lib_dir and lib_dir not in sys.path:
        sys.path.insert(0, lib_dir)


_register_external_yt_dlp()

from core.logger import enable_native_crash_dump, get_logger, install_excepthook

install_excepthook()
enable_native_crash_dump()

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from ui.assets.font_manager import FontManager
from ui.window.main_window import MainWindow

def main():
    """
    Uygulama giriş noktası.
    """
    logger = get_logger("app")
    logger.info("Uygulama basladi")

    # QtWebEngine (Instagram giris penceresi) icin: QApplication olusturulmadan
    # ONCE ayarlanmali, yoksa gomulu tarayici acilirken cokebilir.
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    FontManager.load_fonts()
    app.setFont(FontManager.application_font())

    # Ana pencereyi oluştur ve göster
    window = MainWindow()
    window.show()

    exit_code = app.exec_()
    logger.info("Uygulama kapandi (exit_code=%s)", exit_code)
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
