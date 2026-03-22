# Main orchestrator
from typing import Any, Dict, List, Optional, Tuple

from docuflow.core.chunking.detectors import (
    HeadingDetector,
    ListDetector,
    TableDetector,
)
from docuflow.schemas import Chunk, ChunkBatch, ChunkingConfig
from docuflow.utils import get_logger

logger = get_logger(__name__)


class ChunkingEngine:
    """
    Create flat chunks with rich metadata.

    """

    def __init__(self, config: Optional[ChunkingConfig] = None):
        """Initialize with config"""
        self.config = ChunkingConfig()
        self.heading_detector = HeadingDetector()
        self.table_detector = TableDetector()
        self.list_detector = ListDetector()
        self.logger = logger

    def process(
        self, content: str, source: str, format: str, total_pages: int, page_mapping: Optional[Dict[int, int]] = None
    ) -> ChunkBatch:
        """
        Process text and create chunks

        Args:
            content: Clean text
            source: File path
            format: File format
            total_pages: Number of pages
            page_mapping: Position → page mapping

        Returns:
            ChunkBatch with chunks

        Raises:
            ValueError: If content is empty
        """
        # Validate inputs
        if not content or not content.strip():
            raise ValueError("Content cannot be empty")

        if not source or not format:
            raise ValueError("Source and format required")

        self.logger.info(f"Processing {source} ({len(content)} chars)")

        try:
            # Step 1: Detect structure
            detected = self._detect_structure(content)

            # Step 2: Create chunks
            chunks = self._create_chunks_intelligent(content=content, detected=detected, page_mapping=page_mapping)

            # Step 3: Add metadata
            chunks = self._enrich_chunks(chunks=chunks, detected=detected, source=source, format=format)
            self.logger.info(f"Created {len(chunks)} chunks")

            return ChunkBatch(
                source=source,
                format=format,
                total_pages=total_pages,
                total_tokens=self._count_tokens(content),
                chunks=chunks,
            )

        except Exception as e:
            self.logger.error(f"Chunking failed: {e}")
            raise

    def _detect_structure(self, content: str) -> Dict[str, Any]:
        """
        Detect all structure elements

        Returns: Dict with headings, tables, lists, etc.
        """

        self.logger.debug("Detecting structure...")

        return {
            "headings": self.heading_detector.detect(content),
            "tables": self.table_detector.detect(content),
            "lists": self.list_detector.detect(content),
        }

    def _create_chunks_intelligent(
        self, content: str, detected: Dict[str, Any], page_mapping: Optional[Dict[int, int]]
    ) -> List[Chunk]:
        """
        Create chunks using intelligent boundary detection

        Respects:
        - Max size
        - Table boundaries
        - Heading boundaries
        - Natural section breaks
        """

        chunks = []
        pos = 0
        chunk_id = 1

        while pos < len(content):
            # Find best boundary
            boundary = self._find_best_boundary(content=content, start_pos=pos, detected=detected)

            if boundary <= pos:
                # Safety: always move forward
                boundary = self._find_safe_boundary(content, pos)

            # Extract chunk
            chunk_text = content[pos:boundary].strip()

            if chunk_text and self._is_valid_chunk(chunk_text):
                chunk = Chunk(chunk_id=str(chunk_id), content=chunk_text, token_count=self._count_tokens(chunk_text))
                chunks.append(chunk)
                chunk_id += 1

                self.logger.debug(f"Chunk {chunk_id}: {self._count_tokens(chunk_text)} tokens")

            pos = boundary

        return chunks

    def _find_best_boundary(self, content: str, start_pos: int, detected: Dict[str, Any]) -> int:
        """
        Find best boundary considering ALL constraints

        Returns position where chunk should end
        """

        # Collect all candidate boundaries
        candidates: List[Tuple[int, float]] = []  # (position, score)

        # 1. Size constraint (hard limit)
        max_pos = self._get_max_position(content, start_pos)
        candidates.append((max_pos, 1.0))

        # 2. Heading boundaries (prefer these)
        heading_boundaries = self._get_heading_boundaries(content, start_pos, detected["headings"])
        for pos in heading_boundaries:
            candidates.append((pos, 0.9))

        # 3. Table boundaries (must respect)
        table_boundaries = self._get_table_boundaries(content, start_pos, detected["tables"])
        for pos in table_boundaries:
            candidates.append((pos, 0.95))

        # 4. Paragraph boundaries (good place to break)
        para_boundaries = self._get_paragraph_boundaries(content, start_pos)
        for pos in para_boundaries:
            candidates.append((pos, 0.7))

        # Choose best boundary
        if not candidates:
            return len(content)

        # Sort by score, pick best
        candidates.sort(key=lambda x: (-x[1], abs(x[0] - start_pos)))
        best_boundary = candidates[0][0]

        return best_boundary

    def _get_max_position(self, content: str, start_pos: int) -> int:
        """Get max position respecting max chunk size"""

        # Find position that gives us max tokens
        current = start_pos
        while current < len(content):
            tokens = self._count_tokens(content[start_pos:current])
            if tokens >= self.config.max_chunk_size:
                return current
            current += 10  # Step by 10 chars

        return len(content)

    def _get_heading_boundaries(self, content: str, start_pos: int, headings: List[Dict]) -> List[int]:
        """Get positions of heading boundaries"""

        boundaries = []
        for heading in headings:
            if heading["start"] > start_pos:
                boundaries.append(heading["start"])

        return boundaries

    def _get_table_boundaries(self, content: str, start_pos: int, tables: List[Dict]) -> List[int]:
        """Get positions of table boundaries"""

        boundaries = []
        for table in tables:
            # Must end before table starts or after table ends
            if table["start"] > start_pos:
                boundaries.append(table["start"])
            elif table["end"] > start_pos:
                boundaries.append(table["end"])

        return boundaries

    def _get_paragraph_boundaries(self, content: str, start_pos: int) -> List[int]:
        """Get paragraph boundaries (blank lines)"""

        boundaries = []
        pos = start_pos

        while pos < len(content):
            if pos + 1 < len(content) and content[pos : pos + 2] == "\n\n":
                boundaries.append(pos + 2)
            pos += 1

        return boundaries[:5]  # Limit to 5 nearest

    def _find_safe_boundary(self, content: str, pos: int) -> int:
        """Find safe boundary to always make progress"""

        # Just go to next sentence or max size
        next_period = content.find(".", pos)
        if next_period > pos:
            return next_period + 1

        # Fallback: move by config amount
        return min(pos + self.config.max_chunk_size, len(content))

    def _is_valid_chunk(self, text: str) -> bool:
        """Check if chunk is valid"""

        tokens = self._count_tokens(text)
        if tokens < self.config.min_chunk_size:
            return False

        if not text.strip():
            return False

        return True

    def _enrich_chunks(self, chunks: List[Chunk], detected: Dict[str, Any], source: str, format: str) -> List[Chunk]:
        """Add metadata to chunks"""

        for chunk in chunks:
            heading = self._find_heading_for_chunk(chunk.content, detected["headings"])

            content_type = self._detect_content_type(chunk.content, detected)

            chunk.metadata = {
                "source": source,
                "format": format,
                "section": heading.get("title", ""),
                "heading_level": heading.get("level", 0),
                "content_type": content_type,
            }

        return chunks

    def _find_heading_for_chunk(self, content: str, headings: List[Dict]) -> Dict[str, Any]:
        """Find most relevant heading for chunk"""

        # Find most recent heading
        for heading in reversed(headings):
            return heading

        return {"title": "Document", "level": 0}

    def _detect_content_type(self, content: str, detected: Dict[str, Any]) -> str:
        """Detect content type"""

        if any("|" in line for line in content.split("\n")):
            return "table"
        elif content.strip().startswith("-"):
            return "list"
        else:
            return "text"

    def _count_tokens(self, text: str) -> int:
        """Count approximate tokens"""

        # Better estimate: ~1 token per 4 chars
        return max(1, len(text) // 4)
