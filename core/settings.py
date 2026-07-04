import json
import os
from pathlib import Path

_SETTINGS_PATH = os.path.join(Path.home(), ".baglanti_indirici", "settings.json")


def load_theme() -> str:
    try:
        with open(_SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        theme = data.get("theme")
        return theme if theme in ("dark", "light") else "dark"
    except (OSError, json.JSONDecodeError):
        return "dark"


def save_theme(theme_name: str) -> None:
    os.makedirs(os.path.dirname(_SETTINGS_PATH), exist_ok=True)
    with open(_SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump({"theme": theme_name}, f)
