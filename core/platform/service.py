import urllib.parse


class PlatformService:
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
    def detect(url):
        try:
            normalized_url = PlatformService.normalize_url(url)
            parsed_url = urllib.parse.urlparse(normalized_url)
            domain = parsed_url.netloc.lower()

            if not domain:
                return "GecersizURL"

            if "pinterest.com" in domain or "pin.it" in domain:
                return "Pinterest"
            if "youtube.com" in domain or "youtu.be" in domain:
                return "YouTube"
            if "tiktok.com" in domain:
                return "TikTok"
            if "instagram.com" in domain:
                return "Instagram"
            if "facebook.com" in domain or "fb.watch" in domain:
                return "Facebook"
            if "twitter.com" in domain or "x.com" in domain:
                return "X (Twitter)"
            if parsed_url.scheme in ("http", "https"):
                return "Web"
            return "Bilinmeyen"
        except (TypeError, ValueError):
            return "GecersizURL"

    @staticmethod
    def is_supported(platform):
        return platform not in ("Bilinmeyen", "GecersizURL")

    @staticmethod
    def format_options(platform, option):
        if option == "ses":
            return {
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            }

        if platform == "YouTube":
            return {"format": "best[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best"}
        return {"format": "best[ext=mp4]/bestvideo+bestaudio/best"}
