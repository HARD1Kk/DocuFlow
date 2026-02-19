import logging
from typing import List

import numpy as np
from FlagEmbedding import FlagModel

from docuflow.configs.settings import settings

logger = logging.getLogger(__name__)


# Global model instance
model = FlagModel(
    settings.embedding_model,
    query_instruction_for_retrieval="Represent this sentence for searching relevant passages:",
    use_fp16=False,
)


class EmbeddingServices:
    def __init__(self, model, batch_size: int = 64):
        """
        Store the model and batch_size inside this service object.
        """
        self.model = model
        self.batch_size = batch_size

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate dense embeddings for a list of texts.

        Args:
            texts: List of strings to embed.

        Returns:
            List of embeddings (lists of floats).
        """

        if not texts:
            return []

        try:
            all_embeddings = []

            for i in range(0, len(texts), self.batch_size):
                batch = texts[i : i + self.batch_size]
                embeddings = self.model.encode(batch)
                # FlagModel.encode returns the embeddings directly as a numpy array
                # Convert numpy array to list of lists for JSON serialization/storage compatibility
                if isinstance(embeddings, np.ndarray):
                    all_embeddings.extend(embeddings.tolist())  # ← extend, not return
                else:
                    all_embeddings.extend(embeddings)
            return all_embeddings
        except Exception as e:
            logger.error(f"Embedding failed for {len(texts)} texts: {e}")
            raise

    def embed_query(self, query: str) -> List[float]:
        """
        Generate dense embeddings for a list of query.

        Args:
            texts: List of strings to embed.

        Returns:
            List of embeddings (lists of floats).
        """

        # Encode returns a 2D array if we pass a list,
        # so we wrap the query in a list and take the first vector.
        if not query:
            return []

        embedding = model.encode([query])

        # Convert numpy array to a list if needed

        if isinstance(embedding, np.ndarray):
            return embedding[0].tolist()

        else:
            return embedding[0]


# Example usage:
# svc = EmbeddingServices(model, batch_size=64)
# vectors = svc.embed_texts(["text1", "text2"])
# query_vec = svc.embed_query("example query")
