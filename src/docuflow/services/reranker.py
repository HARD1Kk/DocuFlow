import random
import time
from typing import List

from docuflow.schemas import RetrievedChunk
from docuflow.utils import get_logger, log_context


class Reranker:
    def __init__(self):
        self.logger = get_logger(__name__)

    def rerank(self, query: str, chunks: List[RetrievedChunk]) -> List[RetrievedChunk]:
        """Rerank retrieved chunks based on simulated cross-encoder scores."""
        with log_context(stage="Reranking"):
            if not chunks:
                self.logger.warning("Empty chunk list provided to Reranker.")
                return []

            self.logger.info(f"Reranking started for query: '{query}' with {len(chunks)} chunks")
            start_time = time.perf_counter()

            # Simulate processing delay
            time.sleep(random.uniform(0.05, 0.15))

            reranked = []
            for chunk in chunks:
                # Simulate a score boost/change
                boost = random.uniform(-0.1, 0.2)
                new_score = min(1.0, max(0.0, chunk.score + boost))

                self.logger.info(
                    f"Reranked chunk: score_before={chunk.score:.4f}, score_after={new_score:.4f} (diff={boost:+.4f})"
                )

                reranked.append(RetrievedChunk(content=chunk.content, score=new_score, metadata=chunk.metadata))

            # Sort by new score descending
            reranked.sort(key=lambda x: x.score, reverse=True)

            latency_ms = (time.perf_counter() - start_time) * 1000
            self.logger.info(f"Reranking completed in {latency_ms:.2f}ms", extra={"latency_ms": latency_ms})

            return reranked
