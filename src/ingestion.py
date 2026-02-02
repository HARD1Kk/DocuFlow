import pymupdf4llm
import pathlib
from config import Settings

def convert_pdf_to_md(pdf_path: str) -> str:
    """
    Converts a PDF to Markdown using layout analysis.
    Preserves tables and multi-column layouts.
    """

    # Simply returns the whole doc as a clean markdown string

    md_text = pymupdf4llm.to_markdown(pdf_path)
    return md_text

def smart_split():

    #step 1 Define the rules for splitting
    split_rules = [
        ("#",  "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3")
    ]

    #step 2 create splitter using these rules
    splitter = MarkDownHeaderTextSplitter(
        headers_to_split_on = split_rules
    )

   # Step 3: Give the markdown text to the splitter
    sections = splitter.split_text(markdown_text)

    return sections



