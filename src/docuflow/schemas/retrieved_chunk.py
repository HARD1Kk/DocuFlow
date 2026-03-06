from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class RetrievedChunk:
    content: str
    score: float
    metadata: Dict[str, Any]
