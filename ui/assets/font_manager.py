import sys
from pathlib import Path

from PyQt5.QtGui import QFont, QFontDatabase

from ui.themeing.font_profiles import get_font_profile


class FontManager:
    UI_FAMILY = "Inter Variable"
    MONO_FAMILY = "JetBrains Mono"
    FALLBACK_UI = "Segoe UI"
    FALLBACK_MONO = "Consolas"
    BASE_POINT_SIZE = 10

    _loaded = False
    _base_dir: str | None = None

    @classmethod
    def load_fonts(cls):
        if cls._loaded:
            return

        for font_file in cls.font_dir().glob("*.ttf"):
            QFontDatabase.addApplicationFont(str(font_file))

        cls._loaded = True

    @classmethod
    def application_font(cls):
        family = cls.ui_family()
        font = QFont(family, cls.BASE_POINT_SIZE)
        if get_font_profile().get("prefer_italic"):
            font.setItalic(True)
        font.setStyleStrategy(QFont.PreferAntialias)
        return font

    @classmethod
    def ui_family(cls):
        return cls._first_available(get_font_profile()["ui_families"], cls.FALLBACK_UI)

    @classmethod
    def mono_family(cls):
        return cls._first_available(get_font_profile()["mono_families"], cls.FALLBACK_MONO)

    @classmethod
    def font_stack(cls):
        return f"'{cls.ui_family()}', '{cls.FALLBACK_UI}', Arial, sans-serif"

    @classmethod
    def mono_stack(cls):
        return f"'{cls.mono_family()}', '{cls.FALLBACK_MONO}', monospace"

    @classmethod
    def font_dir(cls):
        return Path(cls._get_base_dir()) / "ui" / "assets" / "fonts"

    @classmethod
    def _family_available(cls, family):
        return family in QFontDatabase().families()

    @classmethod
    def _first_available(cls, candidates, fallback):
        families = set(QFontDatabase().families())
        for family in candidates:
            if family in families:
                return family
        return fallback

    @classmethod
    def _get_base_dir(cls) -> str:
        if cls._base_dir is None:
            if hasattr(sys, "_MEIPASS"):
                cls._base_dir = sys._MEIPASS
            else:
                current_path = Path(__file__).resolve()
                for parent in current_path.parents:
                    if (parent / "ui" / "assets" / "fonts").exists():
                        cls._base_dir = str(parent)
                        break
                else:
                    cls._base_dir = str(current_path.parents[2])
        return cls._base_dir
