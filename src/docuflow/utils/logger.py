import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
import pytz
from docuflow.configs import settings


def ist_timezone(*args):
    """Return IST time for logging formatter."""
    tz = pytz.timezone("Asia/Kolkata")
    return datetime.now(tz).timetuple()


def get_logger(name: str = __name__):
    logger = logging.getLogger(name)

    # Prevent duplicate logs
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)-40s | %(message)s",
        datefmt="%Y-%m-%d %I:%M:%S %p",
    )
    # Use IST for timestamps
    formatter.converter = ist_timezone

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    # File handler (auto-creates file if missing)
    file_handler = RotatingFileHandler(
        settings.log_path, maxBytes=5_000_000, backupCount=3
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.propagate = False
    return logger
