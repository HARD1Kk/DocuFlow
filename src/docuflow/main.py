import logging

from docuflow.core.ingestion.ingestion_pipeline import ingest_data
from docuflow.utils.logger import get_logger


def main() -> None:
    get_logger()
    logger = logging.getLogger(__name__)
    logger.info("Starting pipeline...")
    ingest_data()
    return None


if __name__ == "__main__":
    main()
