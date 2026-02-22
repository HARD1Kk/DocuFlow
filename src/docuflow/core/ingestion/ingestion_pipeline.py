import logging
from pathlib import Path

from docuflow.core.ingestion.chunking import get_sections
from docuflow.core.ingestion.conversion import convert_pdf_to_md
from docuflow.interfaces.text_embedder import TextEmbedder
from docuflow.interfaces.vector_store import VectorStore

logger = logging.getLogger(__name__)


class IngestionPipeline:
    def __init__(self, embedder: TextEmbedder, vector_store: VectorStore):
        self.embedder = embedder
        self.vector_store = vector_store

    def ingest(self, file_path: Path):
        # conversion of pdf to md
        logger.info("Starting conversion...")
        markdown_text = convert_pdf_to_md(file_path)
        print(type(markdown_text))

        # chunking md to document objects
        logger.info("Starting chunking...")
        documents = get_sections(markdown_text)
        logger.info(f"Generated {len(documents)} chunks")

        # Extract content and metadata
        texts = [doc.page_content for doc in documents]
        logger.info(f"Stored {len(texts)} chunks into vector store")
        metadata = [doc.metadata for doc in documents]

        # generate embeddings
        logger.info("Generating embeddings...")
        embeddings = self.embedder.embed(texts)
        logger.info("Storing embeddings in vector store...")

        #  Generate IDs
        ids = [str(i) for i in range(len(texts))]

        # store in vector db
        self.vector_store.add(
            ids=ids,
            documents=texts,
            metadata=metadata,
            embeddings=embeddings,
        )
        logger.info("Ingestion complete.")
