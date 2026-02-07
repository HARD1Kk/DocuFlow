# DocuFlow

DocuFlow is a modern Retrieval-Augmented Generation (RAG) system designed to process complex PDF documents with precision. By converting PDFs to structured Markdown before ingestion, DocuFlow preserves document layout, tables, and headers, ensuring higher-quality context for Large Language Models.

Powered by **Azure OpenAI** and **LangChain**.

## 🚀 Features

- **Automatic Batch Processing**: Automatically detects and processes all PDF files in the `data/` directory.
- **High-Fidelity Ingestion**: Uses `pymupdf4llm` to convert PDFs to Markdown, preserving tables and multi-column layouts.
- **OCR Support**: Handles scanned PDFs by performing optional OCR extraction (via pymupdf4llm).
- **Smart Splitting**: Implements structure-aware splitting based on Markdown headers (`#`, `##`, `###`) to keep semantic sections together.
- **Azure Integration**: Built-in configuration for Azure OpenAI (Chat & Embeddings).
- **Modern Stack**: Fully typed Python 3.11+ codebase managed with `uv` and linted with `ruff`.

## 🛠️ Tech Stack

- **Core**: Python 3.11+
- **LLM & Embeddings**: Azure OpenAI
- **Orchestration**: LangChain
- **Document Processing**: PyMuPDF4LLM (with OCR capabilities)
- **Configuration**: Pydantic Settings

## 📋 Prerequisites

Ensure you have access to an Azure OpenAI resource with deployments for:
- An embedding model (e.g., `text-embedding-3-small`)
- A chat model (e.g., `gpt-4o`)

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/HARD1Kk/DocuFlow.git
   cd DocuFlow
   ```

2. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```bash
   touch .env
   ```
   Add your Azure credentials:
   ```env
   AZURE_OPENAI_API_KEY=your_key_here
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
   AZURE_OPENAI_API_VERSION=2024-02-01

   # Logging
   LOG_LEVEL=INFO
   ```

3. **Install dependencies**
   Refers to `pyproject.toml` for the list of dependencies.
   ```bash
   # Using uv (recommended)
   uv sync
   ```

## 📂 Project Structure

```
.
├── data/               # Source PDFs for ingestion & Output Markdown
├── src/
│   ├── core/           # Business Logic
│   │   ├── ingestion.py# PDF Conversion & Batch Processing
│   │   └── rag.py      # RAG Retrieval & Generation
│   ├── utils/          # Utilities & Config
│   │   ├── settings.py # Settings management (Pydantic)
│   │   ├── logger.py   # Centralized logging
│   │   ├── conversion.py # PDF to MD conversion logic
│   │   └── load_fie.py # File loading utilities
│   └── main.py         # Application entry point
├── .env                # Environment secrets
├── justfile            # Task runner
└── pyproject.toml      # Dependencies
```

## 🧩 Usage

Simply place your PDF files in the `data/` folder. The system will process **all** found PDFs.

```bash
# Using just (recommended)
just go

# Or directly with uv
uv run src/main.py
```

### Manual Ingestion Flow
You can also import specific logic for your own scripts:

```python
from src.core.ingestion import ingest_data

# Process all PDFs in the data directory
ingest_data()
```

## 🚧 Roadmap / To-Do

- [ ] **Vector Store Integration**: Set up ChromaDB or Azure AI Search for storing embeddings.
- [ ] **Embedding Pipeline**: Implement logic to generate embeddings for document chunks using Azure OpenAI.
- [ ] **Retrieval Logic**: Build the retrieval chain to fetch relevant context for queries.
- [ ] **Chat Interface**: Create a simple frontend (Streamlit or FastAPI) for user interaction.
- [ ] **Evaluation**: Add evaluation metrics (using Ragas) to test retrieval quality.
- [ ] **Dockerization**: Containerize the application for easy deployment.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
