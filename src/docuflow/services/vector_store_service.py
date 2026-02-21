import logging

import chromadb
import numpy as np

from docuflow.schemas.document import Document
from docuflow.services.embedding_service import EmbeddingServices
from docuflow.utils.document_helper import get_meta_content_id

logger = logging.getLogger(__name__)


class VectorStoreService:
    def __init__(self, db_path: str, collection_name: str):
        self.client = chromadb.PersistentClient(path=db_path)

        self.collection = self.client.get_or_create_collection(
            name=collection_name, embedding_function=None
        )

        self.embedding_service: EmbeddingServices = EmbeddingServices()

    def add_document(self, documents: list["Document"]):
        # Get the text and metadata from documents
        doc_data = get_meta_content_id(documents)

        # Generate embeddings using the embed_text method
        embeddings = self.embedding_service.embed_texts(doc_data["documents"])

        embeddings = np.array(embeddings)

        self.collection.upsert(
            ids=doc_data["ids"],
            documents=doc_data["documents"],
            embeddings=embeddings,
            metadatas=doc_data["metadatas"],
        )

    def query(self, query_text: str, n_results: int = 5):
        query_embedding = self.embedding_service.embed_query(query_text)
        return self.collection.query(
            query_embeddings=[query_embedding], n_results=n_results
        )

    def delete(self, ids):
        self.collection.delete(ids=ids)
