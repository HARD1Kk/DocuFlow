import importlib.metadata
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pymupdf.layout  # noqa: F401
import pymupdf4llm

from docuflow.interfaces import BaseConverter
from docuflow.schemas import RawDocument
from docuflow.utils import PdfQualityChecker, get_logger

logger = get_logger(__name__)


def _get_package_version(pkg_name: str, fallback: str = "unknown") -> str:
    """Safely fetch installed package version."""
    try:
        return importlib.metadata.version(pkg_name)
    except Exception:
        return fallback

# Shared quality checker — conservative defaults.
# Only triggers Docling when PyMuPDF4LLM output is clearly degraded.
_quality_checker = PdfQualityChecker(
    min_chars=200,
    min_chars_per_page=80,
    max_short_line_ratio=0.60,
    short_line_threshold=25,
    min_tables=0,
)


def preprocess_markdown(text: str) -> str:
    """Preprocess markdown content to clean up artifacts before chunking."""
    if not text:
        return ""

    # 1. Remove PyMuPDF image placeholders: **==> picture [...] intentionally omitted <==**
    # Matches with or without bold format asterisks, case-insensitive
    text = re.sub(
        r"\*?\*?==>\s*picture\s*\[\d+\s*x\s*\d+\]\s*intentionally\s*omitted\s*<==\*?\*?", "", text, flags=re.IGNORECASE
    )

    # 2. Remove standalone page numbers
    # A standalone page number is a line containing only a number (optionally with whitespace)
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)

    # 3. Collapse extra blank lines (limit to maximum one consecutive blank line)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def _convert_pdf_with_pymupdf(pdf_file: Path, ignore_images: bool = False) -> str:
    """Primary extractor: fast, low-memory, good for clean/digital PDFs."""
    markdown_text = pymupdf4llm.to_markdown(str(pdf_file), use_ocr=True, ignore_images=ignore_images)
    logger.info(
        "PyMuPDF4LLM extracted %d chars from %s (ignore_images=%s)", len(markdown_text), pdf_file, ignore_images
    )
    return str(markdown_text)


def _convert_pdf_with_docling(pdf_file: Path) -> str:
    """Fallback extractor: handles complex layouts, multi-column, and table-heavy PDFs."""
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions, TableStructureOptions
    from docling.document_converter import DocumentConverter as DoclingConverter
    from docling.document_converter import PdfFormatOption

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options = TableStructureOptions(do_cell_matching=True)

    converter = DoclingConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)})
    result = converter.convert(str(pdf_file))
    markdown_text = result.document.export_to_markdown()
    logger.info("Docling extracted %d chars from %s", len(markdown_text), pdf_file)
    return markdown_text


def convert_pdf_to_markdown_with_meta(
    pdf_file: Path, ignore_images: bool = False
) -> tuple[str, str, str]:
    """Convert PDF file to Markdown and return (markdown_text, parser_name, parser_version)."""
    pdf_file = pdf_file.expanduser().resolve()
    primary_exc: Exception | None = None
    primary_text: str | None = None

    # --- Stage 1: PyMuPDF4LLM ---
    try:
        primary_text = _convert_pdf_with_pymupdf(pdf_file, ignore_images=ignore_images)
        primary_text = preprocess_markdown(primary_text)
    except Exception as exc:
        primary_exc = exc
        logger.warning(
            "PyMuPDF4LLM failed for %s (%s) — attempting Docling fallback",
            pdf_file,
            exc,
        )

    # Check quality if we got output from the primary extractor
    if primary_text is not None:
        if _quality_checker.is_good_enough(primary_text, source_path=pdf_file, extractor="pymupdf4llm"):
            version_str = _get_package_version("pymupdf4llm", fallback=_get_package_version("pymupdf", "1.27.2"))
            return primary_text, "pymupdf4llm", version_str
        logger.warning(
            "PyMuPDF4LLM output quality insufficient for %s — triggering Docling fallback",
            pdf_file,
        )

    # --- Stage 2: Docling fallback ---
    try:
        fallback_text = _convert_pdf_with_docling(pdf_file)
        fallback_text = preprocess_markdown(fallback_text)
        logger.info("Docling fallback succeeded for %s", pdf_file)
        return fallback_text, "docling", _get_package_version("docling", "2.64.0")
    except Exception as fallback_exc:
        primary_msg = f"PyMuPDF4LLM: {primary_exc}" if primary_exc else "PyMuPDF4LLM: quality check failed"
        raise RuntimeError(
            f"PDF conversion failed for {pdf_file}. "
            f"Primary failure — {primary_msg}. "
            f"Fallback (Docling) failure — {fallback_exc}"
        ) from fallback_exc


def convert_pdf_to_markdown(pdf_file: Path, ignore_images: bool = False) -> str:
    """Convert a PDF file to Markdown using a two-stage pipeline with quality-gated fallback."""
    text, _, _ = convert_pdf_to_markdown_with_meta(pdf_file, ignore_images=ignore_images)
    return text


def convert_docx_to_markdown(docx_file: Path) -> str:
    """Convert a DOCX file into markdown using pandoc."""
    docx_file = docx_file.expanduser().resolve()
    try:
        result = subprocess.run(
            ["pandoc", str(docx_file), "-t", "markdown", "--wrap=none"],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
        logger.info("Converted DOCX %s into %s characters of markdown", docx_file, len(result.stdout))
        return result.stdout
    except Exception as exc:
        logger.exception("Failed to convert DOCX %s", docx_file)
        raise RuntimeError(f"DOCX conversion failed for {docx_file}") from exc


def extract_text_content(file_path: Path) -> str:
    """Read plain-text or markdown files as UTF-8 text."""
    return file_path.expanduser().resolve().read_text(encoding="utf-8")


def convert_spreadsheet_to_markdown(file_path: Path) -> str:
    """Convert spreadsheet (XLS, XLSX, CSV, TSV) to markdown table."""
    file_path = file_path.expanduser().resolve()
    try:
        # Try reading with xlrd for .xls, openpyxl for .xlsx
        if file_path.suffix.lower() == ".xls":
            df = pd.read_excel(file_path, engine="xlrd")
        elif file_path.suffix.lower() == ".xlsx":
            df = pd.read_excel(file_path, engine="openpyxl")
        elif file_path.suffix.lower() in {".csv", ".tsv"}:
            sep = "\t" if file_path.suffix.lower() == ".tsv" else ","
            df = pd.read_csv(file_path, sep=sep)
        else:
            raise ValueError(f"Unsupported spreadsheet format: {file_path.suffix}")

        # Convert to markdown table
        markdown = df.to_markdown(index=False)
        logger.info("Converted spreadsheet %s into %s characters of markdown", file_path, len(markdown))
        return markdown

    except Exception as exc:
        logger.exception("Failed to convert spreadsheet %s", file_path)
        raise RuntimeError(f"Spreadsheet conversion failed for {file_path}") from exc


class DocumentConverter(BaseConverter):
    """Convert document files into normalized markdown or text."""

    SUPPORTED_EXTENSIONS = (".pdf", ".docx", ".txt", ".md", ".xls", ".xlsx", ".csv", ".tsv")

    def __init__(self, ignore_images: bool = False) -> None:
        self.ignore_images = ignore_images

    def convert(self, raw_document: RawDocument) -> str:
        source_path = Path(raw_document.source)
        file_format = raw_document.metadata.get("format", source_path.suffix.lower()).lower()
        ignore_images = raw_document.metadata.get("ignore_images", self.ignore_images)

        if file_format == ".pdf":
            text, parser_name, parser_ver = convert_pdf_to_markdown_with_meta(
                source_path, ignore_images=ignore_images
            )
            raw_document.metadata["parser"] = parser_name
            raw_document.metadata["parser_version"] = parser_ver
            return text

        if file_format == ".docx":
            raw_document.metadata["parser"] = "pandoc"
            raw_document.metadata["parser_version"] = _get_package_version("pandoc", fallback="cli")
            return convert_docx_to_markdown(source_path)

        if file_format in {".txt", ".md"}:
            raw_document.metadata["parser"] = "utf8"
            raw_document.metadata["parser_version"] = sys.version.split()[0]
            return extract_text_content(source_path)

        if file_format in {".xls", ".xlsx", ".csv", ".tsv"}:
            raw_document.metadata["parser"] = "pandas"
            raw_document.metadata["parser_version"] = _get_package_version("pandas", fallback="2.0.0")
            return convert_spreadsheet_to_markdown(source_path)

        raise ValueError(f"Unsupported document format: {file_format}")
