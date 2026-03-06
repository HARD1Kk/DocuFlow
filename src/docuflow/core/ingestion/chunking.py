import logging
import re
from typing import List

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

from docuflow.schemas.document import Document as DocuFlowDocument

logger = logging.getLogger(__name__)


def get_sections(markdown_text: str) -> List[DocuFlowDocument]:
    """
    Splits markdown text into semantic sections based on headers.
    If sections are too large, recursively splits them further.
    """
    # 1. First pass: Split by Markdown Headers (Semantic)
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]

    # MD splits

    markdown_text = re.sub(r"^\*\*(.*?)\*\*", r"## \1", markdown_text, flags=re.MULTILINE)

    header_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

    header_splits = header_splitter.split_text(markdown_text)

    # 2. Second pass: Split large chunks recursively (Size limit)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=100, separators=["\n\n", "\n", ". ", " ", ""]
    )

    # Split
    final_splits = text_splitter.split_documents(header_splits)
    logger.info(f"Split into {len(final_splits)} chunks")
    converted_docs = [
        DocuFlowDocument(
            page_content=doc.page_content,
            metadata=doc.metadata,
        )
        for doc in final_splits
    ]
    return converted_docs
