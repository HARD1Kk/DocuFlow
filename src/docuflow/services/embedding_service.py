import logging
from typing import List

import numpy as np

from docuflow.core.providers.embedding_provider import get_embedding_model

logger = logging.getLogger(__name__)


class EmbeddingServices:
    def __init__(self, model=get_embedding_model(), batch_size: int = 64):
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
                elif isinstance(embeddings, list):
                    all_embeddings.extend(embeddings)
                else:
                    raise ValueError(
                        "Embedding model output is in an unexpected format."
                    )
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
            logger.warning("Empty query passed to embed_query.")
            return []

        embedding = self.model.encode([query])

        # Convert numpy array to a list if needed
        try:
            if isinstance(embedding, np.ndarray):
                return embedding[0].tolist()
            elif isinstance(embedding, list):
                return embedding[0]
            else:
                raise ValueError("Query embedding is in an unexpected format.")

        except Exception as e:
            logger.error(f"Embedding failed for query: {query}. Error: {e}")
            raise  # Re-raise the exception after logging
