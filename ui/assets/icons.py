import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QStyle
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize


class IconManager:
    """
    Merkezi icon yöneticisi.
    Hem geliştirme ortamında hem PyInstaller EXE'de doğru path döndürür.
    """
    _cache: dict = {}
    _base_dir: str | None = None

    @classmethod
    def _get_base_dir(cls) -> str:
        if cls._base_dir is None:
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller EXE: dosyalar geçici _MEIPASS dizinine çıkarılır
                cls._base_dir = sys._MEIPASS
            else:
                current_path = Path(__file__).resolve()
                for parent in current_path.parents:
                    if (parent / "icons" / "icon.ico").exists():
                        cls._base_dir = str(parent)
                        break
                else:
                    # Geliştirme: ui/assets/icons.py -> proje kökü
                    cls._base_dir = str(current_path.parents[2])
        return cls._base_dir

    @classmethod
    def resource_path(cls, relative_path: str) -> str:
        """EXE ve geliştirme ortamı için doğru mutlak path döndürür."""
        return os.path.join(cls._get_base_dir(), relative_path)

    @classmethod
    def app_icon(cls) -> QIcon:
        """Ana pencere ikonu (icon.ico)."""
        path = cls.resource_path('icons/icon.ico')
        if os.path.exists(path):
            return QIcon(path)
        return QIcon()

    @classmethod
    def get(cls, name: str, size: int | None = None) -> QIcon:
        """
        İsme göre ikon döndürür ve cache'ler.
        Önce icons/<name>.svg, sonra .png dener; yoksa Qt built-in kullanır.
        """
        cache_key = f"{name}@{size}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        icon = cls._load_from_file(name)
        if icon.isNull():
            icon = cls._load_builtin(name)

        if size is not None and not icon.isNull():
            pixmap = icon.pixmap(QSize(size, size))
            icon = QIcon(pixmap)

        cls._cache[cache_key] = icon
        return icon

    @classmethod
    def _load_from_file(cls, name: str) -> QIcon:
        for ext in ('svg', 'png', 'ico'):
            path = cls.resource_path(f'icons/{name}.{ext}')
            if os.path.exists(path):
                return QIcon(path)
        return QIcon()

    @classmethod
    def _load_builtin(cls, name: str) -> QIcon:
        style = QApplication.style()
        mapping = {
            'folder':      QStyle.SP_DirIcon,
            'folder_open': QStyle.SP_DirOpenIcon,
            'download':    QStyle.SP_ArrowDown,
            'cancel':      QStyle.SP_DialogCancelButton,
            'file':        QStyle.SP_FileIcon,
        }
        if name in mapping:
            return style.standardIcon(mapping[name])
        return QIcon()

    @classmethod
    def clear_cache(cls) -> None:
        cls._cache.clear()
