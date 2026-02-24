from abc import ABC, abstractmethod
from typing import List, Sequence


class ITextEmbedder(ABC):
    """

    Interface for Text Embedding

    """

    @abstractmethod
    def embed(self, texts: Sequence[str]) -> List[List[float]]:
        pass
