"""Tests for chunk metadata propagation, DocumentContext, plain-text headings, and logging context.

Verifies that:
1. DocumentContext generates deterministic content-based IDs (stable across file renames).
2. Headings are cleaned to plain text (stripping Markdown bold/italics/code syntax).
3. Parser and parser_version metadata are stored and propagated.
4. Duplicate metadata keys (like section/section_level) are eliminated.
5. Structured logging propagates document_id for end-to-end observability.
"""

import logging
from docuflow.processing.chunking.chunking_engine import ChunkingEngine
from docuflow.processing.chunking.detectors import clean_heading_title
from docuflow.schemas.chunk import Chunk, ChunkingConfig, DocumentType
from docuflow.schemas.document_context import DocumentContext
from docuflow.utils import get_logger, log_context
from docuflow.utils.logger import document_id_var


# ---------------------------------------------------------------------------
# 1. Plain text headings & cleaning
# ---------------------------------------------------------------------------

class TestPlainTextHeadings:
    """Headings are stored in metadata as plain text without Markdown syntax."""

    def test_clean_heading_title_bold_and_italics(self):
        """Markdown bold and italic syntax should be stripped."""
        assert clean_heading_title("**Introduction**") == "Introduction"
        assert clean_heading_title("*Methods*") == "Methods"
        assert clean_heading_title("__Results__") == "Results"
        assert clean_heading_title("_Conclusion_") == "Conclusion"
        assert clean_heading_title("`Code Section`") == "Code Section"

    def test_clean_heading_title_numbered_and_mixed(self):
        """Complex headings with numbers and bold markers should be cleaned."""
        assert clean_heading_title("**1.** Objectives") == "1. Objectives"
        assert (
            clean_heading_title("**Innovative Tech Solutions, Inc. Product Launch Report: SmartHome Hub**")
            == "Innovative Tech Solutions, Inc. Product Launch Report: SmartHome Hub"
        )

    def test_chunking_engine_stores_plain_text_headings(self):
        """ChunkingEngine produces chunks with clean plain text headings."""
        config = ChunkingConfig()
        engine = ChunkingEngine(config=config, enable_enrichment=False)

        content = (
            "# **Introduction**\n\n"
            "This is a detailed introduction paragraph designed to test plain text heading extraction.\n\n"
            "## **Key Features**\n\n"
            "These are the key features described in detail to satisfy minimum chunk token bounds."
        )

        batch = engine.chunk(content=content, document_type=DocumentType.MD, metadata={"source": "doc.md"})

        headings = [c.heading for c in batch.chunks]
        assert "Introduction" in headings
        assert "Key Features" in headings
        for h in headings:
            assert "**" not in h, f"Heading '{h}' still contains markdown bold syntax"


# ---------------------------------------------------------------------------
# 2. Content-derived Document ID & Determinism
# ---------------------------------------------------------------------------

class TestDocumentContextDeterminism:
    """DocumentContext deterministic ID generation based on document content."""

    def test_generate_document_id_from_content(self):
        """Identical content produces identical document_id regardless of source_path."""
        content1 = b"PDF raw bytes data content for testing SHA256"
        id1 = DocumentContext.generate_document_id(content=content1, source_path="folder/file_a.pdf")
        id2 = DocumentContext.generate_document_id(content=content1, source_path="different/path/file_b.pdf")
        assert id1 == id2, "Renaming or moving file should retain same document_id for identical content"
        assert len(id1) == 16

    def test_generate_document_id_different_content(self):
        """Different content produces different IDs."""
        id1 = DocumentContext.generate_document_id(content="Content A")
        id2 = DocumentContext.generate_document_id(content="Content B")
        assert id1 != id2

    def test_from_source_factory_with_parser(self):
        """from_source populates parser and parser_version correctly."""
        ctx = DocumentContext.from_source(
            source_path="data/input/sample.pdf",
            document_type=DocumentType.PDF,
            content="sample content text",
            parser="pymupdf4llm",
            parser_version="1.27.2",
        )
        assert ctx.document_name == "sample.pdf"
        assert ctx.parser == "pymupdf4llm"
        assert ctx.parser_version == "1.27.2"
        assert len(ctx.document_id) == 16


# ---------------------------------------------------------------------------
# 3. Parser & Version Metadata Propagation & Deduplication
# ---------------------------------------------------------------------------

class TestMetadataPropagationAndDeduplication:
    """Parser info and deduplication in chunks."""

    def test_parser_metadata_on_chunk_and_to_dict(self):
        """parser and parser_version flow into Chunk and to_dict()."""
        config = ChunkingConfig()
        engine = ChunkingEngine(config=config, enable_enrichment=False)

        content = "# Section\n\nDetailed content for testing metadata propagation."
        batch = engine.chunk(
            content=content,
            document_type=DocumentType.MD,
            metadata={
                "source": "test.md",
                "parser": "pymupdf4llm",
                "parser_version": "1.27.2",
            },
        )

        assert len(batch.chunks) > 0
        chunk = batch.chunks[0]
        assert chunk.parser == "pymupdf4llm"
        assert chunk.parser_version == "1.27.2"

        d = chunk.to_dict()
        assert d["parser"] == "pymupdf4llm"
        assert d["parser_version"] == "1.27.2"

    def test_deduplicated_chunk_metadata(self):
        """Redundant 'section' and 'section_level' are not duplicated in chunk.metadata."""
        config = ChunkingConfig()
        engine = ChunkingEngine(config=config, enable_enrichment=False)

        content = "# Overview\n\nContent paragraph with details."
        batch = engine.chunk(content=content, document_type=DocumentType.MD, metadata={"source": "test.md"})

        for chunk in batch.chunks:
            # Single source of truth is chunk.heading & chunk.heading_level
            assert chunk.heading == "Overview"
            assert chunk.heading_level == 1
            assert "section" not in chunk.metadata, "section should not be duplicated inside metadata dict"
            assert "section_level" not in chunk.metadata, "section_level should not be duplicated inside metadata dict"

    def test_omit_metadata_key_when_empty(self):
        """to_dict() omits 'metadata' key when empty, but includes it when populated."""
        chunk_empty = Chunk(chunk_id="c1", content="text", metadata={})
        d_empty = chunk_empty.to_dict()
        assert "metadata" not in d_empty, "'metadata' key should be omitted when empty"

        chunk_with_meta = Chunk(chunk_id="c2", content="table", metadata={"element_type": "table", "rows": 5})
        d_with_meta = chunk_with_meta.to_dict()
        assert "metadata" in d_with_meta, "'metadata' key should be present when populated"
        assert d_with_meta["metadata"] == {"element_type": "table", "rows": 5}


# ---------------------------------------------------------------------------
# 4. Structured Logging Context
# ---------------------------------------------------------------------------

class TestStructuredLoggingTraceability:
    """document_id context variable propagation for structured logging."""

    def test_log_context_sets_document_id_var(self):
        """log_context binds document_id to contextvar during block execution."""
        test_id = "deadbeef12345678"
        assert document_id_var.get("") == ""

        with log_context(document_id=test_id, stage="Ingestion"):
            assert document_id_var.get("") == test_id

        assert document_id_var.get("") == ""

    def test_log_context_nesting(self):
        """Nested log_context preserves document_id across inner stage updates."""
        test_id = "31d52cad8f5be081"

        with log_context(document_id=test_id, stage="Ingestion"):
            assert document_id_var.get("") == test_id
            with log_context(stage="Chunking"):
                assert document_id_var.get("") == test_id
            assert document_id_var.get("") == test_id


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "--tb=short"])
