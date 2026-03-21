from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class RawDocument:
    """
    Raw document from loaders - minimal structure.
    Output of data source layer (loaders).
    Input to data processing layer.
    """

    content: bytes  # Raw extracted text
    source: str  # File path
    metadata: Dict[str, Any]  # File metadata
