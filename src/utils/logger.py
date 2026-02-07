import logging

from utils.settings import settings


def setup_logging() -> None:
    """Configures logging for the entire application."""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    log_path = settings.log_dir / settings.log_file

    # Ensure the directory exists
    log_path.parent.mkdir(parents=True, exist_ok=True)

    handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s - %(filename)s - %(levelname)s - %(message)s",
        datefmt="%d-%m-%Y %I:%M:%S %p",
    )
    handler.setFormatter(formatter)

    root_logger.addHandler(handler)
