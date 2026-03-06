import subprocess
from pathlib import Path

import pymupdf.layout  # noqa: F401
import pymupdf4llm

from docuflow.utils import get_logger

logger = get_logger(__name__)


def get_converter(file_path: str):
    """Get appropriate converter for file type"""
    suffix = Path(file_path).suffix.lower()
    converter = CONVERTERS.get(suffix)

    if not converter:
        raise ValueError(f"No converter for {suffix}. Supported: {list(CONVERTERS.keys())}")

    return converter


def convert_pdf_to_md(pdf_file: Path) -> str:
    """
     Convert the PDF at pdf_file path to Markdown text.

    Args:
        pdf_file (str): Path to the PDF.

    Returns:
        str: The document content in Markdown format.
    """
    try:
        md_text = pymupdf4llm.to_markdown(pdf_file, use_ocr=False)
        logger.info(f"Length of text for {pdf_file}: {len(md_text)}")
        return str(md_text)
    except Exception as e:
        logger.exception(f"Failed to convert {pdf_file}: {e}")
        raise


def convert_docx_to_md(docx_file: Path) -> str:
    result = subprocess.run(
        ["pandoc", str(docx_file), "-t", "markdown", "--wrap=none"],
        capture_output=True,
        text=True,
        timeout=30,
        check=True,
    )
    return result.stdout


def extract_txt_content(txt_file: Path) -> str:
    """Add this - TXT extraction (simple)"""
    return Path(txt_file).read_text(encoding="utf-8")


def extract_md_content(md_file: Path) -> str:
    """Add this - MD extraction (just read as-is)"""
    return Path(md_file).read_text(encoding="utf-8")


CONVERTERS = {
    ".pdf": convert_pdf_to_md,
    ".docx": convert_docx_to_md,
    ".txt": extract_txt_content,
    ".md": extract_md_content,
}


def save_markdown(md_text: str, output_path: Path) -> Path:
    """
    Save markdown text to a file.

    Args:
        md_text (str): Markdown content
        output_path (str): Path where MD file is written

    Returns:
        str:
    """
    # Ensure parent folder exists
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    output_file.write_text(md_text, encoding="utf-8")
    logger.info(f"Saved {output_file} file at {output_path} ")
    return output_file
