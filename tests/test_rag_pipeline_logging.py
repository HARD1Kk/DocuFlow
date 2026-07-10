import json

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


def test_end_to_end_rag_pipeline_logging(tmp_path):
    # 1. Setup local temporary paths for test logs
    test_log_file = tmp_path / "test_pipeline.log"
    settings.log_dir = tmp_path
    settings.log_file = "test_pipeline.log"

    # Force re-configure logging to target test file
    import docuflow.utils.logger as logger_module
    from docuflow.utils.logger import setup_logging

    logger_module._logging_configured = False
    setup_logging(level="INFO")

    logger = logger_module.get_logger("test_pipeline")

    # 2. Pipeline Initialization
    doc_file = tmp_path / "test_doc_logging.md"
    document_id = doc_file.name
    request_id = "test_query_logging_req_123"

    # Write mock file content to disk so the converter can read it
    doc_content = "This is the content of a test document. Section 1 covers RAG concepts. Section 2 covers logging."
    doc_file.write_text(doc_content, encoding="utf-8")

    with log_context(document_id=document_id, stage="Ingestion"):
        logger.info("Initializing logging pipeline test")

        # 3. Parser Step
        raw_doc = RawDocument(content=doc_content.encode("utf-8"), source=str(doc_file), metadata={"format": ".md"})
        parser = DocumentParser()
        parsed_text = parser.parse(raw_doc)
        assert parsed_text is not None

        # 4. Chunking Step
        config = ChunkingConfig(max_chunk_size=100, min_chunk_size=20)
        chunking_engine = ChunkingEngine(config=config, enable_enrichment=True)
        mock_llm = LLMService(mock=True)
        chunking_engine.enricher.llm_service = mock_llm

        chunk_batch = chunking_engine.chunk(
            content=parsed_text, document_type=DocumentType.MD, metadata={"source": document_id}
        )

        # 5. Embedding Step
        embedder = BGETextEmbedder(batch_size=2)
        chunks_content = [c.content for c in chunk_batch.chunks]
        embeddings = embedder.embed(chunks_content)
        assert len(embeddings) == len(chunks_content)

        # 6. Indexing Step
        db_path = tmp_path / "chroma_test_logging"
        vector_store = ChromaVectorStore(db_path=db_path, collection_name="test_collection")

        chunk_ids = [c.chunk_id for c in chunk_batch.chunks]
        metadatas = [c.to_dict() for c in chunk_batch.chunks]
        # Clean dict metadatas since chroma requires flat dicts
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

        # Indexing run 1
        vector_store.add(ids=chunk_ids, documents=chunks_content, metadata=metadatas, embeddings=embeddings)

    # 7. Query/Retrieval & Generation Step
    with log_context(request_id=request_id):
        retriever = VectorRetriever(embedder=embedder, vector_store=vector_store)
        reranker = Reranker()
        validator = ValidationLayer(llm_service=mock_llm)
        rag_chain = RAGChain(retriever=retriever, reranker=reranker, llm_service=mock_llm, validator=validator)

        answer = rag_chain.query("Explain RAG logging concepts", top_k=2)
        assert answer is not None

    # 8. Assertions on the structured JSON log output
    assert test_log_file.exists()

    with open(test_log_file, "r") as f:
        log_lines = f.readlines()

    assert len(log_lines) > 0

    stages_found = set()
    found_request_id = False
    found_document_id = False
    found_latency = False
    found_tokens = False

    for line in log_lines:
        data = json.loads(line)
        # Check basic keys
        assert "timestamp" in data
        assert "level" in data
        assert "logger" in data
        assert "message" in data

        # Trace stages
        stage = data.get("stage")
        if stage:
            stages_found.add(stage)

        # Trace IDs
        if data.get("request_id") == request_id:
            found_request_id = True
        if data.get("document_id") == document_id:
            found_document_id = True

        # Trace metrics
        if "latency_ms" in data:
            found_latency = True
        if "input_tokens" in data:
            found_tokens = True

    # Assert expected stages logged
    assert "Ingestion" in stages_found
    assert "Chunking" in stages_found
    assert "Embedding" in stages_found
    assert "Indexing" in stages_found
    assert "Retrieval" in stages_found
    assert "Reranking" in stages_found
    assert "Context Assembly" in stages_found
    assert "Generation" in stages_found
    assert "Validation" in stages_found

    assert found_request_id
    assert found_document_id
    assert found_latency
    assert found_tokens
