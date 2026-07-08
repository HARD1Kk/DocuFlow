import time
import uuid
from typing import List, Optional
from docuflow.schemas import RetrievedChunk
from docuflow.utils import get_logger, log_context
from docuflow.utils.logger import request_id_var

class RAGChain:
    def __init__(self, retriever, reranker=None, llm_service=None, validator=None):
        self.logger = get_logger(__name__)
        self.retriever = retriever
        self.reranker = reranker
        self.llm_service = llm_service
        self.validator = validator
        
        # Default token budget for context assembly
        self.max_context_tokens = 2000

    def query(self, query: str, top_k: int = 5) -> str:
        """Execute end-to-end RAG query pipeline with correlation ID and stage tracking."""
        query_id = request_id_var.get("") or f"q-{uuid.uuid4().hex[:8]}"
        
        with log_context(request_id=query_id, stage="Retrieval"):
            self.logger.info(f"RAG query started: query='{query}' (query_id={query_id})")
            
            # 1. Retrieve
            retrieved_chunks = self.retriever.retrieve(query, top_k=top_k)
            
            # 2. Rerank (if present)
            if self.reranker and retrieved_chunks:
                self.logger.info("Executing Reranker stage")
                retrieved_chunks = self.reranker.rerank(query, retrieved_chunks)

        with log_context(request_id=query_id, stage="Context Assembly"):
            self.logger.info("Assembling context for prompt")
            start_time = time.perf_counter()
            
            # 3. Context Assembly
            assembled_context = []
            context_tokens = 0
            dropped_chunks_count = 0
            
            for i, chunk in enumerate(retrieved_chunks):
                # Calculate tokens of this chunk
                chunk_tokens = len(chunk.content) // 4
                if context_tokens + chunk_tokens <= self.max_context_tokens:
                    assembled_context.append(chunk.content)
                    context_tokens += chunk_tokens
                    self.logger.info(f"Chunk index {i} accepted: tokens={chunk_tokens} (running_total={context_tokens})")
                else:
                    dropped_chunks_count += 1
                    self.logger.warning(
                        f"Chunk index {i} dropped due to context token budget: "
                        f"chunk_tokens={chunk_tokens}, context_tokens={context_tokens}, limit={self.max_context_tokens}"
                    )

            if dropped_chunks_count > 0:
                self.logger.warning(
                    f"Truncation event: {dropped_chunks_count} chunks were dropped during context assembly to fit token budget of {self.max_context_tokens}"
                )

            context_str = "\n\n---\n\n".join(assembled_context)
            prompt = f"Use the context below to answer the query.\n\nContext:\n{context_str}\n\nQuery: {query}\nAnswer:"
            prompt_tokens = len(prompt) // 4
            
            latency_ms = (time.perf_counter() - start_time) * 1000
            self.logger.info(
                f"Context assembly complete. Prompt tokens: {prompt_tokens} (latency={latency_ms:.2f}ms)",
                extra={"latency_ms": latency_ms, "input_tokens": prompt_tokens}
            )

        with log_context(request_id=query_id, stage="Generation"):
            self.logger.info(f"Calling LLM generation: model={getattr(self.llm_service, 'model_name', 'default')}")
            
            # 4. Generate
            gen_start = time.perf_counter()
            if not self.llm_service:
                self.logger.warning("No LLM service configured. Returning default mock answer.")
                answer = "Mock response - No LLM service configured."
                gen_latency = 0.0
                in_tokens = prompt_tokens
                out_tokens = len(answer) // 4
                cost = 0.0
            else:
                try:
                    answer = self.llm_service.generate(prompt)
                    gen_latency = (time.perf_counter() - gen_start) * 1000
                    
                    in_tokens = self.llm_service.last_input_tokens
                    out_tokens = self.llm_service.last_output_tokens
                    cost = self.llm_service.last_cost_usd
                    
                    self.logger.info(
                        f"LLM generation succeeded (latency={gen_latency:.2f}ms)",
                        extra={
                            "latency_ms": gen_latency,
                            "input_tokens": in_tokens,
                            "output_tokens": out_tokens,
                            "cost_usd": cost
                        }
                    )
                except Exception as e:
                    gen_latency = (time.perf_counter() - gen_start) * 1000
                    self.logger.error(
                        f"LLM generation failed: {e}",
                        exc_info=True,
                        extra={"latency_ms": gen_latency}
                    )
                    raise

        # 5. Validate (if present)
        if self.validator:
            with log_context(request_id=query_id, stage="Validation"):
                is_valid = self.validator.validate(query, context_str, answer)
                if not is_valid:
                    self.logger.warning(
                        "RAG answer validation failed. Triggering fallback response rejection.",
                        extra={"latency_ms": 0}
                    )
                    answer = "Response rejected: The generated answer failed quality audit checks."

        self.logger.info(f"RAG query finished: query='{query}' (query_id={query_id})")
        return answer
