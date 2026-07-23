"""
Unit tests for PdfQualityChecker.

These are pure-Python tests against already-extracted text strings.
No PDF files or external libraries are required to run these tests.
"""

import pytest

from docuflow.utils.pdf_quality import PdfQualityChecker, QualityCheckResult


@pytest.fixture
def checker():
    """Default checker with standard thresholds."""
    return PdfQualityChecker(
        min_chars=200,
        min_chars_per_page=80,
        max_short_line_ratio=0.60,
        short_line_threshold=25,
        min_tables=0,
    )


# ---------------------------------------------------------------------------
# Positive cases (should PASS — PyMuPDF4LLM output is good enough)
# ---------------------------------------------------------------------------


class TestQualityPass:
    def test_clean_dense_text_passes(self, checker):
        text = "This is a well-extracted PDF document. " * 20
        result = checker.check(text)
        assert result.passed is True
        assert result.reasons == []

    def test_text_with_markdown_headings_passes(self, checker):
        text = (
            "# Introduction\n\n"
            "This document contains meaningful content. " * 15 + "\n\n"
            "## Methods\n\n"
            "We used a robust approach to extract text. " * 10
        )
        result = checker.check(text)
        assert result.passed is True

    def test_text_with_table_passes(self, checker):
        text = (
            "Summary of results.\n\n"
            "| Column A | Column B | Column C |\n"
            "|---|---|---|\n"
            "| Value 1  | Value 2  | Value 3  |\n"
            "| Value 4  | Value 5  | Value 6  |\n\n"
            "The table above shows the comparison between different methods. " * 10
        )
        result = checker.check(text)
        assert result.passed is True

    def test_is_good_enough_convenience_wrapper(self, checker):
        text = "Well extracted clean text from a digital PDF. " * 10
        assert checker.is_good_enough(text) is True


# ---------------------------------------------------------------------------
# Negative cases — each heuristic triggers independently
# ---------------------------------------------------------------------------


class TestQualityFail:
    def test_low_content_fails(self, checker):
        text = "Too short."
        result = checker.check(text)
        assert result.passed is False
        assert any("low_content" in r for r in result.reasons)

    def test_empty_text_fails(self, checker):
        result = checker.check("")
        assert result.passed is False
        assert any("low_content" in r for r in result.reasons)

    def test_low_density_per_page_fails(self, checker):
        # 5 pages, only 100 chars total → 20 chars/page (< 80 threshold)
        text = "A" * 100
        result = checker.check(text, num_pages=5)
        assert result.passed is False
        assert any("low_density_per_page" in r for r in result.reasons)

    def test_layout_chaos_fails(self, checker):
        # 80% of lines are very short (< 25 chars) — simulates multi-column chaos
        short_lines = ["col" for _ in range(40)]
        long_lines = ["This is a properly wrapped paragraph line." for _ in range(10)]
        text = "\n".join(short_lines + long_lines)
        # Prepend enough bulk chars so we pass min_chars threshold
        text = "x" * 300 + "\n" + text
        result = checker.check(text)
        assert result.passed is False
        assert any("layout_chaos" in r for r in result.reasons)

    def test_missing_tables_fails_when_required(self):
        # Checker configured to expect at least 1 table
        strict_checker = PdfQualityChecker(min_tables=1, min_chars=0)
        text = "This document should contain tables but does not. " * 10
        result = strict_checker.check(text)
        assert result.passed is False
        assert any("missing_tables" in r for r in result.reasons)

    def test_missing_tables_ignored_when_min_tables_zero(self, checker):
        # Default min_tables=0 — table absence should not trigger failure
        text = "Plain text document with no tables. " * 10
        result = checker.check(text)
        assert result.passed is True


# ---------------------------------------------------------------------------
# Multiple heuristics firing simultaneously
# ---------------------------------------------------------------------------


class TestMultipleFailures:
    def test_multiple_reasons_accumulated(self):
        checker = PdfQualityChecker(min_chars=500, min_tables=2)
        # Too short AND no tables
        text = "Short text. " * 5
        result = checker.check(text)
        assert result.passed is False
        assert len(result.reasons) >= 2

    def test_result_str_shows_reasons(self, checker):
        text = "x"
        result = checker.check(text)
        assert result.passed is False
        assert "FAILED" in str(result)
        assert "low_content" in str(result)


# ---------------------------------------------------------------------------
# QualityCheckResult dataclass
# ---------------------------------------------------------------------------


class TestQualityCheckResult:
    def test_passed_result_str(self):
        result = QualityCheckResult(passed=True, extractor="pymupdf4llm")
        assert "PASSED" in str(result)

    def test_failed_result_str(self):
        result = QualityCheckResult(passed=False, reasons=["low_content: 10 chars < 200"], extractor="pymupdf4llm")
        assert "FAILED" in str(result)
        assert "low_content" in str(result)
