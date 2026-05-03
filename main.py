import sys
from PyQt5.QtWidgets import QApplication
from ui.assets.font_manager import FontManager
from ui.window.main_window import MainWindow

def main():
    """
    Uygulama giriş noktası.
    """
    app = QApplication(sys.argv)
    FontManager.load_fonts()
    app.setFont(FontManager.application_font())
    
    # Ana pencereyi oluştur ve göster
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
