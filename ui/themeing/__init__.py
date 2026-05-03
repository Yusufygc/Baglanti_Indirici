from .font_profiles import ACTIVE_FONT_PROFILE, FONT_PROFILES
from .theme import LOG_COLORS, THEME

__all__ = ["ACTIVE_FONT_PROFILE", "FONT_PROFILES", "LOG_COLORS", "StyleManager", "THEME"]


def __getattr__(name):
    if name == "StyleManager":
        from .styles import StyleManager

        return StyleManager
    raise AttributeError(name)
