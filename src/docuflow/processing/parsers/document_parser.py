from docuflow.processing.converters import ConverterFactory
from docuflow.schemas import RawDocument
from docuflow.utils import get_logger


class DocumentParser:
    def __init__(self, converter_provider: object | None = None) -> None:
        """Parser that extracts text using a converter provider.

        Args:
            converter_provider: object with `get_converter(source_path)` method.
                Defaults to `ConverterFactory`.
        """
        self.logger = get_logger(__name__)
        self.converter_provider = converter_provider or ConverterFactory

    def parse(self, raw_document: RawDocument) -> str:
        """Extract text from document formats using the converter layer."""
        file_format = raw_document.metadata.get("format", "").lower()

        try:
            self.logger.info(f"Parsing {raw_document.source} ({file_format})")
            converter = self.converter_provider.get_converter(raw_document.source)
            self.logger.info(f"Using converter: {converter.__class__.__name__}")
            result = converter.convert(raw_document)

            if result is None:
                self.logger.error(f"Conversion returned None for {file_format}")
                raise RuntimeError("Conversion failed: None returned")

            self.logger.info(f"Successfully parsed: {len(result)} chars")
            return result

        except Exception as e:
            self.logger.error(f"Error parsing {raw_document.source}: {e}", exc_info=True)
            raise
