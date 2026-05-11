from abc import ABC, abstractmethod
from typing import List

from docuflow.schemas import RawDocument


class IParser(ABC):
    """
    PARSER LAYER - Parsing raw content into structured documents.
    """

    @abstractmethod
    def parse(self, raw_documents: List[RawDocument]) -> List[RawDocument]:
        """
        Parse raw content into structured documents.

        Args:
            raw_documents: List of RawDocument to parse

        Returns:
            List of parsed RawDocument
        """
        pass
