from abc import ABC, abstractmethod
from typing import Any, List, Mapping


class IVectorStore(ABC):
    """

    Interface for Vector Store

    """

    @abstractmethod
    def add(
        self,
        ids: List[str],
        documents: List[str],
        metadata: List[Mapping[str, Any]],
        embeddings: List[List[float]],
    ) -> None:
        """Add documents, embeddings, and metadata to the vector store."""
        pass

    @abstractmethod
    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5,
    ) -> dict[str, Any]:
        """Return top `n_results` from the vector store matching `query_embedding`."""
        pass

    @abstractmethod
    def delete(self, ids: List[str]) -> None:
        pass
