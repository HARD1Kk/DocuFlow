# DocuFlow

DocuFlow is a modern Retrieval-Augmented Generation (RAG) system designed to process complex PDF documents with precision. By converting PDFs to structured Markdown before ingestion, DocuFlow preserves document layout, tables, and headers, ensuring higher-quality context for Large Language Models.

Powered by **Azure OpenAI** and **LangChain**.

## 🚀 Features

- **High-Fidelity Ingestion**: Uses `pymupdf4llm` to convert PDFs to Markdown, preserving tables and multi-column layouts.
- **Smart Splitting**: Implements structure-aware splitting based on Markdown headers (`#`, `##`, `###`) to keep semantic sections together.
- **Azure Integration**: Built-in configuration for Azure OpenAI (Chat & Embeddings).
- **Modern Stack**: Fully typed Python 3.11+ codebase managed with `uv` (or standard pip) and linted with `ruff`.

## 🛠️ Tech Stack

- **Core**: Python 3.11+
- **LLM & Embeddings**: Azure OpenAI
- **Orchestration**: LangChain
- **Document Processing**: PyMuPDF4LLM
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

   AZURE_CHATOPENAI_API_KEY=your_key_here
   AZURE_CHATOPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_CHATOPENAI_DEPLOYMENT=gpt-4o
   AZURE_CHATOPENAI_API_VERSION=2024-02-01
   ```

3. **Install dependencies**
   Refers to `pyproject.toml` for the list of dependencies.
   ```bash
   pip install .
   # OR if using uv
   uv pip install .
   ```

## 📂 Project Structure

```
.
├── src/
│   ├── config.py       # Pydantic settings management
│   ├── ingestion.py    # PDF to Markdown conversion & splitting
│   ├── rag.py          # Main RAG pipeline logic
│   └── main.py         # Entry point
├── .env                # Environment secrets (not committed)
├── pyproject.toml      # Project metadata & dependencies
└── README.md
```

## 🧩 Usage

*Work in Progress*

The core ingestion logic can be found in `src/ingestion.py`. It converts a PDF to markdown and then splits it by headers.

```python
from src.ingestion import convert_pdf_to_md, smart_split

# 1. Convert PDF to Markdown
markdown_content = convert_pdf_to_md("docs/whitepaper.pdf")

# 2. Split into chunks
chunks = smart_split() # Note: Requires valid markdown_text input
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
