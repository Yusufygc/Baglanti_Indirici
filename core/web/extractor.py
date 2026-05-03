import html
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from html.parser import HTMLParser


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0 Safari/537.36"
)

MEDIA_EXTENSIONS = (".m3u8", ".mp4", ".webm", ".m4v", ".mov")
MAX_IFRAME_DEPTH = 3
MAX_VISITED_PAGES = 8
REQUEST_TIMEOUT = 15

MEDIA_URL_RE = re.compile(
    r"""(?P<url>(?:https?:)?(?:\\?/\\?/|//)[^'"<>\s\\]+?\.(?:m3u8|mp4|webm|m4v|mov)(?:\?[^'"<>\s\\]*)?)""",
    re.IGNORECASE,
)
QUOTED_MEDIA_RE = re.compile(
    r"""["'](?P<url>[^"']+?\.(?:m3u8|mp4|webm|m4v|mov)(?:\?[^"']*)?)["']""",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class WebMediaResult:
    media_url: str
    source_page_url: str
    media_type: str


class _MediaHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.media_candidates: list[str] = []
        self.iframe_candidates: list[str] = []
        self._in_script = False
        self._script_chunks: list[str] = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        tag = tag.lower()

        if tag == "script":
            self._in_script = True

        if tag == "iframe":
            src = attrs_dict.get("src")
            if src:
                self.iframe_candidates.append(src)
            return

        if tag in ("video", "source", "a"):
            url = attrs_dict.get("src") or attrs_dict.get("href")
            if url:
                self.media_candidates.append(url)

    def handle_endtag(self, tag):
        if tag.lower() == "script":
            self._in_script = False

    def handle_data(self, data):
        if self._in_script and data:
            self._script_chunks.append(data)

    def script_text(self):
        return "\n".join(self._script_chunks)


class MediaCandidateParser:
    def parse(self, html_text: str):
        parser = _MediaHTMLParser()
        parser.feed(html_text)
        return {
            "media": _unique(parser.media_candidates + _script_media_urls(parser.script_text())),
            "iframes": _unique(parser.iframe_candidates),
        }


class HtmlFetcher:
    def fetch(self, url: str, referer: str) -> str | None:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": referer,
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
                content_type = response.headers.get("Content-Type", "")
                final_url = response.geturl()
                if _is_media_url(final_url) or _looks_like_media_content(content_type):
                    return None

                raw = response.read(2_000_000)
                charset = response.headers.get_content_charset() or "utf-8"
                return raw.decode(charset, errors="replace")
        except (urllib.error.URLError, TimeoutError, ValueError):
            return None


class MediaUrlResolver:
    @staticmethod
    def normalize(url: str) -> str:
        return _normalize_url(url)

    @staticmethod
    def is_media_url(url: str) -> bool:
        return _is_media_url(url)

    @staticmethod
    def media_type(url: str) -> str:
        return _media_type(url)

    @staticmethod
    def resolve(candidate: str, base_url: str) -> str:
        return _resolve_candidate(candidate, base_url)


class WebMediaExtractor:
    def __init__(self, fetcher=None, parser=None, resolver=None):
        self.fetcher = fetcher or HtmlFetcher()
        self.parser = parser or MediaCandidateParser()
        self.resolver = resolver or MediaUrlResolver()

    @staticmethod
    def extract(url: str) -> WebMediaResult | None:
        return WebMediaExtractor().find(url)

    def find(self, url: str) -> WebMediaResult | None:
        normalized_url = self.resolver.normalize(url)
        if self.resolver.is_media_url(normalized_url):
            return WebMediaResult(
                media_url=normalized_url,
                source_page_url=normalized_url,
                media_type=self.resolver.media_type(normalized_url),
            )
        return self._extract_from_page(normalized_url, normalized_url, depth=0, visited=set())

    def _extract_from_page(
        self,
        url: str,
        original_url: str,
        depth: int,
        visited: set[str],
    ) -> WebMediaResult | None:
        if depth > MAX_IFRAME_DEPTH or len(visited) >= MAX_VISITED_PAGES:
            return None

        normalized_url = self.resolver.normalize(url)
        if normalized_url in visited:
            return None
        visited.add(normalized_url)

        if self.resolver.is_media_url(normalized_url):
            return WebMediaResult(
                normalized_url,
                normalized_url,
                self.resolver.media_type(normalized_url),
            )

        html_text = self.fetcher.fetch(normalized_url, referer=original_url)
        if not html_text:
            return None

        candidates = self.parser.parse(html_text)
        for candidate in candidates["media"]:
            media_url = self.resolver.resolve(candidate, normalized_url)
            if self.resolver.is_media_url(media_url):
                return WebMediaResult(
                    media_url,
                    normalized_url,
                    self.resolver.media_type(media_url),
                )

        for iframe in candidates["iframes"]:
            iframe_url = self.resolver.resolve(iframe, normalized_url)
            result = self._extract_from_page(iframe_url, original_url, depth + 1, visited)
            if result:
                return result

        return None


def _normalize_url(url: str) -> str:
    cleaned = (url or "").strip()
    if not cleaned:
        return cleaned
    parsed = urllib.parse.urlparse(cleaned)
    if not parsed.scheme and "." in cleaned.split("/")[0]:
        return f"https://{cleaned}"
    return cleaned


def _is_media_url(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    path = urllib.parse.unquote(parsed.path).lower()
    return any(path.endswith(extension) for extension in MEDIA_EXTENSIONS)


def _media_type(url: str) -> str:
    return "hls" if urllib.parse.urlparse(url).path.lower().endswith(".m3u8") else "file"


def _looks_like_media_content(content_type: str) -> bool:
    lowered = content_type.lower()
    return (
        lowered.startswith("video/")
        or "mpegurl" in lowered
        or "application/vnd.apple.mpegurl" in lowered
    )


def _resolve_candidate(candidate: str, base_url: str) -> str:
    value = html.unescape(candidate).strip().strip("\"'")
    value = value.replace("\\/", "/")
    if value.startswith("//"):
        parsed_base = urllib.parse.urlparse(base_url)
        value = f"{parsed_base.scheme}:{value}"
    return urllib.parse.urljoin(base_url, value)


def _script_media_urls(script_text: str) -> list[str]:
    matches = []
    normalized_text = script_text.replace("\\/", "/")
    for match in MEDIA_URL_RE.finditer(normalized_text):
        matches.append(match.group("url"))
    for match in QUOTED_MEDIA_RE.finditer(normalized_text):
        matches.append(match.group("url"))
    return matches


def _unique(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result
