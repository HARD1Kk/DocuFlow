import io
import subprocess
from pathlib import Path

import pandas as pd
import pymupdf.layout  # noqa: F401
import pymupdf4llm

from docuflow.interfaces import BaseConverter
from docuflow.schemas import RawDocument
from docuflow.utils import get_logger

logger = get_logger(__name__)


def convert_pdf_to_markdown(pdf_file: Path) -> str:
    """Convert a PDF file into markdown using PyMuPDF4LLM."""
    pdf_file = pdf_file.expanduser().resolve()
    try:
        markdown_text = pymupdf4llm.to_markdown(pdf_file, use_ocr=False)
        logger.info("Converted PDF %s into %s characters of markdown", pdf_file, len(markdown_text))
        return str(markdown_text)
    except Exception as exc:
        logger.exception("Failed to convert PDF %s", pdf_file)
        raise RuntimeError(f"PDF conversion failed for {pdf_file}") from exc


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

    def convert(self, raw_document: RawDocument) -> str:
        source_path = Path(raw_document.source)
        file_format = raw_document.metadata.get("format", source_path.suffix.lower()).lower()

        if file_format == ".pdf":
            return convert_pdf_to_markdown(source_path)
        if file_format == ".docx":
            return convert_docx_to_markdown(source_path)
        if file_format in {".txt", ".md"}:
            return extract_text_content(source_path)
        if file_format in {".xls", ".xlsx", ".csv", ".tsv"}:
            return convert_spreadsheet_to_markdown(source_path)

        raise ValueError(f"Unsupported document format: {file_format}")
