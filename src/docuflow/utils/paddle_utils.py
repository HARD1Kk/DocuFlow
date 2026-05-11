"""Utility functions for PaddleOCR configuration and initialization."""

from pathlib import Path
from typing import Optional

from paddleocr import PaddleOCR

from docuflow.schemas.ocr import PaddleConfig


def get_paddle_ocr(config: Optional[PaddleConfig] = None) -> PaddleOCR:
    """Initialize and return a PaddleOCR instance with the given configuration.

    Args:
        config: Optional PaddleConfig. If None, uses default configuration.

    Returns:
        Configured PaddleOCR instance.
    """
    if config is None:
        config = PaddleConfig()

    return PaddleOCR(
        lang=config.lang,
        use_textline_orientation=config.use_textline_orientation,
        show_log=False,
    )


def get_model_path(model_name: str, cache_dir: Optional[Path] = None) -> Path:
    """Get the path to a cached PaddleOCR model.

    Args:
        model_name: Name of the model (e.g., "PP-OCRv5_server_det")
        cache_dir: Optional custom cache directory. If None, uses default PaddleOCR cache.

    Returns:
        Path to the model directory.
    """
    if cache_dir is None:
        # Default PaddleOCR cache location
        cache_dir = Path.home() / ".paddleocr" / "whl" / "det"

    model_path = cache_dir / model_name
    return model_path
