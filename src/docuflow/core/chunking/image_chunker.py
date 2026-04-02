# src/docuflow/core/chunking/image_chunker.py
"""Chunker for OCR-extracted text from images."""

from typing import Dict, List

from docuflow.core.chunking.base_chunker import BaseChunker
from docuflow.schemas.chunk import Chunk, ChunkBatch, ChunkingConfig, ContentType, DocumentType


class ImageChunker(BaseChunker):
    """
    Chunker for OCR-extracted text from images.

    Strategy:
    - OCR text is typically short and unstructured
    - Treat entire OCR output as single chunk if it fits
    - Split by detected line boundaries if too long
    - Add image-specific metadata
    """

    @property
    def supported_document_types(self) -> List[DocumentType]:
        return [DocumentType.IMAGE]

    def chunk(self, content: str, metadata: Dict[str, any]) -> ChunkBatch:
        """Chunk OCR-extracted text from images."""
        if not content or not content.strip():
            return ChunkBatch(
                source=metadata.get("source", "unknown"),
                format=DocumentType.IMAGE,
                total_pages=1,
                total_tokens=0,
                processing_errors=["Empty OCR content"],
            )

        chunks: List[Chunk] = []
        token_count = self._count_tokens(content)

        # Determine chunking strategy based on length
        if token_count <= self.config.max_chunk_size:
            # Entire OCR text fits in one chunk
            chunk = self._create_chunk(
                chunk_id=self._generate_chunk_id(metadata.get("source", "image"), 0),
                content=content.strip(),
                content_type=ContentType.TEXT.value,
                metadata=self._build_metadata(metadata, "full"),
            )
            chunks.append(chunk)
        else:
            # Split by lines (OCR typically has line info)
            chunks = self._chunk_by_lines(content, metadata)

        total_tokens = sum(c.token_count for c in chunks)

        return ChunkBatch(
            source=metadata.get("source", "unknown"),
            format=DocumentType.IMAGE,
            total_pages=1,
            total_tokens=total_tokens,
            chunks=chunks,
        )

    def _chunk_by_lines(self, content: str, metadata: Dict[str, any]) -> List[Chunk]:
        """Chunk OCR text by line groups."""
        chunks = []
        lines = content.split("\n")

        current_group: List[str] = []
        current_tokens = 0
        group_index = 0

        for line in lines:
            line_tokens = self._count_tokens(line)

            if current_tokens + line_tokens > self.config.max_chunk_size and current_group:
                # Emit current group
                chunk_content = "\n".join(current_group)
                chunk = self._create_chunk(
                    chunk_id=self._generate_chunk_id(metadata.get("source", "image"), group_index),
                    content=chunk_content,
                    content_type=ContentType.TEXT.value,
                    metadata=self._build_metadata(metadata, f"lines_{group_index}"),
                )
                chunks.append(chunk)
                group_index += 1
                current_group = []
                current_tokens = 0

            current_group.append(line)
            current_tokens += line_tokens

        # Emit final group
        if current_group:
            chunk_content = "\n".join(current_group)
            chunk = self._create_chunk(
                chunk_id=self._generate_chunk_id(metadata.get("source", "image"), group_index),
                content=chunk_content,
                content_type=ContentType.TEXT.value,
                metadata=self._build_metadata(metadata, f"lines_{group_index}"),
            )
            chunks.append(chunk)

        return chunks

    def _build_metadata(self, base_metadata: Dict[str, any], chunk_type: str) -> Dict[str, any]:
        """Build image-specific metadata."""
        return {
            "source_type": "ocr",
            "image_path": base_metadata.get("source", ""),
            "image_width": base_metadata.get("width"),
            "image_height": base_metadata.get("height"),
            "ocr_engine": base_metadata.get("ocr_engine", "unknown"),
            "chunk_type": chunk_type,
            "confidence": base_metadata.get("confidence"),
        }
