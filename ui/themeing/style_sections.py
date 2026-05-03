from ui.assets.font_manager import FontManager
from .theme import FONT_SIZES as fs
from .theme import THEME as t


def global_styles():
    return f"""
        QWidget {{
            background-color: {t["background"]};
            color: {t["text"]};
            font-family: {FontManager.font_stack()};
            font-size: {fs["body"]}px;
        }}
    """


def text_styles():
    return f"""
        #headerTitle {{
            font-size: {fs["title"]}px;
            font-weight: 700;
            color: {t["text"]};
            letter-spacing: 0;
        }}

        #headerSubtitle {{
            font-size: {fs["subtitle"]}px;
            color: {t["text_secondary"]};
            margin-bottom: 6px;
        }}

        #formLabel {{
            font-size: {fs["label"]}px;
            font-weight: 700;
            color: {t["text_secondary"]};
            letter-spacing: 0.8px;
            background: transparent;
        }}

        #helperText {{
            font-size: {fs["helper"]}px;
            color: {t["text_soft"]};
            margin-top: 2px;
        }}

        #errorText {{
            font-size: {fs["helper"]}px;
            color: {t["danger"]};
            margin-top: 2px;
        }}
    """


def container_styles():
    return f"""
        #modernCard {{
            background-color: {t["surface"]};
            border: 1px solid {t["border"]};
            border-radius: 8px;
        }}

        #statusBar {{
            background-color: {t["background_dark"]};
            border-top: 1px solid {t["surface"]};
            min-height: 32px;
        }}

        #statusBarText {{
            font-size: {fs["status"]}px;
            font-weight: 600;
            color: {t["text_secondary"]};
        }}

        #footerText {{
            color: {t["text_secondary"]};
            font-family: {FontManager.mono_stack()};
            font-size: {fs["footer"]}px;
        }}

        #detailLabel {{
            color: {t["text_secondary"]};
            font-size: {fs["status"]}px;
        }}
    """


def input_styles():
    return f"""
        QLineEdit {{
            background-color: {t["surface_elevated"]};
            border: 1px solid {t["border"]};
            border-radius: 6px;
            padding: 10px 12px;
            color: {t["text"]};
            font-size: {fs["input"]}px;
            selection-background-color: {t["accent"]};
            selection-color: {t["background"]};
        }}

        QLineEdit:focus {{
            border: 1.5px solid {t["accent"]};
            background-color: {t["surface_focus"]};
        }}

        QLineEdit:disabled {{
            color: {t["text_soft"]};
            background-color: {t["surface"]};
            border-color: {t["surface_hover"]};
        }}

        #pathDisplay {{
            background-color: {t["surface"]};
            color: {t["text_soft"]};
            border-color: {t["surface_hover"]};
        }}
    """


def button_styles():
    return f"""
        #primaryButton {{
            background-color: {t["accent"]};
            border: none;
            border-radius: 8px;
            padding: 12px 32px;
            color: {t["text_button"]};
            font-weight: 700;
            font-size: {fs["button"]}px;
            min-width: 110px;
        }}

        #primaryButton:hover {{ background-color: {t["accent_hover"]}; }}
        #primaryButton:pressed {{ background-color: {t["accent_pressed"]}; }}

        #primaryButton:disabled {{
            background-color: {t["surface_elevated"]};
            color: {t["text_soft"]};
            border: 1px solid {t["border"]};
        }}

        #secondaryButton {{
            background-color: {t["surface_elevated"]};
            border: 1px solid {t["border"]};
            border-radius: 6px;
            padding: 8px 14px;
            color: #C3CDDB;
            font-size: {fs["secondary_button"]}px;
        }}

        #secondaryButton:hover {{
            background-color: {t["surface_hover"]};
            border-color: {t["border_hover"]};
            color: {t["text"]};
        }}

        #dangerButton {{
            background-color: {t["surface_elevated"]};
            border: 1.5px solid {t["danger"]};
            border-radius: 8px;
            padding: 12px 28px;
            color: {t["danger"]};
            font-weight: 700;
            font-size: {fs["button"]}px;
            min-width: 100px;
        }}

        #dangerButton:hover {{ background-color: rgba(255, 77, 109, 0.10); }}

        #dangerButton:disabled {{
            background-color: {t["surface"]};
            color: {t["text_soft"]};
            border-color: {t["border"]};
        }}

        #linkButton {{
            background: transparent;
            border: none;
            color: {t["accent"]};
            font-size: {fs["status"]}px;
            font-weight: 600;
            padding: 4px 8px;
            text-decoration: underline;
        }}

        #linkButton:hover {{ color: {t["accent_hover"]}; }}
    """


def control_styles():
    return f"""
        #segmentControl {{
            background-color: {t["surface_elevated"]};
            border: 1px solid {t["border"]};
            border-radius: 8px;
        }}

        #segmentControl QPushButton {{
            background-color: transparent;
            border: none;
            border-radius: 6px;
            padding: 8px 18px;
            color: {t["text_secondary"]};
            font-size: {fs["segment"]}px;
            font-weight: 500;
            min-width: 80px;
        }}

        #segmentControl QPushButton:hover {{
            color: {t["text"]};
            background-color: {t["surface_hover"]};
        }}

        #segmentControl QPushButton[active="true"] {{
            background-color: {t["accent"]};
            color: {t["text_button"]};
            font-weight: 700;
        }}

        QCheckBox {{
            color: {t["text_secondary"]};
            spacing: 8px;
        }}

        QCheckBox::indicator {{
            width: 17px;
            height: 17px;
            border-radius: 4px;
            border: 1.5px solid {t["border_hover"]};
            background: {t["surface_elevated"]};
        }}

        QCheckBox::indicator:hover {{ border-color: {t["accent"]}; }}

        QCheckBox::indicator:checked {{
            background-color: {t["accent"]};
            border-color: {t["accent"]};
        }}

        QProgressBar {{
            background-color: {t["surface_hover"]};
            border: none;
            border-radius: 4px;
            height: 6px;
        }}

        QProgressBar::chunk {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {t["accent_pressed"]}, stop:1 {t["accent"]});
            border-radius: 4px;
        }}
    """


def scrollbar_styles():
    return f"""
        QScrollBar:vertical {{
            background: {t["background"]};
            width: 8px;
            margin: 0;
        }}

        QScrollBar::handle:vertical {{
            background: {t["border"]};
            border-radius: 4px;
            min-height: 24px;
        }}

        QScrollBar::handle:vertical:hover {{ background: {t["border_hover"]}; }}

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
    """


def main_stylesheet():
    return "\n".join([
        global_styles(),
        text_styles(),
        container_styles(),
        input_styles(),
        button_styles(),
        control_styles(),
        scrollbar_styles(),
    ])
