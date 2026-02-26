from docuflow.configs import settings
from docuflow.utils import get_logger
from pathlib import Path

logger = get_logger(__name__)


def ensure_directories() -> None:
    directories = [
        settings.db_path,
        settings.log_dir,
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def log_path(log_file: Path) -> None:
    try:
        # ensure directory present
        if not log_file.parent.exists():
            log_file.parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"Creating log directory: : {log_file.parent}")
        else:
            logger.debug(f"Log directory already exists: {log_file.parent}")
    except Exception as e:
        logger.error(f"Failed to ensure log directory: {e}", exc_info=True)
