import logging
import sys

from core.logger import get_logger, install_excepthook


def test_get_logger_returns_configured_logger():
    logger = get_logger("test_module")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "baglanti_indirici.test_module"


def test_install_excepthook_replaces_sys_excepthook():
    original_hook = sys.excepthook
    try:
        install_excepthook()
        assert sys.excepthook is not original_hook
    finally:
        sys.excepthook = original_hook


def test_excepthook_logs_without_raising():
    original_hook = sys.excepthook
    try:
        install_excepthook()
        try:
            raise ValueError("test hatasi")
        except ValueError:
            exc_info = sys.exc_info()
        sys.excepthook(*exc_info)
    finally:
        sys.excepthook = original_hook
