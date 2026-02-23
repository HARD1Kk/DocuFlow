from docuflow.configs import Settings
from docuflow.core.ingestion.ingestion_pipeline import IngestionPipeline
from docuflow.services.bge_text_embedder import BGETextEmbedder
from docuflow.services.chroma_vector_store import ChromaVectorStore
from docuflow.utils.logger import get_logger


def main():
    get_logger()
    Settings.pdf_dir.mkdir(parents=True, exist_ok=True)
    Settings.db_path.mkdir(parents=True, exist_ok=True)

    embedder = BGETextEmbedder()

    vector_store = ChromaVectorStore(
        db_path=Settings.db_path,
        collection_name="my_docuflow_collection",
    )

    pipeline = IngestionPipeline(
        embedder=embedder,
        vector_store=vector_store,
    )

    pdf_files = list(Settings.pdf_dir.glob("*.pdf"))

    if not pdf_files:
        return

    for pdf in pdf_files:
        pipeline.ingest(pdf)


if __name__ == "__main__":
    main()
