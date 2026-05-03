from .style_sections import main_stylesheet
from .theme import LOG_COLORS


class StyleManager:
    @staticmethod
    def get_main_stylesheet():
        return main_stylesheet()

    @staticmethod
    def get_log_span(color_code, message):
        color = LOG_COLORS.get(color_code, "#F0F2F5")
        return f"<span style='color:{color};'>{message}</span>"
