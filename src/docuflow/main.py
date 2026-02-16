from docuflow.core.ingestion.ingestion_pipeline import ingest_data
from docuflow.utils.logger import get_logger


def start() -> None:
    get_logger()
    ingest_data()
    return None


if __name__ == "__main__":
    start()
