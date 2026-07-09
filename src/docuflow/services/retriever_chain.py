import time
import uuid
from typing import List

from docuflow.interfaces import IRetriever, ITextEmbedder, IVectorStore
from docuflow.schemas import RetrievedChunk
from docuflow.utils import get_logger, log_context


class VectorRetriever(IRetriever):
    def __init__(self, embedder: ITextEmbedder, vector_store: IVectorStore):
        self.logger = get_logger(__name__)
        self.embedder = embedder
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int = 5) -> List[RetrievedChunk]:
        """Retrieve top_k relevant documents for the query."""
        from docuflow.utils.logger import request_id_var

        # Generate a correlation ID if not set
        query_id = request_id_var.get("") or f"q-{uuid.uuid4().hex[:8]}"

        with log_context(request_id=query_id, stage="Retrieval"):
            self.logger.info(f"Retrieving top {top_k} chunks for query: '{query}'")

            start_time = time.perf_counter()
            try:
                # Generate query embeddings
                query_embeddings = self.embedder.embed([query])
                if not query_embeddings:
                    self.logger.warning(
                        "Empty query embedding generated",
                        extra={"latency_ms": (time.perf_counter() - start_time) * 1000},
                    )
                    return []

                query_embedding = query_embeddings[0]

                # Query vector store
                raw_results = self.vector_store.query(
                    query_embedding=query_embedding,
                    n_results=top_k,
                )

                latency_ms = (time.perf_counter() - start_time) * 1000

                # Extract results
                ids = raw_results.get("ids", [[]])[0]
                documents = raw_results.get("documents", [[]])[0]
                distances = raw_results.get("distances", [[]])[0]
                metadatas = raw_results.get("metadatas", [[]])[0]

                if not documents:
                    self.logger.warning(
                        f"Empty result set returned for query '{query}'", extra={"latency_ms": latency_ms}
                    )
                    return []

                retrieved_chunks = []
                self.logger.info(
                    f"Retrieved {len(documents)} chunks (latency={latency_ms:.2f}ms)", extra={"latency_ms": latency_ms}
                )

                for doc_id, doc, dist, meta in zip(ids, documents, distances, metadatas):
                    # Convert distance to similarity score
                    score = 1.0 - dist
                    self.logger.info(
                        f"Retrieved chunk: id={doc_id}, score={score:.4f}", extra={"latency_ms": latency_ms}
                    )
                    retrieved_chunks.append(RetrievedChunk(content=doc, score=score, metadata=meta))

                return retrieved_chunks

            except Exception as e:
                self.logger.error(f"Retrieval failed for query '{query}': {e}", exc_info=True)
                raise
