# src/docuflow/processing/chunking/chunking_engine.py
"""
Unified Chunking Engine - Main orchestrator for all document types.

Design Principles (SOLID):
- Single Responsibility: Each chunker handles one document type
- Open/Closed: Easy to add new chunkers without modifying existing code
- Liskov Substitution: All chunkers implement BaseChunker interface
- Interface Segregation: Minimal, focused interfaces
- Dependency Inversion: Depends on abstractions, not concrete implementations
"""

import time
from typing import Dict, List, Optional

from docuflow.processing.chunking.base_chunker import BaseChunker
from docuflow.processing.chunking.code_chunker import CodeChunker
from docuflow.processing.chunking.image_chunker import ImageChunker
from docuflow.processing.chunking.markdown_chunker import MarkdownChunker
from docuflow.processing.chunking.metadata_enricher import MetadataEnricher
from docuflow.processing.chunking.spreadsheet_chunker import SpreadsheetChunker
from docuflow.schemas.chunk import ChunkBatch, ChunkingConfig, DocumentType
from docuflow.schemas.document_context import DocumentContext
from docuflow.utils import get_logger, log_context

logger = get_logger(__name__)


class ChunkingEngine:
    """
    Main orchestrator for document chunking.

    Responsibilities:
    - Route content to appropriate chunker based on document type
    - Apply metadata enrichment after chunking
    - Provide unified interface regardless of document type
    - Handle errors gracefully with informative messages
    """

    def __init__(
        self,
        config: Optional[ChunkingConfig] = None,
        llm_service=None,
        enable_enrichment: bool = True,
    ):
        """
        Initialize the chunking engine.

        Args:
            config: Chunking configuration (uses defaults if None)
            llm_service: Optional LLM service for metadata enrichment
            enable_enrichment: Whether to enrich chunks with metadata
        """
        self.config = config or ChunkingConfig()
        self.llm_service = llm_service
        self.enable_enrichment = enable_enrichment

        self.logger = get_logger(self.__class__.__name__)

        # Initialize chunkers registry
        self._chunkers: Dict[DocumentType, BaseChunker] = {}
        self._register_builtin_chunkers()

        # Initialize metadata enricher
        self.enricher = MetadataEnricher(
            config=self.config if enable_enrichment else None,
            llm_service=llm_service,
        )

    def _register_builtin_chunkers(self) -> None:
        """Register all built-in chunkers."""
        chunkers: List[BaseChunker] = [
            MarkdownChunker(self.config),
            SpreadsheetChunker(self.config),
            ImageChunker(self.config),
            CodeChunker(self.config),
        ]

        for chunker in chunkers:
            for doc_type in chunker.supported_document_types:
                self._chunkers[doc_type] = chunker
                self.logger.debug(f"Registered chunker for {doc_type.value}")

    def register_chunker(self, chunker: BaseChunker) -> None:
        """
        Register a custom chunker.

        Allows extension without modifying engine code (Open/Closed Principle).

        Args:
            chunker: Chunker instance to register
        """
        for doc_type in chunker.supported_document_types:
            self._chunkers[doc_type] = chunker
            self.logger.info(f"Registered custom chunker for {doc_type.value}")

    def chunk(
        self,
        content: str,
        document_type: DocumentType,
        metadata: Optional[Dict[str, any]] = None,
    ) -> ChunkBatch:
        """
        Chunk document content.

        Args:
            content: The document content (already converted to text)
            document_type: Type of source document
            metadata: Optional document-level metadata

        Returns:
            ChunkBatch with all chunks and processing info

        Raises:
            ValueError: If document type is not supported
        """
        metadata = metadata or {}
        source = metadata.get("source", "unknown")
        doc_id = metadata.get("document_id") or DocumentContext.generate_document_id(content=content, source_path=source)

        with log_context(document_id=doc_id, stage="Chunking"):
            self.logger.info(f"Starting chunking for {source} ({document_type.value})")

            # Validate input
            if not content or not content.strip():
                self.logger.warning("Empty content provided")
                return ChunkBatch(
                    source=source,
                    format=document_type,
                    total_pages=metadata.get("total_pages", 0),
                    total_tokens=0,
                    chunks=[],
                    processing_errors=["Empty content provided"],
                )

            # Get appropriate chunker
            chunker = self._get_chunker(document_type)

            if not chunker:
                self.logger.error(f"No chunker registered for {document_type.value}")
                return ChunkBatch(
                    source=source,
                    format=document_type,
                    total_pages=metadata.get("total_pages", 0),
                    total_tokens=0,
                    chunks=[],
                    processing_errors=[f"No chunker available for document type: {document_type.value}"],
                )

            # Chunk the content
            start_time = time.perf_counter()
            try:
                batch = chunker.chunk(content, metadata)
                batch.format = document_type

                # Build document context from content and metadata
                doc_ctx = DocumentContext.from_source(
                    source_path=source,
                    document_type=document_type,
                    total_pages=metadata.get("total_pages", 1),
                    content=content,
                    parser=metadata.get("parser", ""),
                    parser_version=metadata.get("parser_version", ""),
                )
                if metadata.get("document_id"):
                    doc_ctx.document_id = metadata["document_id"]

                # Stamp every chunk with document-level provenance
                for idx, chunk in enumerate(batch.chunks):
                    chunk.document_type = document_type
                    chunk.document_id = doc_ctx.document_id
                    chunk.document_name = doc_ctx.document_name
                    chunk.source_path = doc_ctx.source_path
                    chunk.chunk_index = idx
                    chunk.parser = doc_ctx.parser
                    chunk.parser_version = doc_ctx.parser_version
                    chunk.chunk_id = f"{doc_ctx.document_id[:8]}_{idx:04d}"
            except Exception as e:
                self.logger.error(f"Chunking failed for {source}: {e}", exc_info=True)
                return ChunkBatch(
                    source=source,
                    format=document_type,
                    total_pages=metadata.get("total_pages", 0),
                    total_tokens=0,
                    chunks=[],
                    processing_errors=[f"Chunking error: {str(e)}"],
                )

            chunking_latency = (time.perf_counter() - start_time) * 1000

            # Enrich chunks with metadata
            if self.enable_enrichment and batch.chunks:
                self.logger.info(f"Enriching {len(batch.chunks)} chunks with metadata")
                batch.chunks = self.enricher.enrich(batch.chunks)

            # Calculate chunk size stats (tokens)
            if batch.chunks:
                sizes = [c.token_count for c in batch.chunks]
                min_size = min(sizes)
                max_size = max(sizes)
                avg_size = sum(sizes) / len(sizes)
                self.logger.info(
                    f"Chunk statistics: min_size={min_size} tokens, max_size={max_size} tokens, avg_size={avg_size:.1f} tokens",
                    extra={"chunk_count": len(batch.chunks)},
                )

            # Log summary
            self.logger.info(
                f"Chunking complete: {len(batch.chunks)} chunks, "
                f"{batch.total_tokens} tokens, "
                f"{len(batch.processing_errors)} errors",
                extra={
                    "latency_ms": chunking_latency,
                    "chunk_count": len(batch.chunks),
                    "output_tokens": batch.total_tokens,
                },
            )

            return batch

    def _get_chunker(self, document_type: DocumentType) -> Optional[BaseChunker]:
        """Get appropriate chunker for document type."""
        return self._chunkers.get(document_type)

    def get_supported_types(self) -> List[DocumentType]:
        """Return list of supported document types."""
        return list(self._chunkers.keys())

    def chunk_multiple(
        self,
        documents: List[Dict[str, any]],
    ) -> List[ChunkBatch]:
        """
        Chunk multiple documents.

        Args:
            documents: List of dicts with keys: content, document_type, metadata

        Returns:
            List of ChunkBatch results
        """
        self.logger.info(f"Chunking {len(documents)} documents")

        results = []
        for doc in documents:
            batch = self.chunk(
                content=doc.get("content", ""),
                document_type=doc.get("document_type", DocumentType.UNKNOWN),
                metadata=doc.get("metadata", {}),
            )
            results.append(batch)

        # Summary
        total_chunks = sum(len(b.chunks) for b in results)
        total_errors = sum(len(b.processing_errors) for b in results)

        self.logger.info(f"Batch chunking complete: {total_chunks} chunks, {total_errors} errors")

        return results
