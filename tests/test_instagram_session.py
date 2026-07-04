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
