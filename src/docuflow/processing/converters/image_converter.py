from pathlib import Path

from docuflow.processing.converters.base_converter import BaseConverter
from docuflow.processing.converters.convert_image_text import convert_image_to_markdown
from docuflow.schemas import RawDocument
from docuflow.utils import get_logger
from docuflow.utils.dependency_checks import is_paddleocr_available

logger = get_logger(__name__)


class ImageConverter(BaseConverter):
    """Convert image files into markdown using the configured OCR backend."""

    SUPPORTED_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".gif")

    def convert(self, raw_document: RawDocument) -> str:
        file_format = raw_document.metadata.get("format", "").lower()
        if file_format not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported image format: {file_format}")

        # If PaddleOCR (PPStructureV3) isn't available, skip conversion gracefully.
        # Returning an empty string signals there's no markdown produced for this image.
        if not is_paddleocr_available():
            logger.warning(
                "PaddleOCR (PPStructureV3) not available: skipping image conversion for %s",
                raw_document.source,
            )
            return ""

        return convert_image_to_markdown(Path(raw_document.source))
