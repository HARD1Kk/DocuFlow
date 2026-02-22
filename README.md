# DocuFlow

DocuFlow is a modular, production-grade **Retrieval-Augmented Generation (RAG)** system built to ingest complex PDF documents with high fidelity. By converting PDFs to structured Markdown before ingestion, DocuFlow preserves document layout, tables, and headers — ensuring richer context for Large Language Models.

---

## 🚀 Features

- **Automatic Batch Processing**: Automatically detects and processes all PDF files placed in the `data/pdfs/` directory.
- **High-Fidelity Ingestion**: Uses `pymupdf4llm` to convert PDFs to Markdown, faithfully preserving tables, multi-column layouts, and document structure.
- **Smart Chunking**: Hierarchical text splitting based on Markdown headers (`#`, `##`, `###`) with a recursive character fallback for long sections.
- **Local Embeddings**: Generates dense vector embeddings using `BAAI/bge-small-en-v1.5` via `FlagEmbedding` with configurable batch processing.
- **Persistent Vector Storage**: Stores embeddings and rich metadata locally using **ChromaDB** with upsert support to avoid duplicate ingestion.
- **Vector Querying**: Semantic similarity search over stored document chunks.
- **Clean Abstraction Layer**: Pluggable `TextEmbedder` and `VectorStore` interfaces make it easy to swap embedding models or vector databases.
- **Structured Configuration**: Fully typed settings via `pydantic-settings`, overridable from a `.env` file.
- **Modern Stack**: Python 3.11+ codebase managed with `uv`, linted with `ruff`.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Core** | Python 3.11+ |
| **PDF Parsing** | PyMuPDF / PyMuPDF4LLM |
| **Text Splitting** | LangChain Text Splitters |
| **Embeddings** | FlagEmbedding (`BAAI/bge-small-en-v1.5`) |
| **Vector DB** | ChromaDB (Persistent) |
| **Configuration** | Pydantic Settings |
| **Package Manager** | uv |
| **Linter / Formatter** | Ruff |

---

## ⚙️ Installation

### Prerequisites
- Python 3.11+
- [`uv`](https://github.com/astral-sh/uv) package manager

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/HARD1Kk/DocuFlow.git
   cd DocuFlow
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Configure Settings (Optional)**

   Create a `.env` file in the project root to override any defaults:
   ```env
   LOG_LEVEL=INFO
   EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
   CHUNK_SIZE=800
   DB_PATH=chroma
   PDF_DIR=data/pdfs
   OUTPUT_DIR=data/markdown
   ```

---

## 📂 Project Structure

```
.
├── data/
│   ├── pdfs/                        # Place your source PDF files here
│   └── markdown/                    # Generated Markdown outputs
├── chroma/                          # ChromaDB persistent vector store
├── logs/                            # Application log files
├── src/
│   └── docuflow/
│       ├── configs/
│       │   └── settings.py          # Pydantic settings (loaded from .env)
│       ├── core/
│       │   ├── ingestion/
│       │   │   ├── ingestion_pipeline.py  # Main ingestion orchestration
│       │   │   ├── chunking.py            # Header-based text splitting
│       │   │   └── conversion.py          # PDF → Markdown conversion
│       │   ├── providers/
│       │   │   └── embedding_provider.py  # Embedding provider abstraction
│       │   └── rag/
│       │       └── rag.py                 # RAG retrieval logic
│       ├── interfaces/
│       │   ├── text_embedder.py     # Abstract TextEmbedder interface
│       │   └── vector_store.py      # Abstract VectorStore interface
│       ├── schemas/
│       │   ├── chunk.py             # Chunk data model
│       │   ├── document.py          # Document data model
│       │   └── rag.py               # RAG schema
│       ├── services/
│       │   ├── bge_text_embedder.py     # Concrete BGE embedding implementation
│       │   ├── chroma_vector_store.py   # Concrete ChromaDB implementation
│       │   ├── embedding_service.py     # Embedding service orchestration
│       │   └── llm_service.py           # LLM integration (WIP)
│       ├── utils/
│       │   ├── logger.py            # Logging setup
│       │   └── ...                  # Other utilities
│       └── main.py                  # Application entry point
├── test/                            # Pytest test suite
├── justfile                         # Task runner shortcuts
├── pyproject.toml                   # Project metadata & dependencies
└── .env                             # Local environment overrides (not committed)
```

---

## 🧩 Usage

1. **Place your PDFs** in the `data/pdfs/` folder.

2. **Run the ingestion pipeline**:
   ```bash
   just go
   ```
   This will:
   - Scan `data/pdfs/` for all PDF files.
   - Convert each PDF to Markdown using `pymupdf4llm` and save it to `data/markdown/`.
   - Split the Markdown into semantic chunks based on headers.
   - Generate embeddings using the BGE-small model (batched, with optional FP16).
   - Upsert chunks and embeddings into the local ChromaDB collection.

3. **Run tests**:
   ```bash
   just test
   ```

4. **Format & lint code**:
   ```bash
   just fmt
   ```

5. **Find dead code**:
   ```bash
   just dead
   ```

---

## ⚙️ Configuration Reference

All settings are defined in `src/docuflow/configs/settings.py` and can be overridden via `.env`:

| Setting | Default | Description |
|---|---|---|
| `pdf_dir` | `data/pdfs` | Directory to scan for PDF files |
| `output_dir` | `data/markdown` | Output directory for generated Markdown |
| `log_dir` | `logs/` | Directory for log files |
| `log_file` | `app.log` | Log file name |
| `db_path` | `chroma/` | ChromaDB persistence directory |
| `embedding_model` | `BAAI/bge-small-en-v1.5` | HuggingFace embedding model |
| `chunk_size` | `800` | Maximum characters per chunk |
| `use_fp16` | `False` | Use FP16 precision for embeddings |

---

## 🏗️ Architecture

DocuFlow is built around clean interface abstractions to keep components decoupled and swappable:

```
PDF Files
    │
    ▼
[Conversion]  ──  pymupdf4llm  ──►  Markdown Text
    │
    ▼
[Chunking]    ──  LangChain    ──►  Semantic Chunks
    │
    ▼
[TextEmbedder]  (interface)
    │
    └── BGETextEmbedder  ──  FlagEmbedding  ──►  Dense Vectors
    │
    ▼
[VectorStore]  (interface)
    │
    └── ChromaVectorStore  ──  ChromaDB  ──►  Persisted Embeddings
```

Both `TextEmbedder` and `VectorStore` are abstract base classes defined in `src/docuflow/interfaces/`. Concrete implementations live in `src/docuflow/services/`, making it trivial to plug in a different embedding model or vector database without touching the pipeline logic.

---

## 🚧 Roadmap

- [x] High-fidelity PDF → Markdown ingestion
- [x] Header-based smart chunking
- [x] Local embedding pipeline (BGE-small) with batch processing
- [x] Persistent vector storage (ChromaDB)
- [x] Semantic similarity querying
- [x] Pluggable `TextEmbedder` / `VectorStore` interface layer
- [ ] RAG retrieval chain (fetch relevant context for a query)
- [ ] LLM integration (Gemini / GPT-4 / Llama 3)
- [ ] CLI interface for querying documents
- [ ] Web UI for chat-based interaction

---
