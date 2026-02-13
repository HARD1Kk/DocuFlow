# DocuFlow

DocuFlow is a modern Retrieval-Augmented Generation (RAG) system designed to process complex PDF documents with precision. By converting PDFs to structured Markdown before ingestion, DocuFlow preserves document layout, tables, and headers, ensuring higher-quality context for Large Language Models.

## 🚀 Features

- **Automatic Batch Processing**: Automatically detects and processes all PDF files in the `data/` directory.
- **High-Fidelity Ingestion**: Uses `pymupdf4llm` to convert PDFs to Markdown, preserving tables and multi-column layouts.
- **Smart Chunking**: Hierarchical splitting based on Markdown headers (`#`, `##`, `###`) with recursive character fallback.
- **Local Embeddings**: Generates high-quality dense vectors using `BAAI/bge-small-en-v1.5` (via `FlagEmbedding`).
- **Vector Storage**: Stores embeddings and metadata locally using **ChromaDB**.
- **Modern Stack**: Fully typed Python 3.11+ codebase managed with `uv`.

## 🛠️ Tech Stack

- **Core**: Python 3.11+
- **Ingestion**: PyMuPDF4LLM
- **Embeddings**: FlagEmbedding (BGE-Small)
- **Vector DB**: ChromaDB (Persistent)
- **Orchestration**: LangChain (Text Splitters)
- **Configuration**: Pydantic Settings

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/HARD1Kk/DocuFlow.git
   cd DocuFlow
   ```

2. **Install dependencies**
   ```bash
   # Using uv (recommended)
   uv sync
   ```
[![GitHub Streak](https://streak-stats.demolab.com/?user=hard1kk&theme=dark)](https://git.io/streak-stats)
3. **Configure Settings (Optional)**
   Create a `.env` file if you need to override defaults:
   ```env
   LOG_LEVEL=INFO
   EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
   ```

## 📂 Project Structure

```
.
├── data/                       # Source PDFs & Output Markdown / VectorDB
│   ├── chromadb/               # ChromaDB persistence folder
│   └── ...
├── src/
│   ├── core/
│   │   ├── ingestion/          # Ingestion Logic
│   │   │   ├── ingestion_pipeline.py  # Main pipeline
│   │   │   ├── chunking.py     # Text splitting logic
│   │   │   └── conversion.py   # PDF to MD conversion
│   │   └── rag/                # RAG Logic (Retrieval)
│   ├── schemas/                # Pydantic Data Models
│   │   ├── chunk.py            # Chunk schema
│   │   └── ...
│   ├── services/               # Core Services
│   │   ├── embedding_service.py # BGE Embedding generation
│   │   └── vector_store_service.py # ChromaDB interactions
│   ├── utils/                  # Utilities
│   │   └── settings.py         # App configuration
│   └── main.py                 # Application entry point
├── .env                        # Environment secrets
├── justfile                    # Task runner
└── pyproject.toml              # Dependencies
```

## 🧩 Usage

1. **Place your PDFs** in the `data/` folder.
2. **Run the Ingestion Pipeline**:
   ```bash
   just go
   ```
   This will:
   - Convert PDFs to Markdown.
   - Split them into semantic chunks.
   - Generate embeddings.
   - Store them in the local ChromaDB.

## 🚧 Roadmap / To-Do

- [x] **High-Fidelity Ingestion** (PDF -> Markdown)
- [x] **Smart Chunking** (Header-based)
- [x] **Embedding Pipeline** (BGE-Small)
- [ ] **Vector Store Integration** (ChromaDB)
- [ ] **Retrieval Logic**: Build the retrieval chain to fetch relevant context for queries.
- [ ] **LLM Integration**: Connect to a Generative Model (e.g., Gemini, GPT-4, Llama 3) to answer questions.
- [ ] **Chat Interface**: Simple CLI or Web UI for interaction.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
