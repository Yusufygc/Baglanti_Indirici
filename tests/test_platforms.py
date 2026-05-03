from core.platform.service import PlatformService


def test_platform_detection_known_sites():
    assert PlatformService.detect("https://youtu.be/abc") == "YouTube"
    assert PlatformService.detect("instagram.com/reel/abc") == "Instagram"
    assert PlatformService.detect("https://x.com/user/status/1") == "X (Twitter)"


def test_platform_detection_web_and_invalid():
    assert PlatformService.detect("https://example.com/video") == "Web"
    assert PlatformService.detect("not a url") == "GecersizURL"


def test_format_policy_audio_and_video():
    audio = PlatformService.format_options("Web", "ses")
    assert audio["format"] == "bestaudio/best"
    assert audio["postprocessors"][0]["preferredcodec"] == "mp3"

    youtube = PlatformService.format_options("YouTube", "video")
    assert "bestvideo" in youtube["format"]
