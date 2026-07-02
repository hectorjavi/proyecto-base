"""
Image upload processing package — resize and JPEG conversion.

Public API
~~~~~~~~~~
get_default_pipeline()
    Lazy singleton — use this from serializers and admin.
"""

from .factory import get_default_pipeline, reset_default_pipeline_for_tests
from .pipeline import ImageValidationPipeline
from .resize.strategies import LanczosResizer, PassthroughResizer

__all__ = [
    "ImageValidationPipeline",
    "LanczosResizer",
    "PassthroughResizer",
    "get_default_pipeline",
    "reset_default_pipeline_for_tests",
]
