import logging
from logging.handlers import RotatingFileHandler


def get_logger():
    logger = logging.getLogger(__name__)

    # Prevent duplicate logs
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(name)s |  %(levelname)s | %(filename)s | %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        "rag-logger.log", maxBytes=5_000_000, backupCount=3
    )

    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    logger.addHandler(file_handler)
    logger.propagate = False
    return logger
