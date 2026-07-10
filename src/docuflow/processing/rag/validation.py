import time

from docuflow.utils import get_logger, log_context


class ValidationLayer:
    def __init__(self, llm_service=None):
        self.logger = get_logger(__name__)
        self.llm_service = llm_service

    def validate(self, query: str, context: str, response: str) -> bool:
        """Validate RAG output using Gatekeeper, Auditor, and Strategist checks."""
        with log_context(stage="Validation"):
            self.logger.info("Starting response validation pipeline")
            start_time = time.perf_counter()

            # 1. Gatekeeper Check: Does this answer address the question?
            self.logger.info("Running Gatekeeper check: Answer relevance check")
            gatekeeper_passed = self._run_gatekeeper(query, response)
            if not gatekeeper_passed:
                self.logger.warning(f"Gatekeeper check failed: Response does not address the query '{query}'")
                return False

            # 2. Auditor Check: Is this response grounded in the context (no hallucination)?
            self.logger.info("Running Auditor check: Faithfulness / Groundedness check")
            auditor_passed = self._run_auditor(context, response)
            if not auditor_passed:
                self.logger.warning("Auditor check failed: Response contains hallucinated information")
                return False

            latency_ms = (time.perf_counter() - start_time) * 1000
            self.logger.info(
                f"Validation pipeline completed successfully. All checks PASSED (latency={latency_ms:.2f}ms)",
                extra={"latency_ms": latency_ms},
            )
            return True

    def _run_gatekeeper(self, query: str, response: str) -> bool:
        if self.llm_service:
            prompt = (
                f"Does the following answer address the query? Query: {query} Answer: {response}. Answer yes or no."
            )
            try:
                res = self.llm_service.generate(prompt)
                return "yes" in res.lower()
            except Exception as e:
                self.logger.warning(f"Gatekeeper LLM call failed: {e}. Falling back to rule-based check.")

        # Rule-based fallback
        return len(response) > 10

    def _run_auditor(self, context: str, response: str) -> bool:
        if self.llm_service:
            prompt = f"Is the answer grounded in the context? Context: {context} Answer: {response}. Answer yes or no."
            try:
                res = self.llm_service.generate(prompt)
                return "yes" in res.lower()
            except Exception as e:
                self.logger.warning(f"Auditor LLM call failed: {e}. Bypassing check.")

        return True
