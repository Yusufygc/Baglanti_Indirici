from .registry import default_registry


class PlatformService:
    @staticmethod
    def normalize_url(url):
        return default_registry.normalize_url(url)

    @staticmethod
    def detect(url):
        return default_registry.detect(url)

    @staticmethod
    def is_supported(platform):
        return default_registry.is_supported(platform)

    @staticmethod
    def format_options(platform, option):
        return default_registry.format_options(platform, option)
