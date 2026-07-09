# DocuFlow

DocuFlow is a modern Retrieval-Augmented Generation (RAG) system designed to process complex PDF documents with precision. By converting PDFs to structured Markdown before ingestion, DocuFlow preserves document layout, tables, and headers, ensuring higher-quality context for Large Language Models.

---

## Features

- **Multi-format Support** — PDF, DOCX, TXT, MD, Images (PNG/JPG), Spreadsheets (XLS/XLSX, CSV/TSV)
- **High-Fidelity Conversion** — Converts documents to structured Markdown preserving layout, tables, and headers
- **Smart Chunking** — Hierarchical text splitting based on Markdown headers (`#`, `##`, `###`) with recursive fallback for long sections
- **Structure Detection** — Automatically detects headings, tables, lists, and code blocks
- **Dual OCR** — Docling + EasyOCR for image text extraction
- **Metadata Enrichment** — Summaries, keywords, and hypothetical questions for better retrieval
- **Local Embeddings** — BAAI/bge-small-en-v1.5 via FlagEmbedding with configurable batch processing
- **Persistent Vector Storage** — ChromaDB with upsert support
- **Clean Abstraction** — Pluggable interfaces for TextEmbedder and VectorStore
- **Structured Config** — Pydantic settings via pydantic-settings, overridable from .env

---

## Tech Stack

| Layer | Technology |
|-------|-------------|
| Core | Python 3.11+ |
| PDF Parsing | PyMuPDF / PyMuPDF4LLM |
| Document Processing | python-docx, pandas, openpyxl |
| OCR | EasyOCR, Docling |
| Text Splitting | LangChain Text Splitters |
| Embeddings | FlagEmbedding (BAAI/bge-small-en-v1.5) |
| Vector DB | ChromaDB (Persistent) |
| Configuration | Pydantic Settings |
| Package Manager | uv |
| Linter / Formatter | Ruff, MyPy |

---

## Installation

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager

### Steps

```bash
# Clone the repository
git clone https://github.com/HARD1Kk/DocuFlow.git
cd DocuFlow

# Install dependencies
uv sync

# Create .env file in the project root:
LOG_LEVEL=INFO
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
DB_PATH=chroma

# Add LLM Keys (required for live metadata enrichment and generation)
GROQ_API_KEY="your_groq_api_key"
```

---

## Quick Start

### 1. Document Ingestion
Place files (PDF, Word, Images, etc.) in the `data/input` directory and run:

```bash
# Run ingestion (parses documents, generates summaries/questions, writes JSON audits, indexes vectors)
just go
```

#### Ingestion Outputs:
* **Markdown Text:** Saved to `data/markdown/{filename}.md`
* **Local Audit JSON:** Saved to `data/markdown/{filename}_chunks.json` (contains the exact list of chunks, summaries, keywords, and hypothetical questions)
* **Vector Index:** Indexed into ChromaDB persistent storage under path `chroma/`

---

## Retrieval & Querying

To query the database and test the retrieval/LLM generation quality:

```bash
# Test retrieval with a natural query
uv run python scripts/test_retrieval.py --query "What is the B.Tech qualification and CGPA of the developer?"
```

This runs the complete pipeline:
1. **Retrieve:** Queries ChromaDB for the semantically closest chunk.
2. **Rerank:** Sorts retrieved matches through the reranking processor.
3. **Generate:** Prompts Groq's live Llama-3.3-70b-versatile LLM using the retrieved context to answer your question.

---

## Architecture

```
src/docuflow/
├── data_source/           # Data loaders
│   ├── document_loader.py    # PDF, DOCX, TXT, MD
│   ├── image_loader.py       # PNG, JPG
│   └── spreadsheet_loader.py # XLS, XLSX, CSV
│
├── processing/
│   ├── chunking/         # Chunking engine
│   │   ├── base_chunker.py      # Abstract base
│   │   ├── chunking_engine.py   # Main orchestrator
│   │   ├── markdown_chunker.py  # Markdown-specific
│   │   ├── code_chunker.py      # Code blocks
│   │   ├── image_chunker.py     # OCR'd images
│   │   ├── spreadsheet_chunker.py
│   │   └── detectors.py         # Structure detection
│   │
│   ├── converters/       # Format conversion
│   │   ├── document_converter.py
│   │   ├── image_converter.py
│   │   └── convert_image_text.py  # OCR (Docling + EasyOCR)
│   │
│   ├── parsers/          # Text extraction
│   │   ├── document_parser.py
│   │   ├── image_parser.py
│   │   └── structure_analyzer.py
│   │
│   └── rag/              # RAG Chain orchestration
│       ├── validation.py     # RAG validation (Gatekeeper, Auditor, Strategist)
│       └── rag.py            # Context assembly and LLM querying
│
├── interfaces/           # Abstract interfaces
├── schemas/              # Pydantic models
├── services/             # Concrete services (Chroma, BGE, LLM, Reranker)
└── utils/                # Helpers & diagnostics
```

---

## Testing

```bash
# Run the complete test suite (executes mock offline validations)
just test
```

---

## Roadmap

- [x] Multi-format document support (PDF, DOCX, Images, Spreadsheets)
- [x] High-fidelity Markdown conversion
- [x] Header-based smart chunking
- [x] Structure detection (headings, tables, lists, code blocks)
- [x] Dual OCR support (Docling + EasyOCR)
- [x] Local embedding pipeline with batch processing
- [x] Persistent vector storage (ChromaDB)
- [x] Pluggable TextEmbedder / VectorStore interfaces
- [x] RAG retrieval chain
- [x] LLM integration (Groq / OpenAI SDK)
- [x] CLI interface for querying documents
- [ ] Web UI for chat-based interaction