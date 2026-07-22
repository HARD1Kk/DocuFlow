# DocuFlow Code File Reference

This document provides a comprehensive directory of every codebase file in DocuFlow. It outlines the purpose, design, class/function entrypoints, and internal mechanics of each module.

---

## 1. Composition Root & Configs

### [main.py](file:///home/hardik/projects/DocuFlow/src/docuflow/main.py)
*   **Purpose**: The main orchestration script and Composition Root for DocuFlow document ingestion.
*   **Details**: Initializes concrete services, constructs the dependency injection mapping, scans the `data/input` directory, processes each file (running loaders, converters, cleaners, chunkers, embedders), saves output Markdown and JSON debug chunks, and registers vectors in ChromaDB.
*   **Key Functions**:
    *   `create_app()`: Wire dependencies together (Parser, ChunkingEngine, LoaderFactory, Embedder, VectorStore).
    *   `main()`: Main pipeline loop covering validation, ingestion, chunking, metadata enrichment, embedding generation, and vector indexing.

### [configs/settings.py](file:///home/hardik/projects/DocuFlow/src/docuflow/configs/settings.py)
*   **Purpose**: Configuration management using Pydantic Settings.
*   **Details**: Loads environment settings from a `.env` file, supplying defaults for folder structures (`data/input`, `data/markdown`), database directories, active model setups, and credentials.
*   **Key Class**: `Settings`

---

## 2. Interfaces Layer (`interfaces/`)
Declares abstract contracts (interfaces) using Python's `abc` package to guarantee decoupling between orchestrators and concrete implementations.

*   [interfaces/data_source.py](file:///home/hardik/projects/DocuFlow/src/docuflow/interfaces/data_source.py): Declares the base contract `IDatasource` for validating and loading files into RawDocuments.
*   [interfaces/loader.py](file:///home/hardik/projects/DocuFlow/src/docuflow/interfaces/loader.py): Defines the document loading contract `ILoader`.
*   [interfaces/converter.py](file:///home/hardik/projects/DocuFlow/src/docuflow/interfaces/converter.py): Defines `BaseConverter` for extracting normalized markdown text from RawDocuments.
*   [interfaces/chunker.py](file:///home/hardik/projects/DocuFlow/src/docuflow/interfaces/chunker.py): Defines `BaseChunker` for document splitters.
*   [interfaces/ocr.py](file:///home/hardik/projects/DocuFlow/src/docuflow/interfaces/ocr.py): Defines `IOCRModel` for OCR engines.
*   [interfaces/text_embedder.py](file:///home/hardik/projects/DocuFlow/src/docuflow/interfaces/text_embedder.py): Defines `ITextEmbedder` for generating numeric vectors.
*   [interfaces/vector_store.py](file:///home/hardik/projects/DocuFlow/src/docuflow/interfaces/vector_store.py): Defines `IVectorStore` for vector database operations (add, query, delete).
*   [interfaces/retriever.py](file:///home/hardik/projects/DocuFlow/src/docuflow/interfaces/retriever.py): Defines `IRetriever` for semantic search.

---

## 3. Data Source Layer (`data_source/`)
Responsible for reading target files as raw bytes and packaging them into standard data structures.

*   [data_source/base_loader.py](file:///home/hardik/projects/DocuFlow/src/docuflow/data_source/base_loader.py): Implements generic file validation and loads raw bytes into a `RawDocument`.
*   [data_source/loader_factory.py](file:///home/hardik/projects/DocuFlow/src/docuflow/data_source/loader_factory.py): Stores a map of extensions to concrete loaders, resolving loaders at runtime.
*   [data_source/document_loader.py](file:///home/hardik/projects/DocuFlow/src/docuflow/data_source/document_loader.py): Loader for text-based files: `.pdf`, `.docx`, `.txt`, `.md`.
*   [data_source/image_loader.py](file:///home/hardik/projects/DocuFlow/src/docuflow/data_source/image_loader.py): Loader for image files: `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`.
*   [data_source/spreadsheet_loader.py](file:///home/hardik/projects/DocuFlow/src/docuflow/data_source/spreadsheet_loader.py): Loader for tabular data sheets: `.xlsx`, `.csv`, `.tsv`.

---

## 4. Processing & Ingestion Layer (`processing/`)
Translates raw file bytes to layout-aware markdown, splits them into logical chunks, and enriches them.

### Converters (`processing/converters/`)
*   [processing/converters/converter_factory.py](file:///home/hardik/projects/DocuFlow/src/docuflow/processing/converters/converter_factory.py): Resolves file extensions to specific converters at runtime.
*   [processing/converters/document_converter.py](file:///home/hardik/projects/DocuFlow/src/docuflow/processing/converters/document_converter.py): Performs document-to-markdown translation:
    *   PDF: PyMuPDF4LLM with layout preservation.
    *   DOCX: Pandoc subprocess call.
    *   Spreadsheets: Pandas loader that outputs Markdown tables.
    *   TXT/MD: Standard UTF-8 text read.
*   [processing/converters/image_converter.py](file:///home/hardik/projects/DocuFlow/src/docuflow/processing/converters/image_converter.py): Converts images to markdown text via OCR.
*   [processing/converters/convert_image_text.py](file:///home/hardik/projects/DocuFlow/src/docuflow/processing/converters/convert_image_text.py): Houses concrete OCR engines:
    *   `DoclingModel`: Advanced structured OCR (layout-aware, handles tables).
    *   `EasyOCRModel`: Offline OCR engine for text extraction.
    *   `PaddleOCRModel`: High-accuracy offline Chinese/English OCR engine.

### Parsers (`processing/parsers/`)
*   [processing/parsers/document_parser.py](file:///home/hardik/projects/DocuFlow/src/docuflow/processing/parsers/document_parser.py): Integrates with `ConverterFactory` to retrieve markdown text and runs `TextCleaner`.
*   [processing/parsers/image_parser.py](file:///home/hardik/projects/DocuFlow/src/docuflow/processing/parsers/image_parser.py): Specific parser to convert and return image text.
*   [processing/parsers/structure_analyzer.py](file:///home/hardik/projects/DocuFlow/src/docuflow/processing/parsers/structure_analyzer.py): Cleans Pandoc layout anchors (`{...}`), empty headings, and excessive white lines.

### Chunking (`processing/chunking/`)
*   [processing/chunking/base_chunker.py](file:///home/hardik/projects/DocuFlow/src/docuflow/processing/chunking/base_chunker.py): Abstract base chunker contract providing token estimation and ID builders.
*   [processing/chunking/chunking_engine.py](file:///home/hardik/projects/DocuFlow/src/docuflow/processing/chunking/chunking_engine.py): Main facade routing texts to specific splitters and calling the enricher.
*   [processing/chunking/markdown_chunker.py](file:///home/hardik/projects/DocuFlow/src/docuflow/processing/chunking/markdown_chunker.py): Preserves layout sections, tables, lists, and headings using `StructureDetectors`.
*   [processing/chunking/detectors.py](file:///home/hardik/projects/DocuFlow/src/docuflow/processing/chunking/detectors.py): Regular expression-based structural block detectors:
    *   `HeadingDetector`: Finds headings (`#` to `######`).
    *   `TableDetector`: Detects markdown tables.
    *   `ListDetector`: Identifies ordered/unordered lists.
    *   `CodeBlockDetector`: Locates markdown code blocks.
*   [processing/chunking/code_chunker.py](file:///home/hardik/projects/DocuFlow/src/docuflow/processing/chunking/code_chunker.py): Intact class, method, and function segmentation for languages like Python, JavaScript, Java, Go.
*   [processing/chunking/spreadsheet_chunker.py](file:///home/hardik/projects/DocuFlow/src/docuflow/processing/chunking/spreadsheet_chunker.py): Splits sheets row-by-row, duplicating headers into each chunk.
*   [processing/chunking/image_chunker.py](file:///home/hardik/projects/DocuFlow/src/docuflow/processing/chunking/image_chunker.py): Groups OCR line listings into chunks when maximum limits are hit.
*   [processing/chunking/metadata_enricher.py](file:///home/hardik/projects/DocuFlow/src/docuflow/processing/chunking/metadata_enricher.py): Appends keywords (rule-based), summaries, and hypothetical questions (via Groq LLM or rule-based fallbacks).
*   [processing/chunking/chunk_builder.py](file:///home/hardik/projects/DocuFlow/src/docuflow/processing/chunking/chunk_builder.py): Placeholder script reserved for downstream chunk metadata builds.

### Ingestion Helper (`processing/ingestion/`)
*   [processing/ingestion/__init__.py](file:///home/hardik/projects/DocuFlow/src/docuflow/processing/ingestion/__init__.py): Exposes `save_markdown`, ensuring target parent folders exist.

### RAG Orchestrator (`processing/rag/`)
*   [processing/rag/rag.py](file:///home/hardik/projects/DocuFlow/src/docuflow/processing/rag/rag.py): Execution chain coordinating retrieval, cross-encoder reranking, prompt mapping, token budgeting, LLM generation, and validation.
*   [processing/rag/validation.py](file:///home/hardik/projects/DocuFlow/src/docuflow/processing/rag/validation.py): Validation layer executing two LLM validation checks:
    *   `Gatekeeper`: Confirms answer relevance to user query.
    *   `Auditor`: Verifies answer is grounded in retrieved context (hallucination detection).

---

## 5. Schemas Layer (`schemas/`)
Defines Pydantic models and Python Dataclasses to enforce type safety across layers.

*   [schemas/raw_document.py](file:///home/hardik/projects/DocuFlow/src/docuflow/schemas/raw_document.py): Dataclass representing raw, loaded file bytes with minimal source metadata.
*   [schemas/document.py](file:///home/hardik/projects/DocuFlow/src/docuflow/schemas/document.py): Pydantic model for storage structures in ChromaDB.
*   [schemas/chunk.py](file:///home/hardik/projects/DocuFlow/src/docuflow/schemas/chunk.py): Models for chunked elements, batches, and chunker configuration flags.
*   [schemas/retrieved_chunk.py](file:///home/hardik/projects/DocuFlow/src/docuflow/schemas/retrieved_chunk.py): Model representing query hits from the database, storing scores and content.
*   [schemas/ocr.py](file:///home/hardik/projects/DocuFlow/src/docuflow/schemas/ocr.py): Config settings for the PaddleOCR backend.
*   [schemas/rag.py](file:///home/hardik/projects/DocuFlow/src/docuflow/schemas/rag.py): Placeholder schema for RAG interactions.

---

## 6. Services Layer (`services/`)
Concrete implementation of API adapters, embedding generation, vector indexes, and LLM integrations.

*   [services/bge_text_embedder.py](file:///home/hardik/projects/DocuFlow/src/docuflow/services/bge_text_embedder.py): Generates numeric vectors using FlagEmbedding models (`BAAI/bge-small-en-v1.5`) with batch processing.
*   [services/chroma_vector_store.py](file:///home/hardik/projects/DocuFlow/src/docuflow/services/chroma_vector_store.py): Encapsulates ChromaDB persistent collection writes (upsert), semantic queries, and deletions.
*   [services/llm_service.py](file:///home/hardik/projects/DocuFlow/src/docuflow/services/llm_service.py): Wraps connection parameters to Groq Cloud / OpenAI, tracking token counts, latency, and costs, with a simulated offline mode.
*   [services/reranker.py](file:///home/hardik/projects/DocuFlow/src/docuflow/services/reranker.py): Performs cross-encoder ranking adjustments.
*   [services/retriever_chain.py](file:///home/hardik/projects/DocuFlow/src/docuflow/services/retriever_chain.py): Combines query embeddings with vector stores to return the top `k` semantic hits.
*   [services/embedding_service.py](file:///home/hardik/projects/DocuFlow/src/docuflow/services/embedding_service.py): Reference wrapper for embedding services.

---

## 7. Utilities (`utils/`)
Shared services, log tracing, checks, and offline verification helpers.

*   [utils/logger.py](file:///home/hardik/projects/DocuFlow/src/docuflow/utils/logger.py): Configures structured JSON logging and human-readable terminal output. Binds tracing parameters (`request_id`, `document_id`, `stage`) using `ContextVars`.
*   [utils/text_cleaner.py](file:///home/hardik/projects/DocuFlow/src/docuflow/utils/text_cleaner.py): Grammatical correction wrapper utilizing `Gramformer` (when available).
*   [utils/dependency_checks.py](file:///home/hardik/projects/DocuFlow/src/docuflow/utils/dependency_checks.py): Validates optional heavy dependencies (PaddleOCR, EasyOCR) and logs diagnostic warnings.
*   [utils/bootstrap.py](file:///home/hardik/projects/DocuFlow/src/docuflow/utils/bootstrap.py): Automatically constructs necessary project directory structures (`data/input`, `data/markdown`, `logs`).
*   [utils/chunking_quality_evaluator.py](file:///home/hardik/projects/DocuFlow/src/docuflow/utils/chunking_quality_evaluator.py): Evaluation tool that generates statistics and scores chunking quality.
*   [utils/load_file.py](file:///home/hardik/projects/DocuFlow/src/docuflow/utils/load_file.py): Low-level helper to load file data.

---

## 8. Scripts & Tests Reference

### Scripts
*   [scripts/test_retrieval.py](file:///home/hardik/projects/DocuFlow/scripts/test_retrieval.py): End-to-end command-line tester for retrieving and generating RAG answers.
*   [scripts/verify_chromadb_index.py](file:///home/hardik/projects/DocuFlow/scripts/verify_chromadb_index.py): Utility to query ChromaDB and print document counts.
*   [scripts/demo_trace.py](file:///home/hardik/projects/DocuFlow/scripts/demo_trace.py): Demonstrates context variable logging traces.
*   [scripts/demo_live_llm.py](file:///home/hardik/projects/DocuFlow/scripts/demo_live_llm.py): Verifies API connectivity with the Groq Cloud endpoint.

### Tests
*   `tests/DataSourceLayer/test_document_loader.py`: Verifies DocumentLoader capabilities.
*   `tests/test_chunking_quality.py`: Evaluates structure-aware chunk integrity.
*   `tests/test_embedding_service.py`: Tests semantic embedding generation.
*   `tests/test_vector_store.py`: Tests ChromaDB integration.
*   `tests/test_similarity.py`: Validates cosine-similarity distances.
*   `tests/test_retriever.py`: Tests the VectorRetriever.
*   `tests/test_rag_pipeline_logging.py`: Asserts JSON structured logs and trace contexts.
*   `tests/test_show_actual_content.py`: Diagnostic test to verify extraction quality.
