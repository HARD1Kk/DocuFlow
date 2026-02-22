from abc import ABC, abstractmethod
from typing import Any, List, Mapping


class VectorStore(ABC):
    @abstractmethod
    def add(
        self,
        ids: List[str],
        documents: List[str],
        metadata: List[Mapping[str, Any]],
        embeddings: List[List[float]],
    ):
        pass

    @abstractmethod
    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5,
    ):
        pass

    @abstractmethod
    def delete(self, ids: List[str]):
        pass
