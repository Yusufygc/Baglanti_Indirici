from pathlib import Path

from ui.themeing.font_profiles import (
    ACTIVE_FONT_PROFILE,
    FONT_PROFILES,
    font_stack_for_profile,
    get_font_profile,
)


def test_playful_font_files_exist():
    font_dir = Path(__file__).resolve().parents[1] / "ui" / "assets" / "fonts"
    assert (font_dir / "Nunito-Variable.ttf").exists()
    assert (font_dir / "Nunito-Italic-Variable.ttf").exists()


def test_classic_font_files_exist():
    font_dir = Path(__file__).resolve().parents[1] / "ui" / "assets" / "fonts"
    assert (font_dir / "CormorantGaramond-Variable.ttf").exists()
    assert (font_dir / "CormorantGaramond-Italic-Variable.ttf").exists()
    assert (font_dir / "PlayfairDisplay-Variable.ttf").exists()
    assert (font_dir / "PlayfairDisplay-Italic-Variable.ttf").exists()


def test_active_font_profile_is_valid():
    assert ACTIVE_FONT_PROFILE in FONT_PROFILES


def test_modern_profile_keeps_inter_fallback():
    assert get_font_profile("modern")["ui_families"][0] == "Inter Variable"


def test_elegant_profile_uses_cormorant_first():
    assert get_font_profile("elegant")["ui_families"][0] == "Cormorant Garamond"


def test_classic_profile_uses_playfair_first():
    assert get_font_profile("classic")["ui_families"][0] == "Playfair Display"


def test_italic_classic_profile_marks_italic_preference():
    assert get_font_profile("italic_classic")["prefer_italic"] is True


def test_unknown_profile_falls_back_to_modern():
    assert get_font_profile("missing") == FONT_PROFILES["modern"]


def test_font_stack_contains_profile_and_fallbacks():
    stack = font_stack_for_profile("playful")
    assert "'Nunito'" in stack
    assert "'Segoe UI'" in stack
    assert "'sans-serif'" in stack


def test_classic_font_stack_contains_profile_and_fallbacks():
    stack = font_stack_for_profile("classic")
    assert "'Playfair Display'" in stack
    assert "'Segoe UI'" in stack
    assert "'sans-serif'" in stack
