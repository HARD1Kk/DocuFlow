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
    clean_heading_title,
)
from docuflow.schemas.chunk import Chunk, ChunkBatch, ChunkingConfig, ContentType, DocumentType
from docuflow.utils import get_logger


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
        self.logger = get_logger(__name__)
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
                full_content=content,
                section=section,
                headings=headings,
                tables=tables,
                lists=lists,
                code_blocks=code_blocks,
                chunk_index=chunk_index,
            )
            # Merge small chunks under the same section/heading
            section_chunks = self._merge_small_chunks(section_chunks)

            # Re-generate chunk IDs with correct sequential index
            for idx, chunk in enumerate(section_chunks):
                chunk.chunk_id = self._generate_chunk_id(section["title"], chunk_index + idx)

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
                clean_title = clean_heading_title(heading.title)

                sections.append(
                    {
                        "title": clean_title,
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
        full_content: str,
        section: Dict[str, any],
        headings: List[Heading],
        tables: List[Table],
        lists: List[ListBlock],
        code_blocks: List[DetectedElement],
        chunk_index: int,
    ) -> List[Chunk]:
        """Chunk a single section respecting structure."""
        section_start = section["start"]
        section_end = section["end"]
        chunks: List[Chunk] = []

        # Check if section contains protected elements (table, list, code)
        protected = self._find_protected_elements(section_start, section_end, tables, lists, code_blocks)

        if protected:
            # Section contains protected elements - handle specially
            chunks.extend(
                self._chunk_with_protected_elements(
                    full_content=full_content,
                    protected=protected,
                    section=section,
                    chunk_index=chunk_index,
                )
            )
        else:
            # Regular text - split by size with overlap
            section_content = full_content[section_start:section_end]
            chunks.extend(
                self._chunk_regular_text(
                    content=section_content,
                    section=section,
                    chunk_index=chunk_index,
                )
            )

        return chunks

    def _find_protected_elements(
        self,
        section_start: int,
        section_end: int,
        tables: List[Table],
        lists: List[ListBlock],
        code_blocks: List[DetectedElement],
    ) -> List[Dict[str, any]]:
        """Find protected elements within section boundaries (using global indices)."""
        protected = []

        for table in tables:
            if section_start <= table.start < section_end:
                protected.append({"type": ContentType.TABLE, "element": table, "start": table.start, "end": table.end})

        for list_block in lists:
            if section_start <= list_block.start < section_end:
                protected.append(
                    {"type": ContentType.LIST, "element": list_block, "start": list_block.start, "end": list_block.end}
                )

        for code in code_blocks:
            if section_start <= code.start < section_end:
                protected.append({"type": ContentType.CODE, "element": code, "start": code.start, "end": code.end})

        # Sort by start position
        protected.sort(key=lambda x: x["start"])
        return protected

    def _chunk_with_protected_elements(
        self,
        full_content: str,
        protected: List[Dict[str, any]],
        section: Dict[str, any],
        chunk_index: int,
    ) -> List[Chunk]:
        """Chunk content while keeping protected elements intact."""
        chunks = []
        pos = section["start"]
        local_index = 0

        for element in protected:
            # Chunk text before protected element
            if element["start"] > pos:
                text_before = full_content[pos : element["start"]]
                text_chunks = self._chunk_regular_text(
                    content=text_before,
                    section=section,
                    chunk_index=chunk_index + local_index,
                )
                chunks.extend(text_chunks)
                local_index += len(text_chunks)

            # Add protected element as its own chunk
            element_content = full_content[element["start"] : element["end"]]
            chunk = self._create_chunk(
                chunk_id=self._generate_chunk_id(section["title"], chunk_index + local_index),
                content=element_content,
                content_type=element["type"].value,
                metadata={
                    "element_type": element["type"].value,
                },
                heading=section["title"],
                heading_level=section["level"],
            )
            chunks.append(chunk)
            local_index += 1

            pos = element["end"]

        # Handle remaining text after last protected element
        if pos < section["end"]:
            text_after = full_content[pos : section["end"]]
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
                metadata={},
                heading=section["title"],
                heading_level=section["level"],
            )
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
                metadata={},
                heading=section["title"],
                heading_level=section["level"],
            )
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
                split_points.append((current_start, pos))

                # Start new chunk with overlap
                overlap_start = max(0, pos - 200)  # ~50 tokens overlap
                current_start = overlap_start
                current_tokens = self._count_tokens(content[overlap_start:pos])

            current_tokens += para_tokens
            pos += len(para) + 2  # +2 for \n\n

        # Add final chunk
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
                    metadata={},
                    heading=section["title"],
                    heading_level=section["level"],
                )
                chunks.append(chunk)
                i += 1

            pos = end

        return chunks

    def _merge_small_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
        """Merge chunks that are smaller than min_chunk_size with their neighbors."""
        if not chunks:
            return []

        merged_chunks: List[Chunk] = []

        for chunk in chunks:
            if not merged_chunks:
                merged_chunks.append(chunk)
                continue

            last_chunk = merged_chunks[-1]

            # If either the last chunk or the current chunk is smaller than min_chunk_size,
            # and their combined size doesn't exceed max_chunk_size, merge them.
            if last_chunk.token_count < self.config.min_chunk_size or chunk.token_count < self.config.min_chunk_size:
                combined_content = last_chunk.content + "\n\n" + chunk.content
                combined_tokens = self._count_tokens(combined_content)

                if combined_tokens <= self.config.max_chunk_size:
                    # Update last chunk with combined content and tokens
                    last_chunk.content = combined_content
                    last_chunk.token_count = combined_tokens
                    # If they are different content types, generalize to 'text'
                    if last_chunk.content_type != chunk.content_type:
                        last_chunk.content_type = ContentType.TEXT.value
                    continue

            merged_chunks.append(chunk)

        # If the last chunk is still too small, and we have at least two chunks,
        # try merging it with the previous one even if the previous one wasn't small,
        # as long as they fit in max_chunk_size.
        if len(merged_chunks) > 1:
            last_chunk = merged_chunks[-1]
            if last_chunk.token_count < self.config.min_chunk_size:
                prev_chunk = merged_chunks[-2]
                combined_content = prev_chunk.content + "\n\n" + last_chunk.content
                combined_tokens = self._count_tokens(combined_content)
                if combined_tokens <= self.config.max_chunk_size:
                    prev_chunk.content = combined_content
                    prev_chunk.token_count = combined_tokens
                    if prev_chunk.content_type != last_chunk.content_type:
                        prev_chunk.content_type = ContentType.TEXT.value
                    merged_chunks.pop()

        return merged_chunks
