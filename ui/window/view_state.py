from enum import Enum


class DownloadViewState(Enum):
    IDLE = "idle"
    READY = "ready"
    DOWNLOADING = "downloading"
    SUCCESS = "success"
    ERROR = "error"
    CANCELLED = "cancelled"
