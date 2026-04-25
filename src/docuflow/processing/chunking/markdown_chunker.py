# src/docuflow/processing/chunking/markdown_chunker.py
"""Structure-aware chunker for markdown content (PDF, DOCX, TXT, MD)."""

import re
from typing import Dict, List

from docuflow.processing.chunking.base_chunker import BaseChunker
from docuflow.processing.chunking.detectors import (
    CodeBlockDetector,
    DetectedElement,
    Heading,
    HeadingDetector,
    ListBlock,
    ListDetector,
    Table,
    TableDetector,
)
from docuflow.schemas.chunk import Chunk, ChunkBatch, ChunkingConfig, ContentType, DocumentType


class MarkdownChunker(BaseChunker):
    """
    Structure-aware chunker for markdown content.

    Respects:
    - Heading boundaries (chunks don't cross heading boundaries)
    - Table integrity (tables stay intact)
    - List integrity (lists stay intact)
    - Code block integrity (code blocks not split)
    """

    @property
    def supported_document_types(self) -> List[DocumentType]:
        return [DocumentType.PDF, DocumentType.DOCX, DocumentType.TXT, DocumentType.MD]

    def __init__(self, config: ChunkingConfig | None = None):
        super().__init__(config)
        self.heading_detector = HeadingDetector()
        self.table_detector = TableDetector()
        self.list_detector = ListDetector()
        self.code_detector = CodeBlockDetector()

    def chunk(self, content: str, metadata: Dict[str, any]) -> ChunkBatch:
        """Chunk markdown content respecting structure."""
        if not content or not content.strip():
            return ChunkBatch(
                source=metadata.get("source", "unknown"),
                format=DocumentType.MD,
                total_pages=metadata.get("total_pages", 1),
                total_tokens=0,
                processing_errors=["Empty content provided"],
            )

        # Detect all structural elements
        headings = self.heading_detector.detect(content)
        tables = self.table_detector.detect(content)
        lists = self.list_detector.detect(content)
        code_blocks = self.code_detector.detect(content)

        # Create sections based on headings
        sections = self._create_sections(content, headings)

        # Chunk each section
        chunks: List[Chunk] = []
        chunk_index = 0

        for section in sections:
            section_chunks = self._chunk_section(
                section=section,
                headings=headings,
                tables=tables,
                lists=lists,
                code_blocks=code_blocks,
                chunk_index=chunk_index,
            )
            chunks.extend(section_chunks)
            chunk_index += len(section_chunks)

        total_tokens = sum(c.token_count for c in chunks)

        return ChunkBatch(
            source=metadata.get("source", "unknown"),
            format=DocumentType.MD,
            total_pages=metadata.get("total_pages", 1),
            total_tokens=total_tokens,
            chunks=chunks,
        )

    def _create_sections(self, content: str, headings: List[Heading]) -> List[Dict[str, any]]:
        """Split content into sections based on headings."""
        sections = []

        if not headings:
            # No headings - treat entire content as one section
            sections.append(
                {
                    "title": "Document",
                    "level": 0,
                    "start": 0,
                    "end": len(content),
                    "content": content,
                }
            )
        else:
            # Create section for each heading
            for i, heading in enumerate(headings):
                next_start = headings[i + 1].start if i + 1 < len(headings) else len(content)

                sections.append(
                    {
                        "title": heading.title,
                        "level": heading.level,
                        "start": heading.start,
                        "end": next_start,
                        "heading": heading,
                    }
                )

            # Extract content for each section
            for section in sections:
                section["content"] = content[section["start"] : section["end"]]

        return sections

    def _chunk_section(
        self,
        section: Dict[str, any],
        headings: List[Heading],
        tables: List[Table],
        lists: List[ListBlock],
        code_blocks: List[DetectedElement],
        chunk_index: int,
    ) -> List[Chunk]:
        """Chunk a single section respecting structure."""
        content = section["content"]
        chunks: List[Chunk] = []

        # Check if section is a protected element (table, list, code)
        protected = self._find_protected_elements(content, tables, lists, code_blocks)

        if protected:
            # Section contains protected elements - handle specially
            chunks.extend(
                self._chunk_with_protected_elements(
                    content=content,
                    protected=protected,
                    section=section,
                    chunk_index=chunk_index,
                )
            )
        else:
            # Regular text - split by size with overlap
            chunks.extend(
                self._chunk_regular_text(
                    content=content,
                    section=section,
                    chunk_index=chunk_index,
                )
            )

        return chunks

    def _find_protected_elements(
        self,
        content: str,
        tables: List[Table],
        lists: List[ListBlock],
        code_blocks: List[DetectedElement],
    ) -> List[Dict[str, any]]:
        """Find protected elements within section content."""
        protected = []

        for table in tables:
            if 0 <= table.start < len(content):
                protected.append({"type": ContentType.TABLE, "element": table, "start": table.start, "end": table.end})

        for list_block in lists:
            if 0 <= list_block.start < len(content):
                protected.append(
                    {"type": ContentType.LIST, "element": list_block, "start": list_block.start, "end": list_block.end}
                )

        for code in code_blocks:
            if 0 <= code.start < len(content):
                protected.append({"type": ContentType.CODE, "element": code, "start": code.start, "end": code.end})

        # Sort by start position
        protected.sort(key=lambda x: x["start"])
        return protected

    def _chunk_with_protected_elements(
        self,
        content: str,
        protected: List[Dict[str, any]],
        section: Dict[str, any],
        chunk_index: int,
    ) -> List[Chunk]:
        """Chunk content while keeping protected elements intact."""
        chunks = []
        pos = 0
        local_index = 0

        for element in protected:
            # Chunk text before protected element
            if element["start"] > pos:
                text_before = content[pos : element["start"]]
                text_chunks = self._chunk_regular_text(
                    content=text_before,
                    section=section,
                    chunk_index=chunk_index + local_index,
                )
                chunks.extend(text_chunks)
                local_index += len(text_chunks)

            # Add protected element as its own chunk
            element_content = content[element["start"] : element["end"]]
            chunk = self._create_chunk(
                chunk_id=self._generate_chunk_id(section["title"], chunk_index + local_index),
                content=element_content,
                content_type=element["type"].value,
                metadata={
                    "section": section["title"],
                    "section_level": section["level"],
                    "element_type": element["type"].value,
                },
            )
            chunks.append(chunk)
            local_index += 1

            pos = element["end"]

        # Handle remaining text after last protected element
        if pos < len(content):
            text_after = content[pos:]
            text_chunks = self._chunk_regular_text(
                content=text_after,
                section=section,
                chunk_index=chunk_index + local_index,
            )
            chunks.extend(text_chunks)

        return chunks

    def _chunk_regular_text(
        self,
        content: str,
        section: Dict[str, any],
        chunk_index: int,
    ) -> List[Chunk]:
        """Split regular text into chunks with size limits and overlap."""
        chunks = []
        tokens = self._count_tokens(content)

        # If content fits in one chunk, done
        if tokens <= self.config.max_chunk_size:
            chunk = self._create_chunk(
                chunk_id=self._generate_chunk_id(section["title"], chunk_index),
                content=content.strip(),
                content_type=ContentType.TEXT.value,
                metadata={
                    "section": section["title"],
                    "section_level": section["level"],
                },
            )
            if chunk.token_count >= self.config.min_chunk_size:
                chunks.append(chunk)
            return chunks

        # Need to split - find natural boundaries
        split_points = self._find_split_points(content)

        if len(split_points) <= 1:
            # No good split points - force split at max size
            return self._force_split(content, section, chunk_index)

        # Create chunks at split points
        for i, (start, end) in enumerate(split_points):
            chunk_content = content[start:end].strip()
            if not chunk_content:
                continue

            chunk = self._create_chunk(
                chunk_id=self._generate_chunk_id(section["title"], chunk_index + i),
                content=chunk_content,
                content_type=ContentType.TEXT.value,
                metadata={
                    "section": section["title"],
                    "section_level": section["level"],
                },
            )

            if chunk.token_count >= self.config.min_chunk_size:
                chunks.append(chunk)

        return chunks

    def _find_split_points(self, content: str) -> List[tuple[int, int]]:
        """Find natural split points (paragraph boundaries)."""
        split_points = []

        # Split by paragraph breaks
        paragraphs = re.split(r"\n\n+", content)
        pos = 0

        current_start = 0
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._count_tokens(para)

            if current_tokens + para_tokens > self.config.max_chunk_size:
                # End current chunk at previous paragraph
                if current_tokens >= self.config.min_chunk_size:
                    split_points.append((current_start, pos))

                # Start new chunk with overlap
                overlap_start = max(0, pos - 200)  # ~50 tokens overlap
                current_start = overlap_start
                current_tokens = self._count_tokens(content[overlap_start:pos])

            current_tokens += para_tokens
            pos += len(para) + 2  # +2 for \n\n

        # Add final chunk
        if current_tokens >= self.config.min_chunk_size:
            split_points.append((current_start, len(content)))

        return split_points if split_points else [(0, len(content))]

    def _force_split(self, content: str, section: Dict[str, any], chunk_index: int) -> List[Chunk]:
        """Force split content at max size boundaries."""
        chunks = []
        pos = 0
        i = 0

        while pos < len(content):
            end = min(pos + self.config.max_chunk_size * 4, len(content))  # 4 chars per token

            # Try to find sentence boundary
            if end < len(content):
                last_period = content.rfind(".", pos, end)
                if last_period > pos:
                    end = last_period + 1

            chunk_content = content[pos:end].strip()
            if chunk_content:
                chunk = self._create_chunk(
                    chunk_id=self._generate_chunk_id(section["title"], chunk_index + i),
                    content=chunk_content,
                    content_type=ContentType.TEXT.value,
                    metadata={
                        "section": section["title"],
                        "section_level": section["level"],
                    },
                )
                chunks.append(chunk)
                i += 1

            pos = end

        return chunks
