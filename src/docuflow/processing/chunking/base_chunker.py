# src/docuflow/processing/chunking/base_chunker.py
"""Abstract base class for all chunkers - follows Open/Closed Principle."""

from abc import ABC, abstractmethod
from typing import Dict, List

from docuflow.schemas.chunk import Chunk, ChunkBatch, ChunkingConfig, ContentType, DocumentType


class BaseChunker(ABC):
    """
    Abstract base for document-type specific chunkers.

    Single Responsibility: Each chunker handles one document type.
    Open/Closed: Open for extension (new chunkers), closed for modification.
    """

    def __init__(self, config: ChunkingConfig | None = None):
        self.config = config or ChunkingConfig()

    @property
    @abstractmethod
    def supported_document_types(self) -> List[DocumentType]:
        """Return list of document types this chunker supports."""
        pass

    @abstractmethod
    def chunk(self, content: str, metadata: Dict[str, any]) -> ChunkBatch:
        """
        Chunk content into semantically meaningful units.

        Args:
            content: The document content (already converted to text)
            metadata: Document-level metadata (source, original format, etc.)

        Returns:
            ChunkBatch with all chunks and document info
        """
        pass

    def _create_chunk(
        self,
        chunk_id: str,
        content: str,
        content_type: str | ContentType = "text",
        metadata: Dict[str, any] | None = None,
        token_count: int | None = None,
    ) -> Chunk:
        """Helper to create a chunk with consistent token counting."""
        if token_count is None:
            token_count = self._count_tokens(content)

        if isinstance(content_type, str):
            try:
                content_type = ContentType(content_type)
            except ValueError:
                content_type = ContentType.TEXT

        return Chunk(
            chunk_id=chunk_id,
            content=content,
            content_type=content_type,
            metadata=metadata or {},
            token_count=token_count,
        )

    def _count_tokens(self, text: str) -> int:
        """Approximate token count (4 chars per token average)."""
        if not text:
            return 0
        return max(1, len(text) // 4)

    def _generate_chunk_id(self, source: str, index: int) -> str:
        """Generate unique chunk ID."""
        import hashlib

        source_hash = hashlib.md5(source.encode()).hexdigest()[:8]
        return f"{source_hash}_{index:04d}"
