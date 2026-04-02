# src/docuflow/core/chunking/spreadsheet_chunker.py
"""Chunker for spreadsheet data (XLSX, CSV, TSV)."""

import csv
import io
from typing import Dict, List

from docuflow.core.chunking.base_chunker import BaseChunker
from docuflow.schemas.chunk import Chunk, ChunkBatch, ChunkingConfig, ContentType, DocumentType


class SpreadsheetChunker(BaseChunker):
    """
    Chunker for spreadsheet data.

    Strategy:
    - Each row becomes a chunk (if small enough)
    - Large rows are split by column groups
    - Header row is included in each chunk for context
    - Metadata includes column names and row indices
    """

    @property
    def supported_document_types(self) -> List[DocumentType]:
        return [DocumentType.SPREADSHEET]

    def __init__(self, config: ChunkingConfig | None = None):
        super().__init__(config)
        self.headers: List[str] = []

    def chunk(self, content: str, metadata: Dict[str, any]) -> ChunkBatch:
        """Chunk spreadsheet content into row-based chunks."""
        if not content or not content.strip():
            return ChunkBatch(
                source=metadata.get("source", "unknown"),
                format=DocumentType.SPREADSHEET,
                total_pages=metadata.get("total_sheets", 1),
                total_tokens=0,
                processing_errors=["Empty spreadsheet content"],
            )

        # Parse the content based on format
        file_format = metadata.get("spreadsheet_format", "csv")

        try:
            if file_format == "csv":
                rows = self._parse_csv(content)
            elif file_format == "tsv":
                rows = self._parse_tsv(content)
            else:
                rows = self._parse_csv(content)  # Default to CSV
        except Exception as e:
            return ChunkBatch(
                source=metadata.get("source", "unknown"),
                format=DocumentType.SPREADSHEET,
                total_pages=metadata.get("total_sheets", 1),
                total_tokens=0,
                processing_errors=[f"Failed to parse spreadsheet: {e}"],
            )

        if not rows:
            return ChunkBatch(
                source=metadata.get("source", "unknown"),
                format=DocumentType.SPREADSHEET,
                total_pages=metadata.get("total_sheets", 1),
                total_tokens=0,
                processing_errors=["No data rows found"],
            )

        # Extract headers
        self.headers = rows[0] if rows else []
        data_rows = rows[1:] if len(rows) > 1 else []

        # Create chunks from rows
        chunks = self._create_row_chunks(data_rows, metadata)

        total_tokens = sum(c.token_count for c in chunks)

        return ChunkBatch(
            source=metadata.get("source", "unknown"),
            format=DocumentType.SPREADSHEET,
            total_pages=metadata.get("total_sheets", 1),
            total_tokens=total_tokens,
            chunks=chunks,
        )

    def _parse_csv(self, content: str) -> List[List[str]]:
        """Parse CSV content."""
        reader = csv.reader(io.StringIO(content))
        return list(reader)

    def _parse_tsv(self, content: str) -> List[List[str]]:
        """Parse TSV content."""
        reader = csv.reader(io.StringIO(content), delimiter="\t")
        return list(reader)

    def _create_row_chunks(self, rows: List[List[str]], metadata: Dict[str, any]) -> List[Chunk]:
        """Create chunks from data rows."""
        chunks = []
        sheet_name = metadata.get("sheet_name", "Sheet1")
        source = metadata.get("source", "unknown")

        for row_index, row in enumerate(rows, start=2):  # Start at 2 (1-indexed, after header)
            # Convert row to markdown table format
            row_content = self._row_to_markdown(row)

            # Check if row needs to be split
            token_count = self._count_tokens(row_content)

            if token_count <= self.config.max_chunk_size:
                # Single chunk for this row
                chunk = self._create_chunk(
                    chunk_id=self._generate_chunk_id(f"{sheet_name}_row{row_index}", len(chunks)),
                    content=row_content,
                    content_type=ContentType.TABLE.value,
                    metadata={
                        "sheet_name": sheet_name,
                        "row_index": row_index,
                        "columns": self.headers,
                        "num_columns": len(self.headers),
                    },
                    token_count=token_count,
                )
                chunks.append(chunk)
            else:
                # Split row into multiple chunks by column groups
                row_chunks = self._split_large_row(row, row_index, sheet_name, len(chunks))
                chunks.extend(row_chunks)

        return chunks

    def _row_to_markdown(self, row: List[str]) -> str:
        """Convert a row to markdown table format with headers."""
        if not self.headers:
            return " | ".join(row)

        lines = []

        # Header row
        lines.append("| " + " | ".join(self.headers) + " |")

        # Separator row
        lines.append("| " + " | ".join(["---"] * len(self.headers)) + " |")

        # Data row
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")

        return "\n".join(lines)

    def _split_large_row(
        self,
        row: List[str],
        row_index: int,
        sheet_name: str,
        chunk_index: int,
    ) -> List[Chunk]:
        """Split a large row into column groups."""
        chunks = []

        # Group columns to fit within max size
        current_group: List[int] = []
        current_tokens = 0

        for col_idx, cell in enumerate(row):
            cell_tokens = self._count_tokens(str(cell))

            if current_tokens + cell_tokens > self.config.max_chunk_size and current_group:
                # Emit current group and start new one
                group_chunk = self._create_column_group_chunk(
                    row=row,
                    columns=current_group,
                    row_index=row_index,
                    sheet_name=sheet_name,
                    chunk_index=chunk_index + len(chunks),
                )
                chunks.append(group_chunk)
                current_group = []
                current_tokens = 0

            current_group.append(col_idx)
            current_tokens += cell_tokens

        # Emit final group
        if current_group:
            group_chunk = self._create_column_group_chunk(
                row=row,
                columns=current_group,
                row_index=row_index,
                sheet_name=sheet_name,
                chunk_index=chunk_index + len(chunks),
            )
            chunks.append(group_chunk)

        return chunks

    def _create_column_group_chunk(
        self,
        row: List[str],
        columns: List[int],
        row_index: int,
        sheet_name: str,
        chunk_index: int,
    ) -> Chunk:
        """Create a chunk for a group of columns."""
        headers = [self.headers[i] if i < len(self.headers) else f"Col{i}" for i in columns]
        cells = [str(row[i]) if i < len(row) else "" for i in columns]

        lines = [
            f"### {sheet_name} - Row {row_index} (Columns: {', '.join(headers)})\n",
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join(["---"] * len(headers)) + " |",
            "| " + " | ".join(cells) + " |",
        ]

        content = "\n".join(lines)

        return self._create_chunk(
            chunk_id=self._generate_chunk_id(f"{sheet_name}_row{row_index}_cols", chunk_index),
            content=content,
            content_type=ContentType.TABLE.value,
            metadata={
                "sheet_name": sheet_name,
                "row_index": row_index,
                "columns": headers,
                "column_indices": columns,
                "is_partial": len(columns) < len(self.headers),
            },
            token_count=self._count_tokens(content),
        )
