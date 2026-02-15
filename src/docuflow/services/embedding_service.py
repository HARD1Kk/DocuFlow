import logging
from typing import List

import numpy as np
from FlagEmbedding import FlagModel

from utils.settings import settings

logger = logging.getLogger(__name__)


# Global model instance
model = FlagModel(
    settings.embedding_model,
    query_instruction_for_retrieval="Represent this sentence for searching relevant passages:",
    use_fp16=False,
)


def embed_texts(texts: List[str], batch_size: int = 64) -> List[List[float]]:
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

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            embeddings = model.encode(batch)
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
