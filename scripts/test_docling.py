import sys
from pathlib import Path

# Add src to python path
sys.path.append("/home/hardik/projects/DocuFlow/src")

from docuflow.processing.converters.document_converter import _convert_pdf_with_docling

pdf_file = Path("/home/hardik/projects/DocuFlow/data/input/sample_pdf.pdf")
print("Converting PDF with Docling...")
try:
    docling_text = _convert_pdf_with_docling(pdf_file)
    print("\n--- DOCLING MARKDOWN OUTPUT ---")
    print(docling_text)
except Exception as e:
    print(f"Error running Docling: {e}")
