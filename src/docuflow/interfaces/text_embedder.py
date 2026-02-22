from abc import ABC, abstractmethod
from typing import List, Sequence


class TextEmbedder(ABC):
    @abstractmethod
    def embed(self, texts: Sequence[str]) -> List[List[float]]:
        pass
