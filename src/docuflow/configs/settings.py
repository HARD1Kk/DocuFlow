from pathlib import Path

from pydantic import BaseModel, Field, computed_field
from pydantic_settings import BaseSettings


class logs(BaseModel): ...


class Settings(BaseSettings):
    # Path of Pdf
    pdf_dir: Path = Field(
        default=Path("data/"), description="Directory containing PDF files"
    )
    output_dir: Path = Field(
        default=Path("data/"), description="Output directory for markdown files"
    )

    # Logging config
    log_dir: Path = Field(default=Path("logs"), description="Directory for log files")
    log_file: str = Field(default="app.log", description="Log file name")

    # chroma db path
    db_path: Path = Field(
        default=Path("chroma"), description="Directory for chroma db vector storage"
    )

    @computed_field
    @property
    def log_path(self) -> Path:
        return self.log_dir / self.log_file

    # Logging config
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields from .env

    # Embedding model
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    chunk_size: int = 800


# INSTANTIATION
settings = Settings()
