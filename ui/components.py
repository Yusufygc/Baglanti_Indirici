from PyQt5.QtWidgets import QFrame, QGraphicsDropShadowEffect, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

class ModernCard(QFrame):
    """
    Standart kart bileşeni.
    Hafif gölge efekti ve stil sınıfı ile gelir.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("modernCard")
        
        # Gölge efekti (Performans için gerekirse devre dışı bırakılabilir)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

class HeaderLabel(QLabel):
    def __init__(self, text, subtitle=False):
        super().__init__(text)
        self.setAlignment(Qt.AlignCenter)
        if subtitle:
            self.setObjectName("headerSubtitle")
        else:
            self.setObjectName("headerTitle")

class ModernButton(QPushButton):
    def __init__(self, text, btn_type="primary", handler=None):
        super().__init__(text)
        self.setCursor(Qt.PointingHandCursor)
        
        if btn_type == "primary":
            self.setObjectName("primaryButton")
            self.setFixedHeight(50)
        elif btn_type == "danger":
            self.setObjectName("dangerButton")
            self.setFixedHeight(50)
        elif btn_type == "secondary":
            self.setObjectName("secondaryButton")
            
        if handler:
            self.clicked.connect(handler)

class ModernInput(QLineEdit):
    def __init__(self, placeholder="", read_only=False):
        super().__init__()
        self.setPlaceholderText(placeholder)
        if read_only:
            self.setReadOnly(True)
            self.setObjectName("pathDisplay")
        else:
            self.setObjectName("inputLabel") # CSS'te düzeltilmesi gerekebilir veya genel QLineEdit kullanılır
