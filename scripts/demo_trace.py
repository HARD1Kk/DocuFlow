#!/usr/bin/env python3
import json
import shutil

# Fix python path to find local docuflow package
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from docuflow.configs import settings
from docuflow.processing.chunking import ChunkingEngine
from docuflow.processing.parsers import DocumentParser
from docuflow.processing.rag.rag import RAGChain
from docuflow.processing.rag.validation import ValidationLayer
from docuflow.schemas import RawDocument
from docuflow.schemas.chunk import ChunkingConfig, DocumentType
from docuflow.services.bge_text_embedder import BGETextEmbedder
from docuflow.services.chroma_vector_store import ChromaVectorStore
from docuflow.services.llm_service import LLMService
from docuflow.services.reranker import Reranker
from docuflow.services.retriever_chain import VectorRetriever
from docuflow.utils import log_context


def run_demo_trace():
    print("================================================================================")
    print("               DOCUFLOW PRODUCTION-GRADE TRACING & LOGGING DEMO")
    print("================================================================================")

    # 1. Setup local temporary path for demo logs
    demo_log_file = Path("logs/demo_pipeline.log")
    if demo_log_file.exists():
        demo_log_file.unlink()

    # Configure setting's log path for this demo run
    settings.log_file = "demo_pipeline.log"
    settings.LOG_LEVEL = "INFO"

    import docuflow.utils.logger as logger_module
    from docuflow.utils.logger import setup_logging

    logger_module._logging_configured = False
    setup_logging(level="INFO")

    logger = logger_module.get_logger("demo_trace")

    # Generate document and request correlation IDs
    doc_correlation_id = f"doc-{uuid.uuid4().hex[:8]}.md"
    query_correlation_id = f"req-{uuid.uuid4().hex[:8]}"

    # Document contents (purposely keep some sections small to demonstrate warning drop logs!)
    document_content = """# Production Logging in AI Systems

Monitoring and logging are essential steps for any production application, especially in complex pipelines like RAG.

## Short Section
Short.

## Deep Dive into ContextVars
Explicit parameter passing couples business logic to telemetry metadata. Python's contextvars library solves this by maintaining task-local and thread-local state namespaces. This lets correlation IDs flow implicitly across sync/async boundaries.
"""

    # Write mock file content to disk
    Path(doc_correlation_id).write_text(document_content, encoding="utf-8")

    print(f"\n[Step 1] Ingesting & Chunking Document (doc_id={doc_correlation_id})")
    with log_context(document_id=doc_correlation_id, stage="Ingestion"):
        logger.info("Starting document ingestion demo run")

        # Parse
        raw_doc = RawDocument(content=document_content, source=doc_correlation_id, metadata={"format": ".md"})
        parser = DocumentParser()
        parsed_text = parser.parse(raw_doc)

        # Chunking (with metadata enrichment using Mock LLM)
        config = ChunkingConfig(max_chunk_size=150, min_chunk_size=30)
        chunking_engine = ChunkingEngine(config=config, enable_enrichment=True)
        mock_llm = LLMService(mock=False)
        chunking_engine.enricher.llm_service = mock_llm

        chunk_batch = chunking_engine.chunk(
            content=parsed_text, document_type=DocumentType.MD, metadata={"source": doc_correlation_id}
        )

        # Embed
        embedder = BGETextEmbedder(batch_size=4)
        chunks_content = [c.content for c in chunk_batch.chunks]
        embeddings = embedder.embed(chunks_content)

        # Index in Vector Store
        db_path = Path("chroma_demo_db")
        if db_path.exists():
            shutil.rmtree(db_path)

        vector_store = ChromaVectorStore(db_path=db_path, collection_name="demo_collection")
        chunk_ids = [c.chunk_id for c in chunk_batch.chunks]
        metadatas = [c.to_dict() for c in chunk_batch.chunks]

        # Clean dictionaries for Chroma
        for m in metadatas:
            if "keywords" in m:
                m["keywords"] = ", ".join(m["keywords"])
            if "hypothetical_questions" in m:
                m["hypothetical_questions"] = ", ".join(m["hypothetical_questions"])
            if "metadata" in m:
                del m["metadata"]
            if "embedding" in m:
                del m["embedding"]
            if "content_type" in m:
                m["content_type"] = str(m["content_type"])
            if "document_type" in m:
                m["document_type"] = str(m["document_type"])

        # Add to index (First add)
        vector_store.add(ids=chunk_ids, documents=chunks_content, metadata=metadatas, embeddings=embeddings)

        # Add again to demonstrate duplicate warning logging
        logger.info("Triggering simulated duplicate add to demonstrate silent overwrite warning:")
        vector_store.add(ids=chunk_ids, documents=chunks_content, metadata=metadatas, embeddings=embeddings)

    print(f"\n[Step 2] Executing Query (req_id={query_correlation_id})")
    with log_context(request_id=query_correlation_id):
        retriever = VectorRetriever(embedder=embedder, vector_store=vector_store)
        reranker = Reranker()
        validator = ValidationLayer(llm_service=mock_llm)

        rag_chain = RAGChain(retriever=retriever, reranker=reranker, llm_service=mock_llm, validator=validator)

        # Ask a query that gets context
        answer = rag_chain.query("How do contextvars help in RAG systems?", top_k=2)
        print(f"\nFinal Answer:\n> {answer}\n")

    # 9. Read the JSON log file and print the correlation trace
    print("================================================================================")
    print("               JSON LOG TRACE TIMELINE FOR DOCUMENT INGESTION")
    print(f"               (Filtered by document_id={doc_correlation_id})")
    print("================================================================================")

    with open(demo_log_file, "r") as f:
        for line in f:
            data = json.loads(line)
            if data.get("document_id") == doc_correlation_id:
                stage = data.get("stage", "Unknown")
                level = data.get("level", "INFO")
                msg = data.get("message", "")

                # Check for performance stats
                perf_info = []
                for attr in ["latency_ms", "input_tokens", "output_tokens", "cost_usd"]:
                    if attr in data:
                        perf_info.append(f"{attr}={data[attr]}")
                perf_str = f" | {', '.join(perf_info)}" if perf_info else ""

                print(f"[{data['timestamp']}] [{level:<7}] [Stage: {stage:<19}] {msg}{perf_str}")

    print("\n================================================================================")
    print("               JSON LOG TRACE TIMELINE FOR USER QUERY")
    print(f"               (Filtered by request_id={query_correlation_id})")
    print("================================================================================")

    with open(demo_log_file, "r") as f:
        for line in f:
            data = json.loads(line)
            if data.get("request_id") == query_correlation_id:
                stage = data.get("stage", "Unknown")
                level = data.get("level", "INFO")
                msg = data.get("message", "")

                perf_info = []
                for attr in ["latency_ms", "input_tokens", "output_tokens", "cost_usd"]:
                    if attr in data:
                        perf_info.append(f"{attr}={data[attr]}")
                perf_str = f" | {', '.join(perf_info)}" if perf_info else ""

                print(f"[{data['timestamp']}] [{level:<7}] [Stage: {stage:<19}] {msg}{perf_str}")

    # Cleanup demo database and log file
    if db_path.exists():
        shutil.rmtree(db_path)
    if demo_log_file.exists():
        demo_log_file.unlink()
    if Path(doc_correlation_id).exists():
        Path(doc_correlation_id).unlink()


if __name__ == "__main__":
    run_demo_trace()
