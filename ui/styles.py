class StyleManager:
    """
    Uygulama genelindeki stil tanımlarını yöneten sınıf.
    SRP: Sadece stillerden sorumludur.
    """
    @staticmethod
    def get_main_stylesheet():
        return """
            /* === ANA TEMA === */
            QWidget {
                background-color: #121212;
                color: #e0e0e0;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 13px; /* 14px -> 13px */
            }
            
            /* === BAŞLIKLAR === */
            #headerTitle {
                font-size: 24px; /* 28px -> 24px */
                font-weight: bold;
                color: #00d4ff;
                margin-bottom: 5px;
            }
            
            #headerSubtitle {
                font-size: 14px;
                color: #b0b0b0;
                margin-bottom: 15px;
            }
            
            /* === KARTLAR === */
            #modernCard {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 12px;
            }
            
            #cardHeader {
                font-size: 16px;
                font-weight: bold;
                color: #ffffff;
                padding-bottom: 10px;
                border-bottom: 1px solid #333333;
                margin-bottom: 10px;
            }
            
            /* === INPUTLAR === */
            QLineEdit, QTextEdit {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 10px;
                color: #ffffff;
                font-size: 14px;
            }
            
            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #00d4ff;
                background-color: #333333;
            }
            
            QLineEdit::placeholder {
                color: #808080; 
            }
            
            #pathDisplay {
                background-color: #252525;
                color: #cccccc;
            }
            
            /* === ETİKETLER === */
            #inputLabel {
                color: #cccccc;
                font-weight: 500;
                min-width: 90px;
            }
            
            /* === BUTONLAR === */
            #primaryButton {
                background-color: #00d4ff;
                border: none;
                border-radius: 8px;
                padding: 12px;
                color: #000000;
                font-weight: bold;
                font-size: 15px;
            }
            
            #primaryButton:hover {
                background-color: #33ddff;
            }
            
            #primaryButton:pressed {
                background-color: #00b8e6;
            }
            
            #primaryButton:disabled {
                background-color: #333333;
                color: #666666;
            }
            
            #secondaryButton {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 8px 15px;
                color: #00d4ff;
            }
            
            #secondaryButton:hover {
                background-color: #333333;
                border: 1px solid #00d4ff;
            }
            
            #dangerButton {
                background-color: #2d2d2d;
                border: 1px solid #ff4757;
                border-radius: 8px;
                padding: 12px;
                color: #ff4757;
                font-weight: bold;
            }
            
            #dangerButton:hover {
                background-color: rgba(255, 71, 87, 0.1);
            }
            
            #dangerButton:disabled {
                background-color: #333333;
                color: #666666;
                border-color: #444;
            }
            
            /* === RADIO BUTON === */
            QRadioButton {
                color: #e0e0e0;
                spacing: 8px;
            }
            
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #555555;
                background: transparent;
            }
            
            QRadioButton::indicator:checked {
                border-color: #00d4ff;
                background-color: #00d4ff;
                image: none;
            }
            
            /* === PROGRESS BAR === */
            QProgressBar {
                background-color: #2d2d2d;
                border: none;
                border-radius: 6px;
                height: 20px;
                text-align: center;
                color: white;
            }
            
            QProgressBar::chunk {
                background-color: #00d4ff;
                border-radius: 6px;
            }

            /* === SCROLLBAR === */
            QScrollBar:vertical {
                background: #1e1e1e;
                width: 10px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #444;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #555;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }

            /* === STATUS BAR & FOOTER === */
            #statusBar {
                background-color: #1e1e1e;
                border-top: 1px solid #333;
            }
            
            #footerText {
                color: #666;
                font-size: 11px;
            }
            
            #statusLabel {
                font-size: 13px;
                font-weight: bold;
                color: #00d4ff;
            }
            
            #detailLabel {
                color: #888;
                font-size: 12px;
                margin-top: 5px;
            }
        """

    @staticmethod
    def get_log_span(color_code, message):
        """Yardımcı metod: Log mesajları için HTML span döndürür."""
        colors = {
            'info': '#a0a0b8',
            'success': '#00ff9d',
            'warning': '#ffa502',
            'error': '#ff4757',
            'highlight': '#00d4ff'
        }
        color = colors.get(color_code, '#e0e0e0')
        return f"<span style='color:{color};'>{message}</span>"
