from core.web.extractor import WebMediaExtractor


class FakeFetcher:
    def __init__(self, pages):
        self.pages = pages

    def fetch(self, url, referer):
        return self.pages.get(url)


def test_direct_media_url_returns_result():
    result = WebMediaExtractor.extract("https://cdn.test/video.mp4")
    assert result.media_url == "https://cdn.test/video.mp4"
    assert result.media_type == "file"


def test_video_source_relative_url_is_resolved():
    extractor = WebMediaExtractor(fetcher=FakeFetcher({
        "https://site.test/page": '<video src="video.mp4"></video>',
    }))
    result = extractor.find("https://site.test/page")
    assert result.media_url == "https://site.test/video.mp4"


def test_source_m3u8_url_is_resolved():
    extractor = WebMediaExtractor(fetcher=FakeFetcher({
        "https://site.test/page": '<source src="/stream.m3u8">',
    }))
    result = extractor.find("https://site.test/page")
    assert result.media_url == "https://site.test/stream.m3u8"
    assert result.media_type == "hls"


def test_iframe_recursion_finds_nested_media():
    extractor = WebMediaExtractor(fetcher=FakeFetcher({
        "https://site.test/outer": '<iframe src="/inner"></iframe>',
        "https://site.test/inner": '<script>var file="https:\\/\\/cdn.test\\/movie.webm";</script>',
    }))
    result = extractor.find("https://site.test/outer")
    assert result.media_url == "https://cdn.test/movie.webm"


def test_empty_page_returns_none():
    extractor = WebMediaExtractor(fetcher=FakeFetcher({
        "https://site.test/empty": "<html></html>",
    }))
    assert extractor.find("https://site.test/empty") is None
