from pathlib import Path
from typing import Any, List, Mapping

import chromadb
import numpy as np

from docuflow.interfaces import IVectorStore
from docuflow.utils import get_logger


class ChromaVectorStore(IVectorStore):
    def __init__(self, db_path: Path, collection_name: str):
        self.logger = get_logger(__name__)

        self.logger.info("Initializing Chroma Persistent Client")
        self.client = chromadb.PersistentClient(path=db_path)

        self.logger.info(f"Creating or loading collection: {collection_name}")
        self.collection = self.client.get_or_create_collection(name=collection_name, embedding_function=None)

    def add(
        self,
        ids: List[str],
        documents: List[str],
        metadata: List[Mapping[str, Any]],
        embeddings: List[List[float]],
    ) -> None:
        import time

        from docuflow.utils import log_context

        with log_context(stage="Indexing"):
            self.logger.info(f"Adding/Upserting {len(ids)} documents to collection")

            # Size before
            try:
                count_before = self.collection.count()
            except Exception as e:
                self.logger.warning(f"Could not read index size before indexing: {e}")
                count_before = 0

            # Duplicate chunk_id detection (silent overwrite risk)
            try:
                existing = self.collection.get(ids=ids)
                existing_ids = existing.get("ids", [])
                if existing_ids:
                    self.logger.warning(f"Duplicate chunk IDs detected. Overwrite risk for IDs: {existing_ids}")
            except Exception as e:
                self.logger.warning(f"Failed to check for duplicate IDs in vector store: {e}")

            start_time = time.perf_counter()
            try:
                self.collection.upsert(
                    ids=ids,
                    documents=documents,
                    embeddings=np.array(embeddings),
                    metadatas=metadata,
                )
                latency_ms = (time.perf_counter() - start_time) * 1000

                # Size after
                try:
                    count_after = self.collection.count()
                except Exception as e:
                    self.logger.warning(f"Could not read index size after indexing: {e}")
                    count_after = count_before + len(ids)

                self.logger.info(
                    f"Successfully indexed/upserted {len(ids)} documents. "
                    f"Index count: before={count_before}, after={count_after} (latency={latency_ms:.2f}ms)",
                    extra={"latency_ms": latency_ms},
                )
            except Exception as e:
                latency_ms = (time.perf_counter() - start_time) * 1000
                self.logger.error(
                    f"Failed to add/upsert documents: {e}", exc_info=True, extra={"latency_ms": latency_ms}
                )
                raise

    def query(self, query_embedding: List[float], n_results: int = 5):
        from docuflow.utils import log_context

        with log_context(stage="Indexing"):
            self.logger.debug(f"Querying collection with top {n_results} results")

            try:
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results,
                )
                self.logger.info("Query executed successfully")
                return results

            except Exception as e:
                self.logger.error(f"Query failed: {e}", exc_info=True)
                raise

    def delete(self, ids: List[str]):
        from docuflow.utils import log_context

        with log_context(stage="Indexing"):
            self.logger.info(f"Deleting {len(ids)} documents from collection")

            try:
                count_before = self.collection.count()
                self.collection.delete(ids=ids)
                count_after = self.collection.count()

                self.logger.info(
                    f"Deleted {len(ids)} documents. Index count: before={count_before}, after={count_after}"
                )
            except Exception as e:
                self.logger.error(f"Delete operation failed: {e}", exc_info=True)
                raise
