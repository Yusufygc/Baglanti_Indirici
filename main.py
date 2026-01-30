import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    """
    Uygulama giriş noktası.
    """
    app = QApplication(sys.argv)
    
    # Ana pencereyi oluştur ve göster
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()