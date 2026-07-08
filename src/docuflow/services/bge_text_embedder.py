from typing import List, Sequence

import numpy as np
from FlagEmbedding import FlagModel

from docuflow.configs import settings
from docuflow.interfaces import ITextEmbedder
from docuflow.utils import get_logger


class BGETextEmbedder(ITextEmbedder):
    def __init__(self, batch_size: int = 64):
        self.logger = get_logger(__name__)

        self.logger.info("Initializing BGE text embedding phase")
        self.batch_size = batch_size

        self.logger.info(f"Using {settings.embedding_model} model")
        self.model = FlagModel(
            settings.embedding_model,
            query_instruction_for_retrieval=("Represent this sentence for searching relevant passages:"),
            use_fp16=settings.use_fp16,
        )

    def embed(self, texts: Sequence[str]) -> List[List[float]]:
        import time
        from docuflow.utils import log_context

        with log_context(stage="Embedding"):
            if not texts:
                self.logger.warning("No texts provided to embed, returning empty list.")
                return []

            self.logger.info(
                f"Embedding started: count={len(texts)}, batch_size={self.batch_size}, model={settings.embedding_model}"
            )

            start_time = time.perf_counter()
            try:
                all_embeddings = []
                for i in range(0, len(texts), self.batch_size):
                    batch_start = time.perf_counter()
                    batch = list(texts[i : i + self.batch_size])
                    embeddings = self.model.encode(batch)

                    batch_latency = (time.perf_counter() - batch_start) * 1000
                    self.logger.info(
                        f"Embedded batch: size={len(batch)} (latency={batch_latency:.2f}ms)",
                        extra={"latency_ms": batch_latency}
                    )

                    if isinstance(embeddings, np.ndarray):
                        all_embeddings.extend(embeddings.tolist())
                    elif isinstance(embeddings, list):
                        all_embeddings.extend(embeddings)
                    else:
                        raise ValueError("Embedding model output is in an unexpected format.")

                total_latency = (time.perf_counter() - start_time) * 1000
                approx_tokens = sum(len(t) // 4 for t in texts)
                self.logger.info(
                    f"Embedding finished: embedded {len(texts)} texts successfully (total_latency={total_latency:.2f}ms)",
                    extra={
                        "latency_ms": total_latency,
                        "input_tokens": approx_tokens,
                        "output_tokens": approx_tokens,
                    }
                )
                return all_embeddings

            except Exception as e:
                total_latency = (time.perf_counter() - start_time) * 1000
                self.logger.error(
                    f"Embedding failed: {e}",
                    exc_info=True,
                    extra={"latency_ms": total_latency}
                )
                raise
