ACTIVE_FONT_PROFILE = "modern"

FONT_PROFILES = {
    "modern": {
        "ui_families": ("Inter Variable", "Inter", "Inter Display"),
        "mono_families": ("JetBrains Mono",),
    },
    "playful": {
        "ui_families": ("Nunito", "Nunito Sans", "Inter Variable", "Inter"),
        "mono_families": ("JetBrains Mono",),
    },
    "elegant": {
        "ui_families": ("Cormorant Garamond", "Playfair Display", "Inter Variable", "Inter"),
        "mono_families": ("JetBrains Mono",),
    },
    "classic": {
        "ui_families": ("Playfair Display", "Cormorant Garamond", "Inter Variable", "Inter"),
        "mono_families": ("JetBrains Mono",),
    },
    "italic_classic": {
        "ui_families": ("Cormorant Garamond", "Playfair Display", "Inter Variable", "Inter"),
        "mono_families": ("JetBrains Mono",),
        "prefer_italic": True,
    },
}


def get_font_profile(name=None):
    profile_name = name or ACTIVE_FONT_PROFILE
    if profile_name not in FONT_PROFILES:
        profile_name = "modern"
    return FONT_PROFILES[profile_name]


def font_stack_for_profile(name=None, fallback="Segoe UI"):
    profile = get_font_profile(name)
    families = profile["ui_families"] + (fallback, "Arial", "sans-serif")
    return ", ".join(f"'{family}'" for family in families)
