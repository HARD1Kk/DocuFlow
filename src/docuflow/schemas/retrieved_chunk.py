from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class RetrievedChunk:
    content: str
    score: float
    metadata: Dict[str, Any]
