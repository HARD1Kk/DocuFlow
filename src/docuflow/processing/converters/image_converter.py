from pathlib import Path

from docuflow.interfaces import BaseConverter
from docuflow.processing.converters.convert_image_text import convert_image_to_markdown
from docuflow.schemas import RawDocument
from docuflow.utils import get_logger

logger = get_logger(__name__)


class ImageConverter(BaseConverter):
    """Convert image files into markdown using the configured OCR backend."""

    SUPPORTED_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".gif")

    def convert(self, raw_document: RawDocument) -> str:
        file_format = raw_document.metadata.get("format", "").lower()
        if file_format not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported image format: {file_format}")

        return convert_image_to_markdown(Path(raw_document.source))
