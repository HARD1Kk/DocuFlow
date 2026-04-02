from docuflow.configs import settings
from docuflow.configs.sentry_config import init_sentry
from docuflow.core.ingestion.ingestion_pipeline import IngestionPipeline
from docuflow.services import BGETextEmbedder, ChromaVectorStore
from docuflow.utils import ensure_directories, get_logger


def main() -> None:
    logger = get_logger(__name__)

    init_sentry()

    logger.info("Starting Docuflow Pipeline")
    logger.info("Ensuring Directories existence")

    ensure_directories()

    logger.info("Starting Embedding Phase")
    embedder = BGETextEmbedder()

    logger.info("Starting Vectorising")
    vector_store = ChromaVectorStore(
        db_path=settings.db_path,
        collection_name="my_docuflow_collection",
    )

    pipeline = IngestionPipeline(
        embedder=embedder,
        vector_store=vector_store,
    )

    pdf_files = list(settings.pdf_dir.glob("*.pdf"))

    if not pdf_files:
        return

    for pdf in pdf_files:
        try:
            pipeline.ingest(pdf)
        except Exception as e:
            logger.error(f"Failed to ingest {pdf}: {e}", exc_info=True)
            continue


if __name__ == "__main__":
    main()
