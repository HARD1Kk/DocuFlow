"""OCR interface definitions."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional


class IOCRModel(ABC):
    """Base contract for OCR engines."""

    @abstractmethod
    def extract(
        self, file_path: str | Path, save_processed: bool = False, output_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Extract text from an image file.

        Args:
            file_path: Path to the image file.
            save_processed: Whether to save the preprocessed image.
            output_dir: Directory to save processed images.

        Returns:
            Dictionary containing extracted text and metadata.
        """
