from pathlib import Path

from docuflow.core.ingestion import get_sections, convert_pdf_to_md, save_markdown
from docuflow.interfaces import ITextEmbedder, IVectorStore
from docuflow.configs import settings
from docuflow.utils import get_logger


class IngestionPipeline:
    def __init__(self, embedder: ITextEmbedder, vector_store: IVectorStore):
        self.logger = get_logger(__name__)
        self.embedder = embedder
        self.vector_store = vector_store

    def ingest(self, file_path: Path):
        # conversion of pdf to md
        self.logger.info("Starting conversion from pdf to md")
        markdown_text = convert_pdf_to_md(file_path)

        # Saving markdown
        self.logger.info("Saving Markdown file")
        save_markdown(markdown_text, settings.output_path)

        # chunking md to document objects
        self.logger.info("Starting chunking...")
        documents = get_sections(markdown_text)
        self.logger.info(f"Generated {len(documents)} chunks")

        # Extract content and metadata
        texts = [doc.page_content for doc in documents]
        self.logger.info(f"Stored {len(texts)} chunks into vector store")
        metadata = [doc.metadata for doc in documents]

        # generate embeddings
        self.logger.info("Generating embeddings...")
        embeddings = self.embedder.embed(texts)
        self.logger.info("Storing embeddings in vector store...")

        #  Generate IDs
        ids = [str(i) for i in range(len(texts))]

        # store in vector db
        self.vector_store.add(
            ids=ids,
            documents=texts,
            metadata=metadata,
            embeddings=embeddings,
        )
        self.logger.info("Ingestion complete.")
