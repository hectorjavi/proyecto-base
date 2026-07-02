"""Build the default image processing pipeline (resize + JPEG only)."""

from __future__ import annotations

from .pipeline import ImageValidationPipeline
from .resize.strategies import LanczosResizer

_RESIZER = LanczosResizer(max_side=1500)

_pipeline: ImageValidationPipeline | None = None


def get_default_pipeline() -> ImageValidationPipeline:
    """Lazy singleton — reads settings after Django startup."""
    global _pipeline
    if _pipeline is None:
        _pipeline = ImageValidationPipeline(resizer=_RESIZER)
    return _pipeline


def reset_default_pipeline_for_tests() -> None:
    global _pipeline
    _pipeline = None
