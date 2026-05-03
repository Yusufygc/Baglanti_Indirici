import re


ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


class ProgressFormatter:
    @staticmethod
    def clean_terminal_text(value):
        if value is None:
            return "Bilinmiyor"
        text = str(value)
        text = ANSI_ESCAPE_RE.sub("", text)
        return " ".join(text.split()) or "Bilinmiyor"

    @staticmethod
    def from_yt_dlp(data):
        status = data.get("status")
        if status == "finished":
            return 100, "İşleniyor…"
        if status != "downloading":
            return None

        total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
        downloaded = data.get("downloaded_bytes", 0)
        percentage = int(downloaded * 100 / total) if total > 0 else 0

        speed_text = data.get("_speed_str")
        eta_text = data.get("_eta_str")

        if not speed_text:
            speed = data.get("speed", 0)
            speed_text = f"{speed / 1024 / 1024:.2f} MiB/s" if speed else "Bilinmiyor"

        if not eta_text:
            eta = data.get("eta", 0)
            eta_text = f"{eta}s" if eta else "Bilinmiyor"

        speed_text = ProgressFormatter.clean_terminal_text(speed_text)
        eta_text = ProgressFormatter.clean_terminal_text(eta_text)

        info = data.get("info_dict", {})
        playlist_index = info.get("playlist_index")
        playlist_count = info.get("n_entries")
        playlist_text = (
            f" • Video {playlist_index}/{playlist_count}"
            if playlist_index and playlist_count
            else ""
        )

        return percentage, f"Hız: {speed_text} • Kalan: {eta_text}{playlist_text}"
