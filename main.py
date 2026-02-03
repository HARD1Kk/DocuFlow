import logging

from src.core.ingestion import ingest_data


def start() -> None:
    # This "unmutes" the logging system
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    ingest_data()
    return None


if __name__ == "__main__":
    start()
