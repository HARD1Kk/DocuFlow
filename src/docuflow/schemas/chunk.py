# src/docuflow/schemas/chunk.py

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ContentType(str, Enum):
    """Type of content in chunk"""

    TEXT = "text"
    TABLE = "table"
    LIST = "list"
    IMAGE = "image"


@dataclass
class Chunk:
    """Single chunk with rich metadata for RAG"""

    chunk_id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    token_count: int = 0
    embedding: Optional[List[float]] = None


@dataclass
class ChunkBatch:
    """Collection of chunks from one document"""

    source: str
    format: str
    total_pages: int
    total_tokens: int
    chunks: List[Chunk] = field(default_factory=list)


@dataclass
class ChunkingConfig:
    """Configuration for chunking"""

    max_chunk_size: int = 512  # tokens
    min_chunk_size: int = 50  # tokens
    overlap_tokens: int = 50  # overlap between chunks
    preferred_boundary_distance: int = 20  # chars

    # Weights for constraint balancing
    size_weight: float = 0.4
    heading_weight: float = 0.3
    table_weight: float = 0.3
