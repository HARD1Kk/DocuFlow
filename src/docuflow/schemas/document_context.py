# src/docuflow/schemas/document_context.py
"""Document-level context — single source of truth for document metadata.

Created once at ingestion time and propagated downstream so that every
chunk carries consistent, traceable provenance information without any
component needing to re-derive or hardcode these fields.
"""

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

from docuflow.schemas.chunk import DocumentType


@dataclass
class DocumentContext:
    """Immutable document-level metadata passed through the pipeline.

    Attributes:
        document_id: Deterministic 16-char hex hash of document content (or file bytes).
            Stable across repeated processing of the same file, even if renamed/moved.
        document_name: Base filename (e.g. ``"report.pdf"``).
        source_path: Original file path as supplied by the caller.
        document_type: Enum describing the document format.
        total_pages: Number of pages (1 for non-paginated formats).
        page_number: Per-page hint when available (``None`` otherwise).
        parser: Name of the extractor/converter used (e.g. ``"pymupdf4llm"``).
        parser_version: Installed version of the converter library.
    """

    document_id: str
    document_name: str
    source_path: str
    document_type: DocumentType
    total_pages: int = 1
    page_number: Optional[int] = None
    parser: str = ""
    parser_version: str = ""

    @staticmethod
    def generate_document_id(
        content: Optional[Union[bytes, str]] = None,
        source_path: str = "",
    ) -> str:
        """Return a deterministic 16-char hex SHA-256 ID derived from content.

        Prioritizes hashing raw content bytes or string content so that moving
        or renaming a file produces an identical ID. Falls back to reading
        file bytes from disk, or hashing source_path if content is unavailable.
        """
        if content is not None:
            if isinstance(content, str):
                content_bytes = content.encode("utf-8")
            else:
                content_bytes = bytes(content)
            return hashlib.sha256(content_bytes).hexdigest()[:16]

        if source_path:
            p = Path(source_path)
            if p.exists() and p.is_file():
                try:
                    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]
                except Exception:
                    pass
            return hashlib.sha256(source_path.encode("utf-8")).hexdigest()[:16]

        return hashlib.sha256(b"").hexdigest()[:16]

    @classmethod
    def from_source(
        cls,
        source_path: str,
        document_type: DocumentType,
        total_pages: int = 1,
        page_number: Optional[int] = None,
        content: Optional[Union[bytes, str]] = None,
        parser: str = "",
        parser_version: str = "",
    ) -> "DocumentContext":
        """Convenience factory that derives content-based ``document_id`` and ``document_name``."""
        name = Path(source_path).name
        doc_id = cls.generate_document_id(content=content, source_path=source_path)
        return cls(
            document_id=doc_id,
            document_name=name,
            source_path=source_path,
            document_type=document_type,
            total_pages=total_pages,
            page_number=page_number,
            parser=parser,
            parser_version=parser_version,
        )
