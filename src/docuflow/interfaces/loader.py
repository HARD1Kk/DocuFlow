from abc import ABC, abstractmethod
from typing import List

from docuflow.schemas import RawDocument


class ILoader(ABC):
    """
    DATA SOURCE LAYER - Extraction only.

    Responsibility: Load files and extract raw content.
    """

    SUPPORTED_EXTENSIONS: List[str] = []

    @abstractmethod
    def validate(self, source_path: str) -> bool:
        """
        Verify source is valid and accessible.

        Args:
            source_path: Path to file

        Returns:
            True if file exists and is supported format
        """
        pass

    @abstractmethod
    def load(self, source_path: str) -> List[RawDocument]:
        """
        Load and extract raw content from source.

        Args:
            source_path: Path to file

        Returns:
            List of RawDocument with extracted content
        """
        pass
