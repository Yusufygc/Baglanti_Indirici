import os

from core.instagram import session as ig_session


def _use_temp_paths(monkeypatch, tmp_path):
    cookies = str(tmp_path / "instagram_cookies.txt")
    profile = str(tmp_path / "webprofile")
    monkeypatch.setattr(ig_session, "_COOKIES_PATH", cookies)
    monkeypatch.setattr(ig_session, "_PROFILE_DIR", profile)
    return cookies, profile


def test_write_netscape_cookies_format(monkeypatch, tmp_path):
    cookies_file, _ = _use_temp_paths(monkeypatch, tmp_path)
    ig_session.write_netscape_cookies([
        (".instagram.com", "/", True, 1893456000, "sessionid", "abc123"),
        (".instagram.com", "/", True, 0, "csrftoken", "tok"),
    ])

    content = open(cookies_file, encoding="utf-8").read()
    assert content.startswith("# Netscape HTTP Cookie File")
    lines = [ln for ln in content.splitlines() if ln and not ln.startswith("#")]
    fields = lines[0].split("\t")
    assert fields == [".instagram.com", "TRUE", "/", "TRUE", "1893456000", "sessionid", "abc123"]


def test_has_session_true_only_with_sessionid(monkeypatch, tmp_path):
    _use_temp_paths(monkeypatch, tmp_path)
    assert ig_session.has_session() is False

    ig_session.write_netscape_cookies([(".instagram.com", "/", True, 0, "csrftoken", "tok")])
    assert ig_session.has_session() is False  # sessionid yok

    ig_session.write_netscape_cookies([(".instagram.com", "/", True, 0, "sessionid", "abc")])
    assert ig_session.has_session() is True


def test_clear_session_removes_file(monkeypatch, tmp_path):
    cookies_file, _ = _use_temp_paths(monkeypatch, tmp_path)
    ig_session.write_netscape_cookies([(".instagram.com", "/", True, 0, "sessionid", "abc")])
    assert os.path.isfile(cookies_file)

    ig_session.clear_session()

    assert not os.path.isfile(cookies_file)
    assert ig_session.has_session() is False


def test_cdp_cookies_to_netscape_filters_and_maps():
    cdp = [
        {"name": "sessionid", "value": "s1", "domain": ".instagram.com", "path": "/",
         "expires": 1893456000.5, "secure": True, "httpOnly": True},
        {"name": "csrftoken", "value": "t", "domain": ".instagram.com", "path": "/",
         "expires": -1, "secure": True, "httpOnly": False},  # session cookie -> expiry 0
        {"name": "other", "value": "x", "domain": ".example.com", "path": "/",
         "expires": 0, "secure": False, "httpOnly": False},  # instagram degil -> atlanir
    ]
    out = ig_session.cdp_cookies_to_netscape(cdp)
    assert out == [
        (".instagram.com", "/", True, 1893456000, "sessionid", "s1"),
        (".instagram.com", "/", True, 0, "csrftoken", "t"),
    ]


def test_cdp_cookies_roundtrip_has_session(monkeypatch, tmp_path):
    _use_temp_paths(monkeypatch, tmp_path)
    cdp = [{"name": "sessionid", "value": "abc", "domain": ".instagram.com",
            "path": "/", "expires": -1, "secure": True, "httpOnly": True}]
    ig_session.write_netscape_cookies(ig_session.cdp_cookies_to_netscape(cdp))
    assert ig_session.has_session() is True


def test_find_browser_executable_prefers_chrome(monkeypatch, tmp_path):
    chrome = tmp_path / "Google" / "Chrome" / "Application" / "chrome.exe"
    chrome.parent.mkdir(parents=True)
    chrome.write_text("x")
    monkeypatch.setenv("PROGRAMFILES", str(tmp_path))
    monkeypatch.setenv("PROGRAMFILES(X86)", str(tmp_path / "x86"))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "local"))
    name, path = ig_session.find_browser_executable()
    assert name == "chrome"
    assert path == str(chrome)


def test_find_browser_executable_none_when_absent(monkeypatch, tmp_path):
    monkeypatch.setenv("PROGRAMFILES", str(tmp_path / "a"))
    monkeypatch.setenv("PROGRAMFILES(X86)", str(tmp_path / "b"))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "c"))
    assert ig_session.find_browser_executable() is None
