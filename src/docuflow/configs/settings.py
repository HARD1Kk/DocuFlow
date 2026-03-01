from pathlib import Path

from pydantic import Field
from pydantic_settings import SettingsConfigDict, BaseSettings


class Settings(BaseSettings):
    # Path of Pdf
    pdf_dir: Path = Field(
        default=Path("data/pdfs"), description="Directory containing PDF files"
    )

    # md dir
    md_dir: Path = Field(
        default=Path("data/markdown"), description="Output directory for markdown files"
    )

    # md_path
    md_path: str = Field(default="markdown.md", description="MD file name")

    # Logging config
    log_dir: Path = Field(default=Path("logs"), description="Directory for log files")
    log_file: str = Field(default="app.log", description="Log file name")

    # chroma db path
    db_path: Path = Field(
        default=Path("chroma"), description="Directory for chroma db vector storage"
    )

    @property
    def log_path(self) -> Path:
        return self.log_dir / self.log_file

    @property
    def output_path(self) -> Path:
        return self.md_dir / self.md_path

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Embedding model
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    chunk_size: int = 800
    use_fp16: bool = False


# INSTANTIATION
settings = Settings()
