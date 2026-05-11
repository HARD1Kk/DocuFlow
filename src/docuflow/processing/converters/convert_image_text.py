from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import easyocr
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableStructureOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

from docuflow.interfaces import IOCRModel
from docuflow.utils import get_logger

logger = get_logger(__name__)


class DoclingModel(IOCRModel):
    """
    OCR Model that extracts structured content from documents.
    """

    def __init__(self):
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = True
        pipeline_options.do_table_structure = True
        pipeline_options.table_structure_options = TableStructureOptions(do_cell_matching=True)

        self.converter = DocumentConverter(
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
        )

    def extract(self, file_path: str | Path) -> Dict[str, Any]:
        """
        Extract both markdown and structured JSON from document.

        Returns:
            {
                "markdown": "...",
                "structured": {...},
                "metadata": {...}
            }
        """
        try:
            result = self.converter.convert(str(file_path))

            markdown = result.document.export_to_markdown()
            structured_data = result.document.export_to_dict()

            return {
                "markdown": markdown,
                "structured": structured_data,
                "metadata": {
                    "source": str(file_path),
                    "num_pages": len(result.pages) if hasattr(result, "pages") else 1,
                },
            }
        except Exception as e:
            logger.error(f"Docling conversion failed for {file_path}: {e}", exc_info=True)
            raise


class EasyOCRModel(IOCRModel):
    """
    Offline OCR Model using EasyOCR - no network required.
    """

    def __init__(self, languages: list[str] | None = None):
        self.languages = languages or ["en"]
        self._reader: easyocr.Reader | None = None

    def _get_reader(self) -> easyocr.Reader:
        if self._reader is None:
            self._reader = easyocr.Reader(self.languages, gpu=False, verbose=False)
        return self._reader

    def extract(self, file_path: str | Path) -> Dict[str, Any]:
        try:
            reader = self._get_reader()
            results = reader.readtext(str(file_path))

            text_lines = []
            for _, text, confidence in results:
                if confidence > 0.3:
                    text_lines.append(text)

            markdown = "\n".join(text_lines)

            return {
                "markdown": markdown,
                "structured": {"text": text_lines},
                "metadata": {
                    "source": str(file_path),
                    "num_lines": len(text_lines),
                    "model": "easyocr",
                },
            }
        except Exception as e:
            logger.error(f"EasyOCR failed for {file_path}: {e}", exc_info=True)
            raise


def convert_image_to_markdown(image_path: Path, use_docling: bool = True) -> str:
    """
    Convert an image file to markdown.

    Args:
        image_path: Path to the image file.
        use_docling: If True, use Docling (requires network). If False, use EasyOCR (offline).

    Returns:
        Markdown text extracted from the image.
    """
    if use_docling:
        model = DoclingModel()
    else:
        model = EasyOCRModel()

    result = model.extract(image_path)
    return result["markdown"]
