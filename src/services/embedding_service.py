from typing import List

import numpy as np
from FlagEmbedding import FlagModel

from utils.settings import settings

# Global model instance
model = FlagModel(settings.embedding_model, use_fp16=False)


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Generate dense embeddings for a list of texts.

    Args:
        texts: List of strings to embed.

    Returns:
        List of embeddings (lists of floats).
    """
    # FlagModel.encode returns the embeddings directly as a numpy array
    embeddings = model.encode(texts)

    # Convert numpy array to list of lists for JSON serialization/storage compatibility
    if isinstance(embeddings, np.ndarray):
        return embeddings.tolist()
    return embeddings  # type: ignore
