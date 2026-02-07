from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)


def get_sections(markdown_text: str) -> List[Document]:
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

    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on
    )
    header_splits = header_splitter.split_text(markdown_text)

    # 2. Second pass: Split large chunks recursively (Size limit)
    # 2000 chars ~ 500 tokens. Adjust based on your embedding model limits.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000, chunk_overlap=200, separators=["\n\n", "\n", ".", " ", ""]
    )

    final_splits = text_splitter.split_documents(header_splits)

    return final_splits
