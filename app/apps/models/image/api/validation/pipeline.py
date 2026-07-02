"""
Image processing pipeline — resize + JPEG conversion.

Usage::

    from .validation import get_default_pipeline

    def validate_file(self, value):
        return get_default_pipeline().process(value)
"""

from __future__ import annotations

from django.core.files.base import ContentFile

from .resize.base import AbstractResizer


class ImageValidationPipeline:
    """Resizes and converts uploaded images to JPEG before storage."""

    def __init__(self, resizer: AbstractResizer) -> None:
        self.resizer = resizer

    def process(self, file) -> ContentFile:
        """Resize *file* and return a storage-ready JPEG ContentFile."""
        return self.resizer.resize(file)
