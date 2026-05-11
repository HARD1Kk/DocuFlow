# src/docuflow/schemas/chunk.py
"""Chunk schemas with rich metadata for production RAG."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ContentType(str, Enum):
    """Type of content in chunk."""

    TEXT = "text"
    TABLE = "table"
    LIST = "list"
    CODE = "code"
    IMAGE = "image"
    HEADING = "heading"
    MIXED = "mixed"


class DocumentType(str, Enum):
    """Source document type."""

    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"
    IMAGE = "image"
    SPREADSHEET = "spreadsheet"
    CODE = "code"
    UNKNOWN = "unknown"


@dataclass
class Chunk:
    """
    Single chunk with rich metadata for production RAG.

    Per rag.md requirements:
    - Structure-aware chunking (headings, tables, lists stay intact)
    - Rich metadata (summary, keywords, hypothetical questions)
    - Content type tracking for specialized retrieval
    """

    chunk_id: str
    content: str
    content_type: ContentType = ContentType.TEXT
    document_type: DocumentType = DocumentType.UNKNOWN

    # Structural metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Rich metadata for better retrieval (rag.md Section 6.3)
    summary: Optional[str] = None  # Brief summary of chunk
    keywords: List[str] = field(default_factory=list)  # Extracted keywords
    hypothetical_questions: List[str] = field(default_factory=list)  # Questions this chunk answers

    # Embedding (computed later)
    embedding: Optional[List[float]] = None

    # Token tracking
    token_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for vector store."""
        return {
            "chunk_id": self.chunk_id,
            "content": self.content,
            "content_type": self.content_type.value,
            "document_type": self.document_type.value,
            "metadata": self.metadata,
            "summary": self.summary,
            "keywords": self.keywords,
            "hypothetical_questions": self.hypothetical_questions,
            "token_count": self.token_count,
        }


@dataclass
class ChunkBatch:
    """Collection of chunks from one document."""

    source: str
    format: DocumentType
    total_pages: int
    total_tokens: int
    chunks: List[Chunk] = field(default_factory=list)
    processing_errors: List[str] = field(default_factory=list)

    def add_chunk(self, chunk: Chunk) -> None:
        """Add chunk and update totals."""
        self.chunks.append(chunk)
        self.total_tokens += chunk.token_count

    def to_dicts(self) -> List[Dict[str, Any]]:
        """Convert all chunks to dictionaries."""
        return [chunk.to_dict() for chunk in self.chunks]


@dataclass
class ChunkingConfig:
    """Configuration for chunking behavior."""

    # Size constraints (in tokens)
    max_chunk_size: int = 512
    min_chunk_size: int = 50
    overlap_tokens: int = 50

    # Boundary preferences
    preferred_boundary_distance: int = 20  # chars

    # Weights for constraint balancing
    size_weight: float = 0.4
    heading_weight: float = 0.3
    table_weight: float = 0.3

    # Feature toggles
    enable_metadata_enrichment: bool = True
    preserve_tables: bool = True
    preserve_lists: bool = True
    preserve_code_blocks: bool = True
