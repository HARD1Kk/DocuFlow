from pathlib import Path
from typing import List

from docuflow.core.ingestion import CONVERTERS
from docuflow.interfaces import ILoader
from docuflow.schemas import RawDocument
from docuflow.utils import get_logger
from .base_loader import BaseLoader

class DocumentLoader(BaseLoader):
    """Load documents: PDF, DOCX, TXT, MD"""
    SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".txt", ".md"]

    
if __name__ == "__main__":
    doc = DocumentLoader()
    
    source_path = "/home/hardik/projects/DocuFlow/data/pdfs/report.pdf"
    
    # Load document
    raw_documents = doc.load(source_path)
    
    # Check result
    if raw_documents:
        raw_doc = raw_documents[0]
        print(f"✅ Loaded: {raw_doc.source}")
        print(f"Content length: {len(raw_doc.content)}")
        print(f"Metadata: {raw_doc.metadata}")
    else:
        print(f"❌ Failed to load: {source_path}")