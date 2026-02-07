import logging
from pathlib import Path

import pymupdf.layout  # noqa: F401
import pymupdf4llm


def convert_pdf_to_md(pdf_file: str) -> str:
    """
     Convert the PDF at pdf_file path to Markdown text.

    Args:
        pdf_file (str): Path to the PDF.

    Returns:
        str: The document content in Markdown format.
    """
    md_text = pymupdf4llm.to_markdown(pdf_file, use_ocr=False)
    logging.info(f"Length of text for {pdf_file}: {len(md_text)}")
    return str(md_text)


def save_markdown(md_text: str, output_path: str) -> str:
    """
    Save markdown text to a file.

    Args:
        md_text (str): Markdown content
        output_path (str): Path where MD file is written

    Returns:
        str:
    """
    output_file = Path(output_path)
    output_file.write_bytes(md_text.encode())
    return str(output_file)
