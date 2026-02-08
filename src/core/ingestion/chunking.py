import re
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

    # MD splits

    # Preprocess: Convert pseudo-headers in tables to real Markdown headers
    # Matches lines like ||**EDUCATION**|| and converts them to ### EDUCATION
    markdown_text = re.sub(
        r"^\|\|\*\*(.*?)\*\*\|\|", r"### \1", markdown_text, flags=re.MULTILINE
    )

    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on
    )
    header_splits = header_splitter.split_text(markdown_text)

    # 2. Second pass: Split large chunks recursively (Size limit)
    # 2000 chars ~ 500 tokens. Adjust based on your embedding model limits.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=250, chunk_overlap=30, separators=["\n\n", "\n", ".", " ", ""]
    )
    # Split
    final_splits = text_splitter.split_documents(header_splits)
    # logging.info(f"Split document into {len(final_splits)} chunks:")
    # for i, split in enumerate(final_splits):
    #     logging.info(f"Chunk {i+1}:\nContent: {split.page_content}\nMetadata: {split.metadata}\n---")
    return final_splits
