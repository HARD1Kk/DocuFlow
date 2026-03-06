from typing import List

from docuflow.interfaces import IRetriever, ITextEmbedder, IVectorStore
from docuflow.schemas import RetrievedChunk
from docuflow.utils import get_logger


class VectorRetriever(IRetriever):
    def __init__(self, embedder: ITextEmbedder, vector_store: IVectorStore):
        self.logger = get_logger(__name__)
        self.embedder = embedder
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int = 5) -> List[RetrievedChunk]:
        self.logger.info("Retrieving top {top_k} chunks for query")

        # Generate query embeddings
        query_embedding = self.embedder.embed([query])[0]
        print(query_embedding)

    #     # Query vector store
    #     raw_results = self.vector_store.query(
    #         query_embedding=query_embedding,
    #         n_results=top_k,
    #     )
    #     print(raw_results)
    #     # # # Extract and flatten results
    #     # documents = raw_results.get("documents", [[]])[0]
    #     # distances = raw_results.get("distances", [[]])[0]
    #     # metadatas = raw_results.get("metadatas", [[]])[0]

    #     # # Build structured output
    #     # retrieved_chunks: List[RetrievedChunk] = []
    #     # return retrieved_chunks
