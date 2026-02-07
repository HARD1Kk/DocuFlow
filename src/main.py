from core.ingestion import ingest_data
from utils.logger import setup_logging


def start() -> None:
    setup_logging()
    ingest_data()

    return None


if __name__ == "__main__":
    start()
