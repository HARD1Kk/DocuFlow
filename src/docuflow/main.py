#!/usr/bin/env python3
from pathlib import Path

from docuflow.configs import settings
from docuflow.data_source import LoaderFactory
from docuflow.processing.chunking import ChunkingEngine
from docuflow.processing.ingestion import save_markdown
from docuflow.processing.parsers import DocumentParser
from docuflow.schemas.chunk import ChunkingConfig, DocumentType
from docuflow.utils import ensure_directories, get_logger
from docuflow.utils.dependency_checks import check_optional_dependencies, is_paddleocr_available


def get_document_type(file_path: Path) -> DocumentType:
    """Map file extension to DocumentType for chunking engine."""
    ext = file_path.suffix.lower()
    type_map = {
        ".pdf": DocumentType.PDF,
        ".docx": DocumentType.DOCX,
        ".txt": DocumentType.TXT,
        ".md": DocumentType.MD,
        ".png": DocumentType.IMAGE,
        ".jpg": DocumentType.IMAGE,
        ".jpeg": DocumentType.IMAGE,
        ".gif": DocumentType.IMAGE,
        ".webp": DocumentType.IMAGE,
        ".xlsx": DocumentType.SPREADSHEET,
        ".csv": DocumentType.SPREADSHEET,
    }
    return type_map.get(ext, DocumentType.UNKNOWN)


def main() -> None:
    logger = get_logger(__name__)
    logger.info("Starting Docuflow Pipeline")

    # Ensure directories exist
    ensure_directories()

    # Initialize processing components
    parser = DocumentParser()
    chunking_config = ChunkingConfig()
    chunking_engine = ChunkingEngine(config=chunking_config, enable_enrichment=False)
    # Run lightweight optional-dependency checks (logs availability) and set a flag
    deps = check_optional_dependencies()
    paddle_available = is_paddleocr_available()

    input_dir = settings.input_dir
    files = list(input_dir.glob("*"))
    if not files:
        logger.info("No files found to process.")
        return

    for file_path in files:
        try:
            # Skip directories and hidden files
            if not file_path.is_file() or file_path.name.startswith("."):
                logger.debug(f"Skipping non-file or hidden: {file_path}")
                continue

            # If paddle OCR backend isn't available, skip image files early with a clear log.
            if not paddle_available and file_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
                logger.warning(f"Skipping image {file_path.name} because PaddleOCR/PPStructureV3 is not available.")
                continue

            logger.info(f"Processing file: {file_path}")

            # Load document
            try:
                loader = LoaderFactory.get_loader(str(file_path))
            except ValueError:
                logger.warning(f"No loader for {file_path.suffix}; skipping")
                continue

            raw_documents = loader.load(str(file_path))
            if not raw_documents:
                logger.warning(f"No content loaded for {file_path}, skipping.")
                continue

            raw_doc = raw_documents[0]

            # Parse / convert & clean document to text
            parsed_text = parser.parse(raw_doc)

            # Save markdown output
            md_out = settings.md_dir / f"{file_path.stem}.md"
            save_markdown(parsed_text, md_out)
            logger.info(f"Saved markdown: {md_out}")

            # Chunk with advanced ChunkingEngine
            doc_type = get_document_type(file_path)
            chunk_batch = chunking_engine.chunk(
                content=parsed_text,
                document_type=doc_type,
                metadata={"source": str(file_path), "filename": file_path.name},
            )

            logger.info(
                f"Produced {len(chunk_batch.chunks)} chunks ({chunk_batch.total_tokens} tokens) for {file_path}"
            )

            if chunk_batch.processing_errors:
                logger.warning(f"Chunking errors: {chunk_batch.processing_errors}")

        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}", exc_info=True)
            continue

    logger.info("Processing complete")


if __name__ == "__main__":
    main()
