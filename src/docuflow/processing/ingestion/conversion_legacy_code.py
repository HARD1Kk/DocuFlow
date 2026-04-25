from pathlib import Path
from typing import Callable

from docuflow.processing.converters import (
    ConverterFactory,
    convert_docx_to_markdown,
    convert_image_to_markdown,
    convert_pdf_to_markdown,
)
from docuflow.processing.converters import (
    extract_text_content as read_text_content,
)
from docuflow.schemas import RawDocument
from docuflow.utils import get_logger

logger = get_logger(__name__)


def get_converter(file_path: str) -> Callable[[Path], str]:
    """Get appropriate converter for file type."""
    suffix = Path(file_path).suffix.lower()
    converter = CONVERTERS.get(suffix)

    if not converter:
        raise ValueError(f"No converter for {suffix}. Supported: {list(CONVERTERS.keys())}")

    return converter


# ===== DOCUMENT CONVERTERS =====


def convert_pdf_to_md(pdf_file: Path) -> str:
    """Compatibility wrapper around the organized document converter."""
    return convert_pdf_to_markdown(pdf_file)


def convert_docx_to_md(docx_file: Path) -> str:
    """Compatibility wrapper around the organized document converter."""
    return convert_docx_to_markdown(docx_file)


def extract_text_content(file_path: Path) -> str:
    """Compatibility wrapper around the organized document converter."""
    return read_text_content(file_path)


# ===== IMAGE CONVERTER =====


def convert_image_content(image_file: Path) -> str:
    """Compatibility wrapper around the organized image converter."""
    return convert_image_to_markdown(image_file)


def convert_file_to_markdown(file_path: Path) -> str:
    """Route any supported file through the factory-based converter layer."""
    resolved_path = file_path.expanduser().resolve()
    raw_document = RawDocument(
        content=b"",
        source=str(resolved_path),
        metadata={
            "filename": resolved_path.name,
            "file_size": resolved_path.stat().st_size,
            "format": resolved_path.suffix.lower(),
        },
    )
    converter = ConverterFactory.get_converter(str(resolved_path))
    return converter.convert(raw_document)


# ===== CONVERTERS MAPPING =====

CONVERTERS = {
    ".pdf": convert_pdf_to_md,
    ".docx": convert_docx_to_md,
    ".txt": extract_text_content,
    ".md": extract_text_content,
    ".png": convert_image_content,
    ".jpg": convert_image_content,
    ".jpeg": convert_image_content,
    ".webp": convert_image_content,
    ".gif": convert_image_content,
}


def save_markdown(md_text: str, output_path: Path) -> Path:
    """Save markdown text to a file."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(md_text, encoding="utf-8")
    logger.info("Saved %s file at %s", output_file, output_path)
    return output_file
