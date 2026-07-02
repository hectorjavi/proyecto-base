"""Resolución y obtención bajo demanda de artefactos ONNX (Google Drive)."""

from __future__ import annotations

import logging
import threading
from pathlib import Path

import gdown

logger = logging.getLogger(__name__)

_RETINANET_BIRD_LITE = "retinanet_bird_lite.onnx"
_MODELS_SUBDIR = "models"
_RETINANET_DRIVE_FILE_ID = "1q9zm6G-Tdl3EonEbNHrMmO0yRQ21Wydt"
_RETINANET_DRIVE_URL = (
    f"https://drive.google.com/file/d/{_RETINANET_DRIVE_FILE_ID}/view?usp=sharing"
)

_ensure_lock = threading.Lock()


def _package_dir() -> Path:
    return Path(__file__).resolve().parent


def retinanet_bird_lite_path() -> Path:
    """Ruta absoluta al archivo `models/retinanet_bird_lite.onnx`."""
    return _package_dir() / _MODELS_SUBDIR / _RETINANET_BIRD_LITE


def ensure_retinanet_bird_lite() -> Path:
    """
    Garantiza que exista `retinanet_bird_lite.onnx` en `models/`.

    Si no está en disco, lo descarga desde Google Drive con gdown.
    """
    path = retinanet_bird_lite_path()
    if path.is_file():
        return path

    with _ensure_lock:
        if path.is_file():
            return path

        path.parent.mkdir(parents=True, exist_ok=True)
        partial = path.with_suffix(path.suffix + ".partial")

        try:
            if partial.is_file():
                partial.unlink()

            out = gdown.download(
                url=_RETINANET_DRIVE_URL,
                output=str(partial),
                fuzzy=True,
                quiet=True,
            )
            if not out or not partial.is_file():
                raise RuntimeError("gdown no generó el archivo esperado")

            partial.replace(path)
            logger.info("Modelo RetinaNet bird lite descargado en %s", path)
        except Exception:
            logger.exception("Fallo al descargar retinanet_bird_lite.onnx desde Drive")
            if partial.is_file():
                partial.unlink(missing_ok=True)
            raise

    return path
