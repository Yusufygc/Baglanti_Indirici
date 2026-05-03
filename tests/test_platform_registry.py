from core.domain import PlatformProfile
from core.platform.registry import PlatformRegistry


def test_registry_detects_registered_platform():
    registry = PlatformRegistry([
        PlatformProfile("ExampleVideo", ("video.example",), "#123456"),
    ])

    assert registry.detect("video.example/watch/1") == "ExampleVideo"
    assert registry.color_for("ExampleVideo") == "#123456"


def test_registry_uses_profile_format_policy():
    registry = PlatformRegistry([
        PlatformProfile("Custom", ("custom.test",), format_policy=lambda mode: {"format": mode}),
    ])

    assert registry.format_options("Custom", "video") == {"format": "video"}
