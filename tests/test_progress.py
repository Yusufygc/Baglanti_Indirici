from core.download.progress import ProgressFormatter


def test_clean_terminal_text_removes_ansi_codes():
    assert ProgressFormatter.clean_terminal_text("\x1b[0;32m2.35MiB/s\x1b[0m") == "2.35MiB/s"


def test_format_downloading_progress():
    percent, message = ProgressFormatter.from_yt_dlp({
        "status": "downloading",
        "downloaded_bytes": 50,
        "total_bytes": 100,
        "_speed_str": "\x1b[0;32m1.00MiB/s\x1b[0m",
        "_eta_str": "00:10",
        "info_dict": {"playlist_index": 2, "n_entries": 5},
    })

    assert percent == 50
    assert message == "Hız: 1.00MiB/s • Kalan: 00:10 • Video 2/5"


def test_format_finished_progress():
    assert ProgressFormatter.from_yt_dlp({"status": "finished"}) == (100, "İşleniyor…")
