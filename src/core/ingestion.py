import logging
from pathlib import Path
from typing import List
import pymupdf4llm
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter
from utils.debug_md import save_pdf_to_md

def convert_pdf_to_md(pdf_path: str) -> str:
    """
    Converts a PDF to Markdown using layout analysis.
    Preserves tables and multi-column layouts.
    """
    # Simply returns the whole doc as a clean markdown string
    md_text: str = pymupdf4llm.to_markdown(pdf_path)
    return md_text


def smart_split(markdown_text: str) -> List[Document]:
    # step 1 Define the rules for splitting
    split_rules = [("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3")]

    # step 2 create splitter using these rules
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=split_rules)

    # Step 3: Give the markdown text to the splitter
    sections = splitter.split_text(markdown_text)

    return sections


def ingest_data() -> None:
    folder_path = Path("data")

    logging.info("Finding Folder if exists")

    if not folder_path.exists():
        raise FileNotFoundError("Folder not found")

    list_pdfs = list(folder_path.glob("*.pdf"))

    print(f"files found : {[pdf.name for pdf in list_pdfs]}")
    for pdf in list_pdfs:
        print(f"currently processing file: {pdf.name}")

        try:
            text = convert_pdf_to_md(str(pdf))
            chunks = smart_split(text)
            logging.info(f"Found {len(chunks)} in this file")
        except Exception as e:
            logging.error(f"Failed to process {pdf.name}: {e}")

    return None
