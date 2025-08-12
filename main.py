# main.py
import sys
from PyQt5.QtWidgets import QApplication
from arayuz import UygulamaArayuzu

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pencere = UygulamaArayuzu()
    pencere.show()
    sys.exit(app.exec_())