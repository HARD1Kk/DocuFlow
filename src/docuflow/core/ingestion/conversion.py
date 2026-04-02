import subprocess
from pathlib import Path
from typing import Callable, Optional

import pymupdf.layout  # noqa: F401
import pymupdf4llm
from paddleocr import PaddleOCR

from docuflow.utils import get_logger

logger = get_logger(__name__)


def get_converter(file_path: str) -> Callable[[Path], str]:
    """Get appropriate converter for file type"""
    suffix = Path(file_path).suffix.lower()
    converter = CONVERTERS.get(suffix)

    if not converter:
        raise ValueError(f"No converter for {suffix}. Supported: {list(CONVERTERS.keys())}")

    return converter


# ===== DOCUMENT CONVERTERS =====


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
    """Simple Pandoc conversion"""
    try:
        result = subprocess.run(
            ["pandoc", str(docx_file), "-t", "markdown", "--wrap=none"],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
        logger.info(f"Converted: {len(result.stdout)} chars")
        return result.stdout
    except Exception as e:
        logger.error(f"Pandoc failed: {e}")
        raise


def extract_text_content(file_path: Path) -> str:
    """Extract text from .txt or .md files"""

    return file_path.read_text(encoding="utf-8")


# ===== IMAGE CONVERTER =====


# ✅ Lazy load reader once
_ocr_reader: Optional[PaddleOCR] = None


def _get_ocr_reader() -> PaddleOCR:
    """Lazy load PaddleOCR reader - CPU only"""
    global _ocr_reader
    if _ocr_reader is None:
        logger.info("Loading PaddleOCR (CPU mode)...")
        _ocr_reader = PaddleOCR(
            use_angle_cls=True,  # handles rotated text
            lang="en",
            use_gpu=False,  # CPU mode
            show_log=False,  # suppress paddle logs
        )
    return _ocr_reader


def convert_image_content(file_path: Path) -> str:
    """Extract text from .png , .jpg , .jpeg , .svg , .webp files"""
    try:
        reader = _get_ocr_reader()

        # Extract text
        results = reader.ocr(str(file_path), cls=True)

        if not results or not results[0]:
            logger.warning(f"No text detected in: {file_path}")
            return ""

        logger.info(f"Extracting text from: {file_path}")

        # Combine all text
        text = "\n".join([line[1][0] for line in results[0]])
        logger.debug(f"Extracted text: {text[:200]}...")

        if not text.strip():
            logger.warning(f"No text detected in: {file_path}")

        logger.info(f"Extracted {len(text)} chars from image")
        return text

    except Exception as e:
        logger.error(f"Failed to convert image: {e}")
        raise


# ===== CONVERTERS MAPPING =====

CONVERTERS = {
    # Documents
    ".pdf": convert_pdf_to_md,
    ".docx": convert_docx_to_md,
    ".txt": extract_text_content,
    ".md": extract_text_content,
    # Images
    ".png": convert_image_content,
    ".jpg": convert_image_content,
    ".jpeg": convert_image_content,
    ".webp": convert_image_content,
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
