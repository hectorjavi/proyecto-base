"""
Concrete resize strategies.

LanczosResizer      — downscale to max_side × max_side (Lanczos, EXIF-aware).
                      Always converts the output to JPEG (.jpg).
PassthroughResizer  — no-op; wraps original bytes in a ContentFile.
"""

from __future__ import annotations

import os
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image as PilImage
from PIL import ImageOps

from .base import AbstractResizer

_MAX_SIDE_DEFAULT = 1500
_JPEG_QUALITY = 90


class LanczosResizer(AbstractResizer):
    """
    Downscales an image so that its longest side does not exceed *max_side*
    and always converts the result to JPEG.

    - Uses Lanczos resampling (highest quality downscale filter).
    - Corrects EXIF orientation before resizing.
    - Preserves aspect ratio; never upscales.
    - Converts RGBA / palette / greyscale modes to RGB before saving.
    - Output filename always ends with .jpg regardless of original format.
    """

    def __init__(
        self,
        max_side: int = _MAX_SIDE_DEFAULT,
        jpeg_quality: int = _JPEG_QUALITY,
    ) -> None:
        self.max_side = max_side
        self.jpeg_quality = jpeg_quality

    def resize(self, file) -> ContentFile:
        pos = file.tell() if hasattr(file, "tell") else 0
        raw = file.read()
        if hasattr(file, "seek"):
            file.seek(pos)

        original_name = os.path.basename(getattr(file, "name", "image.jpg"))
        base, _ = os.path.splitext(original_name)
        jpg_name = base + ".jpg"

        with PilImage.open(BytesIO(raw)) as img:
            normalized = ImageOps.exif_transpose(img)
            width, height = normalized.size

            if max(width, height) > self.max_side:
                scale = self.max_side / max(width, height)
                target = (round(width * scale), round(height * scale))
                output_img = normalized.resize(target, PilImage.Resampling.LANCZOS)
            else:
                output_img = normalized

            if output_img.mode not in ("RGB", "L"):
                output_img = output_img.convert("RGB")

            out = BytesIO()
            output_img.save(
                out,
                format="JPEG",
                quality=self.jpeg_quality,
                optimize=True,
            )

        out.seek(0)
        return ContentFile(out.read(), name=jpg_name)


class PassthroughResizer(AbstractResizer):
    """
    No-op strategy.

    Wraps the original file bytes in a ContentFile without any modification.
    Useful for testing or when resizing is handled elsewhere.
    """

    def resize(self, file) -> ContentFile:
        pos = file.tell() if hasattr(file, "tell") else 0
        raw = file.read()
        if hasattr(file, "seek"):
            file.seek(pos)
        name = os.path.basename(getattr(file, "name", "image.jpg"))
        return ContentFile(raw, name=name)
