from typing import List, Sequence

import numpy as np
from FlagEmbedding import FlagModel
from docuflow.interfaces import ITextEmbedder

from docuflow.utils import get_logger
from docuflow.configs import settings


class BGETextEmbedder(ITextEmbedder):
    def __init__(self, batch_size: int = 64):
        self.logger = get_logger(__name__)

        self.logger.info("Initializing BGE text embedding phase")
        self.batch_size = batch_size

        self.logger.info(f"Using {settings.embedding_model} model")
        self.model = FlagModel(
            settings.embedding_model,
            query_instruction_for_retrieval=(
                "Represent this sentence for searching relevant passages:"
            ),
            use_fp16=settings.use_fp16,
        )

    def embed(self, texts: Sequence[str]) -> List[List[float]]:
        self.logger.info("Retrieving text")
        if not texts:
            self.logger.error("No texts provided, returning empty list.")
            return []

        try:
            all_embeddings = []
            self.logger.info("Started creating Embeddings")
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
            self.logger.info("Embeddings created Successfully")
            return all_embeddings

        except Exception as e:
            self.logger.error(f"Embedding failed for {len(texts)} texts: {e}")
            raise
