import logging
from pathlib import Path
from typing import Any, List, Mapping

import chromadb
import numpy as np

from docuflow.interfaces.vector_store import VectorStore

logger = logging.getLogger(__name__)


class ChromaVectorStore(VectorStore):
    def __init__(self, db_path: Path, collection_name: str):
        self.client = chromadb.PersistentClient(path=db_path)

        self.collection = self.client.get_or_create_collection(
            name=collection_name, embedding_function=None
        )

    def add(
        self,
        ids: List[str],
        documents: List[str],
        metadata: List[Mapping[str, Any]],
        embeddings: List[List[float]],
    ):
        # # Get the text and metadata from documents
        # doc_data = get_meta_content_id(documents)

        # # Generate embeddings using the embed_text method
        # embeddings = self.embedding_service.embed_texts(doc_data["documents"])

        # embeddings = np.array(embeddings)

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=np.array(embeddings),
            metadatas=metadata,
        )

    def query(self, query_embedding: List[float], n_results: int = 5):
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
        )

    def delete(self, ids: List[str]):
        self.collection.delete(ids=ids)
