from .platform.service import PlatformService

class PlatformHelper:
    """
    Geriye dönük uyumluluk adaptörü.
    Yeni kod doğrudan PlatformService kullanmalı.
    """
    
    @staticmethod
    def normalize_url(url):
        return PlatformService.normalize_url(url)

    @staticmethod
    def get_platform_name(url):
        return PlatformService.detect(url)
            
    @staticmethod
    def get_video_format_options(platform, secenek):
        return PlatformService.format_options(platform, secenek)
