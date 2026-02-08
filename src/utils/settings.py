from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


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

    # Logging config
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields from .env


# INSTANTIATION
settings = Settings()
