class StyleManager:
    @staticmethod
    def get_main_stylesheet():
        return """
            /* ========== GLOBAL ========== */
            QWidget {
                background-color: #0F1117;
                color: #F4F7FB;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 13px;
            }

            /* ========== BAŞLIK ========== */
            #headerTitle {
                font-size: 23px;
                font-weight: 700;
                color: #F4F7FB;
                letter-spacing: 0;
            }

            #headerSubtitle {
                font-size: 13px;
                color: #9AA8BD;
                margin-bottom: 6px;
            }

            /* ========== KART ========== */
            #modernCard {
                background-color: #171B23;
                border: 1px solid #2B3240;
                border-radius: 8px;
            }

            /* ========== FORM LABEL (input üstündeki etiket) ========== */
            #formLabel {
                font-size: 11px;
                font-weight: 700;
                color: #9AA8BD;
                letter-spacing: 0.8px;
                background: transparent;
            }

            /* ========== YARDIMCI METİN ========== */
            #helperText {
                font-size: 11px;
                color: #69758A;
                margin-top: 2px;
            }

            #errorText {
                font-size: 11px;
                color: #FF4D6D;
                margin-top: 2px;
            }

            /* ========== INPUT ========== */
            QLineEdit {
                background-color: #1D222C;
                border: 1px solid #2B3240;
                border-radius: 6px;
                padding: 10px 12px;
                color: #F4F7FB;
                font-size: 13px;
                selection-background-color: #12C8E8;
                selection-color: #0F1117;
            }

            QLineEdit:focus {
                border: 1.5px solid #12C8E8;
                background-color: #202632;
            }

            QLineEdit:disabled {
                color: #69758A;
                background-color: #171B23;
                border-color: #252B35;
            }

            #pathDisplay {
                background-color: #171B23;
                color: #9AA8BD;
                border-color: #252B35;
            }

            /* ========== BUTONLAR ========== */
            #primaryButton {
                background-color: #12C8E8;
                border: none;
                border-radius: 8px;
                padding: 12px 32px;
                color: #081018;
                font-weight: 700;
                font-size: 14px;
                min-width: 110px;
            }

            #primaryButton:hover {
                background-color: #45D6EF;
            }

            #primaryButton:pressed {
                background-color: #0FB3D0;
            }

            #primaryButton:disabled {
                background-color: #1D222C;
                color: #69758A;
                border: 1px solid #2B3240;
            }

            #secondaryButton {
                background-color: #1D222C;
                border: 1px solid #2B3240;
                border-radius: 6px;
                padding: 8px 14px;
                color: #C3CDDB;
                font-size: 13px;
            }

            #secondaryButton:hover {
                background-color: #252B35;
                border-color: #3A4454;
                color: #F4F7FB;
            }

            #dangerButton {
                background-color: #1D222C;
                border: 1.5px solid #FF4D6D;
                border-radius: 8px;
                padding: 12px 28px;
                color: #FF4D6D;
                font-weight: 700;
                font-size: 14px;
                min-width: 100px;
            }

            #dangerButton:hover {
                background-color: rgba(255, 77, 109, 0.10);
            }

            #dangerButton:disabled {
                background-color: #171B23;
                color: #69758A;
                border-color: #2B3240;
            }

            /* ========== SEGMENT KONTROL ========== */
            #segmentControl {
                background-color: #1D222C;
                border: 1px solid #2B3240;
                border-radius: 8px;
            }

            #segmentControl QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 6px;
                padding: 8px 18px;
                color: #9AA8BD;
                font-size: 13px;
                font-weight: 500;
                min-width: 80px;
            }

            #segmentControl QPushButton:hover {
                color: #F4F7FB;
                background-color: #252B35;
            }

            #segmentControl QPushButton[active="true"] {
                background-color: #12C8E8;
                color: #081018;
                font-weight: 700;
            }

            /* ========== CHECKBOX ========== */
            QCheckBox {
                color: #9AA8BD;
                spacing: 8px;
            }

            QCheckBox::indicator {
                width: 17px;
                height: 17px;
                border-radius: 4px;
                border: 1.5px solid #3A4454;
                background: #1D222C;
            }

            QCheckBox::indicator:hover {
                border-color: #12C8E8;
            }

            QCheckBox::indicator:checked {
                background-color: #12C8E8;
                border-color: #12C8E8;
            }

            /* ========== PROGRESS BAR ========== */
            QProgressBar {
                background-color: #252B35;
                border: none;
                border-radius: 4px;
                height: 6px;
            }

            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0FB3D0, stop:1 #12C8E8);
                border-radius: 4px;
            }

            /* ========== SCROLLBAR ========== */
            QScrollBar:vertical {
                background: #0F1117;
                width: 8px;
                margin: 0;
            }

            QScrollBar::handle:vertical {
                background: #2B3240;
                border-radius: 4px;
                min-height: 24px;
            }

            QScrollBar::handle:vertical:hover {
                background: #3A4454;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            /* ========== STATUS BAR ========== */
            #statusBar {
                background-color: #0C0E13;
                border-top: 1px solid #171B23;
                min-height: 32px;
            }

            #statusBarText {
                font-size: 12px;
                font-weight: 600;
                color: #9AA8BD;
            }

            #footerText {
                color: #69758A;
                font-size: 11px;
            }

            #detailLabel {
                color: #9AA8BD;
                font-size: 12px;
            }

            /* ========== LINK BUTON (Klasörde Göster) ========== */
            #linkButton {
                background: transparent;
                border: none;
                color: #12C8E8;
                font-size: 12px;
                font-weight: 600;
                padding: 4px 8px;
                text-decoration: underline;
            }

            #linkButton:hover {
                color: #45D6EF;
            }
        """

    @staticmethod
    def get_log_span(color_code, message):
        colors = {
            'info':      '#8B91A7',
            'success':   '#2ECC71',
            'warning':   '#F39C12',
            'error':     '#FF4757',
            'highlight': '#00d4ff',
        }
        color = colors.get(color_code, '#F0F2F5')
        return f"<span style='color:{color};'>{message}</span>"
