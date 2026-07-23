from pathlib import Path
from unittest.mock import patch

from docuflow.processing.converters.document_converter import (
    DocumentConverter,
    convert_pdf_to_markdown,
)
from docuflow.schemas import RawDocument

# A mock string that passes the quality checker (min_chars=200, low short-line ratio)
GOOD_PDF_CONTENT = ("This is a well-extracted PDF document. " * 15).strip()


@patch("pymupdf4llm.to_markdown")
def test_convert_pdf_to_markdown_direct(mock_to_markdown):
    mock_to_markdown.return_value = GOOD_PDF_CONTENT
    pdf_path = Path("sample.pdf")

    # 1. Test default parameter (should be False)
    res = convert_pdf_to_markdown(pdf_path)
    assert res == GOOD_PDF_CONTENT
    mock_to_markdown.assert_called_with(str(pdf_path.resolve()), use_ocr=True, ignore_images=False)

    # 2. Test explicit False
    convert_pdf_to_markdown(pdf_path, ignore_images=False)
    mock_to_markdown.assert_called_with(str(pdf_path.resolve()), use_ocr=True, ignore_images=False)

    # 3. Test explicit True
    convert_pdf_to_markdown(pdf_path, ignore_images=True)
    mock_to_markdown.assert_called_with(str(pdf_path.resolve()), use_ocr=True, ignore_images=True)


@patch("pymupdf4llm.to_markdown")
def test_document_converter_init_config(mock_to_markdown):
    mock_to_markdown.return_value = GOOD_PDF_CONTENT
    pdf_path = "sample.pdf"

    # Convert using a DocumentConverter configured with ignore_images=True
    converter = DocumentConverter(ignore_images=True)
    raw_doc = RawDocument(content=b"pdf content", source=pdf_path, metadata={"format": ".pdf"})

    res = converter.convert(raw_doc)
    assert res == GOOD_PDF_CONTENT
    mock_to_markdown.assert_called_with(str(Path(pdf_path).resolve()), use_ocr=True, ignore_images=True)


@patch("pymupdf4llm.to_markdown")
def test_document_converter_metadata_override(mock_to_markdown):
    mock_to_markdown.return_value = GOOD_PDF_CONTENT
    pdf_path = "sample.pdf"

    # Convert using a default DocumentConverter, but specify ignore_images=True in RawDocument metadata
    converter = DocumentConverter(ignore_images=False)
    raw_doc = RawDocument(content=b"pdf content", source=pdf_path, metadata={"format": ".pdf", "ignore_images": True})

    res = converter.convert(raw_doc)
    assert res == GOOD_PDF_CONTENT
    mock_to_markdown.assert_called_with(str(Path(pdf_path).resolve()), use_ocr=True, ignore_images=True)


@patch("pymupdf4llm.to_markdown")
def test_document_converter_metadata_override_false(mock_to_markdown):
    mock_to_markdown.return_value = GOOD_PDF_CONTENT
    pdf_path = "sample.pdf"

    # Convert using a DocumentConverter configured with ignore_images=True, but override to False in RawDocument metadata
    converter = DocumentConverter(ignore_images=True)
    raw_doc = RawDocument(content=b"pdf content", source=pdf_path, metadata={"format": ".pdf", "ignore_images": False})

    res = converter.convert(raw_doc)
    assert res == GOOD_PDF_CONTENT
    mock_to_markdown.assert_called_with(str(Path(pdf_path).resolve()), use_ocr=True, ignore_images=False)
