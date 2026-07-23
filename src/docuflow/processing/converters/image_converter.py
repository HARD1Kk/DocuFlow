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
        import importlib.metadata

        file_format = raw_document.metadata.get("format", "").lower()
        if file_format not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported image format: {file_format}")

        try:
            version = importlib.metadata.version("paddleocr")
            parser_name = "paddleocr"
        except Exception:
            try:
                version = importlib.metadata.version("easyocr")
                parser_name = "easyocr"
            except Exception:
                version = "1.0.0"
                parser_name = "ocr"

        raw_document.metadata["parser"] = parser_name
        raw_document.metadata["parser_version"] = version

        return convert_image_to_markdown(Path(raw_document.source))
