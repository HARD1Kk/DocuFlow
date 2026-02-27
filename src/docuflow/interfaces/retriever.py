from abc import ABC, abstractmethod
from typing import List
from docuflow.schemas import RetrievedChunk


class IRetriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[RetrievedChunk]:
        """Return top_k relevant documents for query."""
        pass
