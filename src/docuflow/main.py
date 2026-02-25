from docuflow.configs import settings
from docuflow.core.ingestion.ingestion_pipeline import IngestionPipeline
from docuflow.services import BGETextEmbedder, ChromaVectorStore

from docuflow.utils import get_logger, ensure_directories


def main() -> None:
    ensure_directories()
    get_logger()

    embedder = BGETextEmbedder()

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
        pipeline.ingest(pdf)


if __name__ == "__main__":
    main()
