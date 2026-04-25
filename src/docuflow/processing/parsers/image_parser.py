from docuflow.core.converters import ConverterFactory
from docuflow.schemas import RawDocument
from docuflow.utils import get_logger


class ImageParser:
    def __init__(self) -> None:
        self.logger = get_logger(__name__)

    def parse(self, raw_document: RawDocument) -> str:
        """Extract text from image formats using the converter layer."""
        try:
            file_format = raw_document.metadata.get("format", "").lower()
            self.logger.info(f"Parsing {raw_document.source} ({file_format})")

            result = ConverterFactory.get_converter(raw_document.source).convert(raw_document)

            if result is None:
                self.logger.error(f"Conversion returned None for {file_format}")
                raise RuntimeError("Conversion failed: None returned")

            self.logger.info(f"Successfully parsed: {len(result)} chars")
            return result

        except Exception as e:
            self.logger.error(f"Error parsing {raw_document.source}: {e}")
            raise
