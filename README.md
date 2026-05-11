# DocuFlow

Production-ready document processing pipeline for RAG systems with structure-aware chunking.

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

# Configure settings (optional)
# Create .env file in project root:
LOG_LEVEL=INFO
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
CHUNK_SIZE=800
DB_PATH=chroma
```

---

## Quick Start

```bash
# Process a single document
uv run python -m docuflow.main path/to/document.pdf

# Process with custom chunk size
uv run python -m docuflow.main path/to/document.pdf --chunk-size 512 --overlap 50
```

---

## Supported Formats

| Category | Formats |
|----------|---------|
| Documents | PDF, DOCX, TXT, MD |
| Images | PNG, JPG, JPEG (via OCR) |
| Spreadsheets | XLS, XLSX, CSV, TSV |

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
│   └── parsers/          # Text extraction
│       ├── document_parser.py
│       ├── image_parser.py
│       └── structure_analyzer.py
│
├── interfaces/           # Abstract interfaces
├── schemas/              # Pydantic models
└── utils/               # Helpers
```

---

## Usage

### Python API

```python
from docuflow.processing.chunking import ChunkingEngine
from docuflow.schemas.chunk import ChunkingConfig

config = ChunkingConfig(
    max_chunk_size=512,
    min_chunk_size=100
)

engine = ChunkingEngine(config)
result = engine.chunk("path/to/document.pdf")

for chunk in result.chunks:
    print(f"Content: {chunk.content[:100]}...")
    print(f"Tokens: {chunk.token_count}")
```

### CLI

```bash
# Process and save to output directory
uv run python -m docuflow.main input.pdf --output ./output

# Process multiple files
uv run python -m docuflow.main ./documents/ --glob "*.pdf"
```

### Using justfile

```bash
# Run the pipeline
just go

# Run tests
just test

# Format & lint
just fmt
```

---

## Testing

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=src/docuflow --cov-report=html
```

---

## Configuration Reference

| Setting | Default | Description |
|---------|----------|-------------|
| `LOG_LEVEL` | INFO | Logging level |
| `EMBEDDING_MODEL` | BAAI/bge-small-en-v1.5 | HuggingFace embedding model |
| `CHUNK_SIZE` | 800 | Maximum characters per chunk |
| `DB_PATH` | chroma | ChromaDB persistence directory |

---

## Project Structure

```
DocuFlow/
├── src/docuflow/          # Main package
│   ├── configs/           # Settings
│   ├── data_source/      # Loaders
│   ├── processing/       # Core pipeline
│   ├── interfaces/       # Abstract interfaces
│   ├── schemas/          # Pydantic models
│   ├── services/         # Implementations
│   └── utils/            # Helpers
├── tests/                 # Test suite
├── data/                  # Sample data
├── notes/                 # Architecture notes
├── pyproject.toml         # Dependencies
├── justfile               # Build tasks
└── README.md
```

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Run tests: `just test`
4. Format code: `just fmt`
5. Submit a pull request

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
- [ ] RAG retrieval chain
- [ ] LLM integration (Gemini / GPT-4 / Llama 3)
- [ ] CLI interface for querying documents
- [ ] Web UI for chat-based interaction