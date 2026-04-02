# src/docuflow/core/chunking/__init__.py
"""
Chunking module - Structure-aware chunking for all document types.

Provides:
- ChunkingEngine: Main orchestrator for chunking
- BaseChunker: Abstract base for custom chunkers
- Document-type specific chunkers (Markdown, Spreadsheet, Image)
- MetadataEnricher: Adds summaries, keywords, hypothetical questions
- Structure detectors: Heading, Table, List, Code block detection
"""

from docuflow.core.chunking.base_chunker import BaseChunker
from docuflow.core.chunking.chunking_engine import ChunkingEngine
from docuflow.core.chunking.code_chunker import CodeChunker
from docuflow.core.chunking.detectors import (
    CodeBlockDetector,
    DetectedElement,
    Heading,
    HeadingDetector,
    ListBlock,
    ListDetector,
    StructureDetector,
    Table,
    TableDetector,
)
from docuflow.core.chunking.image_chunker import ImageChunker
from docuflow.core.chunking.markdown_chunker import MarkdownChunker
from docuflow.core.chunking.metadata_enricher import MetadataEnricher
from docuflow.core.chunking.spreadsheet_chunker import SpreadsheetChunker
from docuflow.schemas.chunk import Chunk, ChunkBatch, ChunkingConfig, ContentType, DocumentType

__all__ = [
    # Main engine
    "ChunkingEngine",
    # Base class for custom chunkers
    "BaseChunker",
    # Document-type specific chunkers
    "MarkdownChunker",
    "SpreadsheetChunker",
    "ImageChunker",
    "CodeChunker",
    # Metadata enrichment
    "MetadataEnricher",
    # Schemas
    "Chunk",
    "ChunkBatch",
    "ChunkingConfig",
    "ContentType",
    "DocumentType",
    # Structure detectors
    "StructureDetector",
    "HeadingDetector",
    "TableDetector",
    "ListDetector",
    "CodeBlockDetector",
    "DetectedElement",
    "Heading",
    "Table",
    "ListBlock",
]
