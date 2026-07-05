import faulthandler
import logging
import os
import sys
import threading
from logging.handlers import RotatingFileHandler

from core.config import get_user_data_dir

# Loglar kullanici-yazilabilir dizine yazilir. Exe Program Files'a kurulursa
# exe yani (get_base_path) yazilamaz -> WinError 5 ile acilista cokerdi.
_LOG_DIR = os.path.join(get_user_data_dir(), "logs")
_LOG_PATH = os.path.join(_LOG_DIR, "app.log")
_NATIVE_CRASH_LOG_PATH = os.path.join(_LOG_DIR, "native_crash.log")
_ROOT_NAME = "baglanti_indirici"
_configured = False
_native_crash_file = None


def _configure() -> None:
    global _configured
    if _configured:
        return
    os.makedirs(_LOG_DIR, exist_ok=True)
    handler = RotatingFileHandler(_LOG_PATH, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root = logging.getLogger(_ROOT_NAME)
    root.setLevel(logging.INFO)
    root.addHandler(handler)
    _configured = True


def get_logger(name: str) -> logging.Logger:
    _configure()
    return logging.getLogger(f"{_ROOT_NAME}.{name}")


def install_excepthook() -> None:
    logger = get_logger("crash")

    def _hook(exctype, value, tb):
        logger.critical("Yakalanmamis hata", exc_info=(exctype, value, tb))

    sys.excepthook = _hook

    def _thread_hook(args):
        thread_name = args.thread.name if args.thread else "?"
        logger.critical(
            "Worker thread'de yakalanmamis hata (%s)",
            thread_name,
            exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
        )

    threading.excepthook = _thread_hook


def enable_native_crash_dump() -> None:
    """
    Python exception olarak yakalanamayan native cokmeler (segfault vb.) icin
    faulthandler kurar. Dosya nesnesi process suresince acik tutulmali (module-level
    referans), aksi halde GC tarafindan kapatilip faulthandler islevsiz kalir.
    """
    global _native_crash_file
    _configure()
    os.makedirs(_LOG_DIR, exist_ok=True)
    _native_crash_file = open(_NATIVE_CRASH_LOG_PATH, "a", encoding="utf-8")
    faulthandler.enable(file=_native_crash_file, all_threads=True)
