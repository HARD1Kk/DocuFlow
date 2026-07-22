# DocuFlow Developer Guide

Welcome to DocuFlow! This guide provides everything a new developer needs to get onboarded, set up their local environment, execute tests, run pipelines, and extend the system.

---

## 1. Local Development Setup

### Prerequisites
1.  **Python 3.11** (recommended version, as managed by the `.python-version` file).
2.  **[uv](https://github.com/astral-sh/uv)**: A fast Python package installer and resolver.
3.  **[just](https://github.com/casey/just)**: A handy command runner to execute project tasks.
4.  **Pandoc**: Required on the system if you intend to convert Microsoft Word `.docx` documents.

### Step-by-Step Installation
Run the following commands from your terminal to sync the project environment:

```bash
# 1. Clone the repository
git clone https://github.com/HARD1Kk/DocuFlow.git
cd DocuFlow

# 2. Synchronize dependencies using uv
# This automatically creates a virtual environment (.venv) and installs all locks
uv sync

# 3. Perform editable project installation
just install
```

### Environment Configuration (`.env`)
Create a `.env` file in the project root to control development parameters:

```ini
# Logger setup (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Local HuggingFace embedding model (downloaded automatically)
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5

# Persistent database storage folder
DB_PATH=chroma

# LLM connection parameters (Groq Cloud is standard)
GROQ_API_KEY="your_groq_api_key"
LLM_MODEL="llama-3.3-70b-versatile"
LLM_BASE_URL="https://api.groq.com/openai/v1"
```

---

## 2. Standard Developer Commands

DocuFlow uses a `justfile` to simplify routine operations. Here are the core commands:

| Command | Command Executed | Purpose |
|---------|------------------|---------|
| `just fmt` | `uv run ruff format . && uv run ruff check --fix` | Formats code and auto-fixes import sorting |
| `just check` | `uv run mypy . && uv run ty check` | Runs MyPy strict type analysis |
| `just test` | `uv run pytest -s` | Runs the test suite (unit and integration tests) |
| `just go` | `uv run python -m docuflow.main` | Processes documents in `data/input` |
| `just dead` | `uv run vulture . --exclude .venv` | Analyzes codebase for unused variables and functions |
| `just clean` | `rm -f *.md` | Deletes loose markdown files in the project root |

---

## 3. Ingestion & Retrieval Testing

### Testing Ingestion
1.  Place test files (e.g. `.pdf`, `.docx`, `.xlsx`, `.csv`, `.png`, `.jpg`, `.txt`, `.md`) in the `data/input` folder.
2.  Run the ingestion pipeline:
    ```bash
    just go
    ```
3.  Check the outputs:
    *   Markdown files are saved to `data/markdown/{filename}.md`.
    *   Chunk metadata is saved to `data/markdown/{filename}_chunks.json`.
    *   ChromaDB vector state is loaded inside `chroma/`.

### Testing Retrieval & Live RAG Generation
Query the system using the retrieval script:

```bash
# Run a semantic retrieval query with live LLM response generation
uv run python scripts/test_retrieval.py --query "What is the B.Tech qualification and CGPA of the developer?"

# Run retrieval only, using mock LLM generation (ideal for offline tests)
uv run python scripts/test_retrieval.py --query "What is the main topic?" --mock-llm
```

---

## 4. Architecture Extension Patterns

DocuFlow is designed to be easily extensible. Here is how to add new components:

### 4.1. How to Add a New File Converter
If you need to parse a new file format (e.g., `.pptx` or `.html`):
1.  Define a new class in a converter file or within [processing/converters/](file:///home/hardik/projects/DocuFlow/src/docuflow/processing/converters) inheriting from [BaseConverter](file:///home/hardik/projects/DocuFlow/src/docuflow/interfaces/converter.py):
    ```python
    from docuflow.interfaces import BaseConverter
    from docuflow.schemas import RawDocument

    class PptxConverter(BaseConverter):
        SUPPORTED_EXTENSIONS = (".pptx",)

        def convert(self, raw_document: RawDocument) -> str:
            # Add parsing logic here
            return "# PPTX Slides Content..."
    ```
2.  Register your converter inside [converter_factory.py](file:///home/hardik/projects/DocuFlow/src/docuflow/processing/converters/converter_factory.py):
    ```python
    from docuflow.processing.converters.pptx_converter import PptxConverter
    ConverterFactory.register(PptxConverter)
    ```

### 4.2. How to Add a Custom Chunker
To add a custom splitter (e.g., custom AST chunking for SQL scripts):
1.  Define your class in [processing/chunking/](file:///home/hardik/projects/DocuFlow/src/docuflow/processing/chunking) inheriting from [BaseChunker](file:///home/hardik/projects/DocuFlow/src/docuflow/processing/chunking/base_chunker.py):
    ```python
    from docuflow.processing.chunking.base_chunker import BaseChunker
    from docuflow.schemas.chunk import ChunkBatch, DocumentType

    class SqlChunker(BaseChunker):
        @property
        def supported_document_types(self) -> list[DocumentType]:
            return [DocumentType.CODE] # Add new document types if necessary

        def chunk(self, content: str, metadata: dict[str, any]) -> ChunkBatch:
            # Custom split logic
            ...
    ```
2.  Register your chunker inside [chunking_engine.py](file:///home/hardik/projects/DocuFlow/src/docuflow/processing/chunking/chunking_engine.py):
    *   Either append to `_register_builtin_chunkers()` or call `register_chunker()` on the instantiated engine.

---

## 5. Structured Tracing & Debugging

DocuFlow features structured tracing to track files and requests through the pipeline:
*   **ContextVars**: Correlation parameters are set implicitly using `log_context` from [logger.py](file:///home/hardik/projects/DocuFlow/src/docuflow/utils/logger.py).
*   **Usage Example**:
    ```python
    from docuflow.utils import log_context, get_logger

    logger = get_logger(__name__)

    with log_context(request_id="my-unique-request-id", stage="Validation"):
        logger.info("Executing validation checks")
        # All nested function logs will automatically output the request_id and stage!
    ```
*   **Log Verification**:
    You can inspect how structured logs behave by executing:
    ```bash
    uv run python scripts/demo_trace.py
    ```
    This script generates a temporary log, simulates standard ingestion/retrieval steps, and outputs the exact filtered JSON and human-readable trace timeline.
