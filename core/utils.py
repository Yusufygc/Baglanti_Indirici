import urllib.parse

class PlatformHelper:
    """
    URL analizi ve platform belirleme işlemlerini yürüten yardımcı sınıf.
    """
    
    @staticmethod
    def get_platform_name(url):
        try:
            parsed_url = urllib.parse.urlparse(url)
            domain = parsed_url.netloc

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
