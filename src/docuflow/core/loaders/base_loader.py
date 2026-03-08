
from pathlib import Path
from typing import List

from docuflow.interfaces import ILoader
from docuflow.schemas import RawDocument
from docuflow.utils import get_logger


class BaseLoader(ILoader):
    """
    Base loader with common implementation.
    Subclasses only need to define SUPPORTED_EXTENSIONS.
    """

    SUPPORTED_EXTENSIONS: List[str] = []

    def __init__(self):
        self.logger = get_logger(__name__)

    def validate(self, source_path: str) -> bool:
        """Verify file exists and is supported"""
        path = Path(source_path)
        return path.exists() and path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    def load(self, source_path: str) -> List[RawDocument]:
        """Load file as raw bytes - same for all formats"""
        
        if not self.validate(source_path):
            self.logger.warning(f"Invalid file: {source_path}")
            return []

        try:
            path = Path(source_path)
            
            # Load raw bytes
            raw_content = path.read_bytes()
            
            return [
                RawDocument(
                    content=raw_content,
                    source=source_path,
                    metadata={
                        "filename": path.name,
                        "file_size": path.stat().st_size,
                        "format": path.suffix.lower(),
                    },
                )
            ]
        except Exception as e:
            self.logger.error(f"Error loading {source_path}: {e}")
            return []