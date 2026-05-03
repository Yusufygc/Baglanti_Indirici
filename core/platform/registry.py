import urllib.parse

from core.domain import PlatformProfile
from core.domain.models import DownloadMode, default_format_policy


def youtube_format_policy(mode: str) -> dict:
    if mode == DownloadMode.AUDIO.value:
        return default_format_policy(mode)
    return {"format": "best[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best"}


class PlatformRegistry:
    def __init__(self, profiles: list[PlatformProfile] | None = None):
        self._profiles: list[PlatformProfile] = []
        for profile in profiles or default_profiles():
            self.register(profile)

    def register(self, profile: PlatformProfile) -> None:
        self._profiles = [item for item in self._profiles if item.name != profile.name]
        self._profiles.append(profile)

    def normalize_url(self, url: str) -> str:
        cleaned = (url or "").strip()
        if not cleaned:
            return cleaned
        parsed_url = urllib.parse.urlparse(cleaned)
        if not parsed_url.scheme and "." in cleaned.split("/")[0]:
            return f"https://{cleaned}"
        return cleaned

    def detect(self, url: str) -> str:
        try:
            normalized_url = self.normalize_url(url)
            parsed_url = urllib.parse.urlparse(normalized_url)
            domain = parsed_url.netloc.lower()

            if not domain:
                return "GecersizURL"

            for profile in self._profiles:
                if profile.matches(domain):
                    return profile.name

            if parsed_url.scheme in ("http", "https"):
                return "Web"
            return "Bilinmeyen"
        except (TypeError, ValueError):
            return "GecersizURL"

    def is_supported(self, platform: str) -> bool:
        return platform not in ("Bilinmeyen", "GecersizURL")

    def profile_for(self, platform: str) -> PlatformProfile | None:
        for profile in self._profiles:
            if profile.name == platform:
                return profile
        if platform == "Web":
            return PlatformProfile("Web", tuple(), "#8B91A7")
        return None

    def format_options(self, platform: str, mode: str) -> dict:
        profile = self.profile_for(platform)
        if profile:
            return profile.format_options(mode)
        return default_format_policy(mode)

    def color_for(self, platform: str) -> str:
        profile = self.profile_for(platform)
        return profile.color if profile else "#8B91A7"


def default_profiles() -> list[PlatformProfile]:
    return [
        PlatformProfile("Pinterest", ("pinterest.com", "pin.it"), "#E60023"),
        PlatformProfile("YouTube", ("youtube.com", "youtu.be"), "#FF4444", youtube_format_policy),
        PlatformProfile("TikTok", ("tiktok.com",), "#69C9D0"),
        PlatformProfile("Instagram", ("instagram.com",), "#E1306C"),
        PlatformProfile("Facebook", ("facebook.com", "fb.watch"), "#1877F2"),
        PlatformProfile("X (Twitter)", ("twitter.com", "x.com"), "#1D9BF0"),
        PlatformProfile("Twitch", ("twitch.tv",), "#9146FF"),
        PlatformProfile("SoundCloud", ("soundcloud.com",), "#FF5500"),
    ]


default_registry = PlatformRegistry()
