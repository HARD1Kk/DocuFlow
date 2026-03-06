from dataclasses import dataclass


@dataclass
class RawDocument:
    """
    Raw document from loaders - minimal structure.
    Output of data source layer (loaders).
    Input to data processing layer.
    """

    content: str  # Raw extracted text
    source: str  # File path
    metadata: dict  # File metadata
