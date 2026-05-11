from abc import ABC, abstractmethod

from docuflow.schemas import RawDocument


class BaseConverter(ABC):
    """Base contract for file converters."""

    SUPPORTED_EXTENSIONS: tuple[str, ...] = ()

    @abstractmethod
    def convert(self, raw_document: RawDocument) -> str:
        """Convert a raw document to normalized text or markdown."""
