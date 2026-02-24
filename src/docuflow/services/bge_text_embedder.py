import logging
from typing import List, Sequence

import numpy as np
from FlagEmbedding import FlagModel
from docuflow.interfaces.text_embedder import ITextEmbedder

from docuflow.configs.settings import settings

logger = logging.getLogger(__name__)


class BGETextEmbedder(ITextEmbedder):
    def __init__(self, batch_size: int = 64):
        self.batch_size = batch_size
        self.model = FlagModel(
            settings.embedding_model,
            query_instruction_for_retrieval=(
                "Represent this sentence for searching relevant passages:"
            ),
            use_fp16=settings.use_fp16,
        )

    def embed(self, texts: Sequence[str]) -> List[List[float]]:
        if not texts:
            return []

        try:
            all_embeddings = []

            for i in range(0, len(texts), self.batch_size):
                batch = texts[i : i + self.batch_size]
                embeddings = self.model.encode(list(batch))

                if isinstance(embeddings, np.ndarray):
                    all_embeddings.extend(embeddings.tolist())
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
