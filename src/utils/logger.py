import logging

from config import settings


def setup_logging() -> None:
    """Configures logging for the entire application."""
    root_logger = logging.getLogger()  # root logger
    root_logger.setLevel(logging.INFO)

    log_path = settings.log_dir / settings.log_file

    handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    root_logger.addHandler(handler)
