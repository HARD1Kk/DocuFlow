from pathlib import Path
from typing import List

from docuflow.core.ingestion import CONVERTERS
from docuflow.interfaces import ILoader
from docuflow.schemas import RawDocument
from docuflow.utils import get_logger


class DocumentLoader(ILoader):
    def __init__(self):
        self.logger = get_logger(__name__)

    """
    Just extracts text from docs.
    Handles: PDF, DOCX, TXT, MD
    """

    SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".txt", ".md"]

    def validate(self, source_path: str) -> bool:
        """Verify file exists and is supported"""
        path = Path(source_path)
        return path.exists() and path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    def load(self, source_path: str) -> List[RawDocument]:
        """Load document using appropriate converter"""

        if not self.validate(source_path):
            self.logger.warning(f"Invalid document: {source_path}")
            return []

        try:
            suffix = Path(source_path).suffix.lower()

            # Get converter from mapping
            converter = CONVERTERS.get(suffix)
            if not converter:
                self.logger.error(f"No converter for {suffix}")
                return []

            # Convert
            content = converter(Path(source_path))

            return [
                RawDocument(
                    content=content,
                    source=source_path,
                    metadata={
                        "filename": Path(source_path).name,
                        "file_size": Path(source_path).stat().st_size,
                        "format": suffix,
                    },
                )
            ]
        except Exception as e:
            self.logger.error(f"Error loading {source_path}: {e}")
            return []
