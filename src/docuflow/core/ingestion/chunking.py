import logging
import re
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

logger = logging.getLogger(__name__)


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
    logger.info(headers_to_split_on)
    # MD splits

    markdown_text = re.sub(
        r"^\*\*(.*?)\*\*", r"## \1", markdown_text, flags=re.MULTILINE
    )

    logger.info(markdown_text)
    print(markdown_text)

    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on
    )

    print(header_splitter)
    header_splits = header_splitter.split_text(markdown_text)

    logger.info(header_splits)

    # 2. Second pass: Split large chunks recursively (Size limit)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=100, separators=["\n\n", "\n", ". ", " ", ""]
    )

    # Split
    final_splits = text_splitter.split_documents(header_splits)

    # logger.info(final_splits.metadata)
    # print(final_splits)
    # logging.info(f"Split document into {len(final_splits)} chunks:")
    # for i, split in enumerate(final_splits):
    #     logging.info(f"Chunk {i+1}:\nContent: {split.page_content}\nMetadata: {split.metadata}\n---")
    return final_splits


# if __name__ == "__main__":
#     pdf = get_latest_pdf(settings.pdf_dir)
#     get_sections(convert_pdf_to_md(str(pdf)))
