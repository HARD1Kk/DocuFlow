"""
Heuristic quality assessment for PDF extraction output.

Used by the PDF conversion pipeline to decide whether PyMuPDF4LLM output is
good enough, or whether a fallback to Docling is warranted.

All checks are deterministic, pure-Python, and run in microseconds on the
already-extracted string — no extra I/O or model calls.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from docuflow.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class QualityCheckResult:
    """Result of a PDF quality assessment."""

    passed: bool
    """True if the extraction output meets quality thresholds."""

    reasons: List[str] = field(default_factory=list)
    """Human-readable list of triggered heuristics (populated when passed=False)."""

    extractor: str = "pymupdf4llm"
    """Which extractor produced the text that was assessed."""

    def __str__(self) -> str:
        if self.passed:
            return f"QualityCheck PASSED [{self.extractor}]"
        return f"QualityCheck FAILED [{self.extractor}]: {'; '.join(self.reasons)}"


class PdfQualityChecker:
    """
    Heuristic scorer for PDF-extracted Markdown text.

    Conservative by design: prefer PyMuPDF4LLM unless the output is clearly
    degraded. Each check is an independent signal; any failure triggers fallback.

    Parameters
    ----------
    min_chars : int, default=200
        Minimum total character count. Pages with near-zero text usually indicate
        a failed OCR pass on an image-only or scanned document.

    min_chars_per_page : int, default=80
        Minimum average characters per page. Catches per-page OCR failures that
        the total threshold misses on multi-page documents.

    max_short_line_ratio : float, default=0.60
        Maximum ratio of lines shorter than `short_line_threshold` characters.
        High ratios indicate multi-column or chaotic layout extraction where
        PyMuPDF4LLM is splitting lines incorrectly.

    short_line_threshold : int, default=25
        Character length below which a line is considered "short" for the layout
        chaos heuristic.

    min_tables : int, default=0
        Minimum expected Markdown table count (``|``-delimited rows).
        Set > 0 only when you have strong prior knowledge that the document
        contains tables (e.g., financial reports, data sheets).
    """

    def __init__(
        self,
        min_chars: int = 200,
        min_chars_per_page: int = 80,
        max_short_line_ratio: float = 0.60,
        short_line_threshold: int = 25,
        min_tables: int = 0,
    ) -> None:
        self.min_chars = min_chars
        self.min_chars_per_page = min_chars_per_page
        self.max_short_line_ratio = max_short_line_ratio
        self.short_line_threshold = short_line_threshold
        self.min_tables = min_tables

    def check(
        self,
        text: str,
        source_path: Path | None = None,
        num_pages: int | None = None,
        extractor: str = "pymupdf4llm",
    ) -> QualityCheckResult:
        """
        Assess quality of extracted PDF text.

        Parameters
        ----------
        text : str
            Extracted Markdown text to evaluate.
        source_path : Path, optional
            Source PDF path — used only for logging context.
        num_pages : int, optional
            Page count of the source PDF. If provided, enables the per-page
            density check.
        extractor : str
            Name of the extractor that produced `text` (for logging).

        Returns
        -------
        QualityCheckResult
            ``passed=True`` when all heuristics pass; ``passed=False`` with
            a populated ``reasons`` list when any heuristic triggers.
        """
        reasons: list[str] = []
        label = str(source_path) if source_path else "<unknown>"

        # 1. Total content density
        total_chars = len(text.strip())
        if total_chars < self.min_chars:
            reasons.append(f"low_content: {total_chars} chars < threshold {self.min_chars}")

        # 2. Per-page density (only when page count is available)
        if num_pages and num_pages > 0:
            chars_per_page = total_chars / num_pages
            if chars_per_page < self.min_chars_per_page:
                reasons.append(
                    f"low_density_per_page: {chars_per_page:.0f} chars/page < threshold {self.min_chars_per_page}"
                )

        # 3. Layout chaos — high ratio of very short lines
        lines = [ln for ln in text.splitlines() if ln.strip()]
        if lines:
            short_lines = sum(1 for ln in lines if len(ln.strip()) < self.short_line_threshold)
            short_ratio = short_lines / len(lines)
            if short_ratio > self.max_short_line_ratio:
                reasons.append(
                    f"layout_chaos: {short_ratio:.0%} short lines (>{self.max_short_line_ratio:.0%} threshold)"
                )

        # 4. Missing tables (optional — only active when min_tables > 0)
        if self.min_tables > 0:
            table_rows = re.findall(r"^\|.+\|", text, re.MULTILINE)
            # Count distinct table blocks (separated by non-pipe lines)
            table_count = len(re.findall(r"(?:^\|.+\|\n?)+", text, re.MULTILINE))
            if table_count < self.min_tables:
                reasons.append(f"missing_tables: found {table_count} table(s), expected >= {self.min_tables}")

        result = QualityCheckResult(
            passed=len(reasons) == 0,
            reasons=reasons,
            extractor=extractor,
        )

        if not result.passed:
            logger.warning(
                "PDF quality check failed for %s: %s",
                label,
                result,
            )
        else:
            logger.debug("PDF quality check passed for %s [%s]", label, extractor)

        return result

    def is_good_enough(
        self,
        text: str,
        source_path: Path | None = None,
        num_pages: int | None = None,
        extractor: str = "pymupdf4llm",
    ) -> bool:
        """Convenience wrapper returning a plain bool."""
        return self.check(text, source_path, num_pages, extractor).passed
