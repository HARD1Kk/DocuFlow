from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Generic input directory for documents (PDFs, DOCX, images, etc.)
    # New: prefer `input_dir` for general processing; `pdf_dir` is kept for backward compatibility.
    input_dir: Path = Field(
        default=Path("data/input"), description="Generic input directory containing documents to process"
    )

    # Path of Pdf (legacy - kept for backward compatibility)
    pdf_dir: Path = Field(default=Path("data/pdfs"), description="Directory containing PDF files")

    # md dir
    md_dir: Path = Field(default=Path("data/markdown"), description="Output directory for markdown files")

    # md_path
    md_path: str = Field(default="markdown.md", description="MD file name")

    # Logging config
    log_dir: Path = Field(default=Path("logs"), description="Directory for log files")
    log_file: str = Field(default="app.log", description="Log file name")

    # chroma db path
    db_path: Path = Field(default=Path("chroma"), description="Directory for chroma db vector storage")

    # ✅ Add Sentry
    SENTRY_DSN: Optional[str] = None
    SENTRY_TRACES_SAMPLE_RATE: float = 1.0

    ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    @property
    def log_path(self) -> Path:
        return self.log_dir / self.log_file

    @property
    def output_path(self) -> Path:
        return self.md_dir / self.md_path

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=True)

    # Embedding model
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    chunk_size: int = 800
    use_fp16: bool = False

    # LLM Settings
    LLM_PROVIDER: str = "groq"
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    LLM_BASE_URL: str = "https://api.groq.com/openai/v1"
    GROQ_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None


# INSTANTIATION
settings = Settings()
