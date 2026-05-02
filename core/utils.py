import urllib.parse

class PlatformHelper:
    """
    URL analizi ve platform belirleme işlemlerini yürüten yardımcı sınıf.
    """
    
    @staticmethod
    def normalize_url(url):
        cleaned = (url or "").strip()
        if not cleaned:
            return cleaned
        parsed_url = urllib.parse.urlparse(cleaned)
        if not parsed_url.scheme and "." in cleaned.split("/")[0]:
            return f"https://{cleaned}"
        return cleaned

    @staticmethod
    def get_platform_name(url):
        try:
            normalized_url = PlatformHelper.normalize_url(url)
            parsed_url = urllib.parse.urlparse(normalized_url)
            domain = parsed_url.netloc.lower()

            if not domain:
                return "GecersizURL"

            if "pinterest.com" in domain or "pin.it" in domain:
                return "Pinterest"
            elif "youtube.com" in domain or "youtu.be" in domain:
                return "YouTube"
            elif "tiktok.com" in domain:
                return "TikTok"
            elif "instagram.com" in domain:
                return "Instagram"
            elif "facebook.com" in domain or "fb.watch" in domain:
                return "Facebook"
            elif "twitter.com" in domain or "x.com" in domain:
                return "X (Twitter)"
            elif parsed_url.scheme in ("http", "https"):
                return "Web"
            else:
                return "Bilinmeyen"
        except:
            return "GecersizURL"
            
    @staticmethod
    def get_video_format_options(platform, secenek):
        """
        Platforma göre en uygun yt-dlp format string'ini döndürür.
        """
        if secenek == "ses":
            return {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            }
            
        # Video seçenekleri
        if platform == "YouTube":
            # YouTube için ayrı akışları birleştiren gelişmiş format
            return {'format': 'best[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best'}
        else:
            # Genel video format stratejisi
            return {'format': 'best[ext=mp4]/bestvideo+bestaudio/best'}
