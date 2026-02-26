from pathlib import Path
from typing import Any, List, Mapping

import chromadb
import numpy as np

from docuflow.utils import get_logger
from docuflow.interfaces import IVectorStore


class ChromaVectorStore(IVectorStore):
    def __init__(self, db_path: Path, collection_name: str):
        self.logger = get_logger(__name__)

        self.logger.info("Initializing Chroma Persistent Client")
        self.client = chromadb.PersistentClient(path=db_path)

        self.logger.info(f"Creating or loading collection: {collection_name}")
        self.collection = self.client.get_or_create_collection(
            name=collection_name, embedding_function=None
        )

    def add(
        self,
        ids: List[str],
        documents: List[str],
        metadata: List[Mapping[str, Any]],
        embeddings: List[List[float]],
    ) -> None:
        self.logger.debug(f"Adding {len(ids)} documents to collection")
        # # Get the text and metadata from documents
        # doc_data = get_meta_content_id(documents)

        # # Generate embeddings using the embed_text method
        # embeddings = self.embedding_service.embed_texts(doc_data["documents"])

        # embeddings = np.array(embeddings)
        try:
            self.collection.upsert(
                ids=ids,
                documents=documents,
                embeddings=np.array(embeddings),
                metadatas=metadata,
            )
            self.logger.info(f"Successfully upserted {len(ids)} documents")
        except Exception:
            self.logger.error("Failed to add documents", exc_info=True)
            raise

    def query(self, query_embedding: List[float], n_results: int = 5):
        self.logger.debug(f"Querying collection with top {n_results} results")

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
            )
            self.logger.info("Query executed successfully")
            return results

        except Exception:
            self.logger.error("Query failed", exc_info=True)
            raise

    def delete(self, ids: List[str]):
        self.logger.debug(f"Deleting {len(ids)} documents")

        try:
            self.collection.delete(ids=ids)
            self.logger.info(f"Deleted {len(ids)} documents")
        except Exception:
            self.logger.error("Delete operation failed", exec_info=True)
            raise
