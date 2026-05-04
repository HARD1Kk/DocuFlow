from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

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


def convert_image_to_markdown(image_path: Path) -> str:
    """
    Convert an image file to markdown using Docling.

    Args:
        image_path: Path to the image file.

    Returns:
        Markdown text extracted from the image.
    """
    model = DoclingModel()
    result = model.extract(image_path)
    return result["markdown"]
