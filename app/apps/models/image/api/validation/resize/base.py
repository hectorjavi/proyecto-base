"""
Strategy interface for image resizing.

All concrete resize strategies must return a ContentFile and must NOT
consume the input file (pointer is reset after reading).
"""

from __future__ import annotations

import abc

from django.core.files.base import ContentFile


class AbstractResizer(abc.ABC):
    """
    Strategy Pattern — defines the resize contract.

    Concrete strategies:
      - LanczosResizer      : downscale to max_side preserving aspect ratio.
      - PassthroughResizer  : no-op, wraps original bytes in a ContentFile.
    """

    @abc.abstractmethod
    def resize(self, file) -> ContentFile:
        """
        Process *file* and return a ContentFile with the result.

        The input file pointer is reset to its original position after reading
        so that downstream code can still read the original content if needed.

        Args:
            file: Any readable file-like object (UploadedFile, ContentFile…).

        Returns:
            ContentFile ready for storage or further processing.
        """
