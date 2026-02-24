from docuflow.configs import settings


def ensure_directories() -> None:
    directories = [
        settings.pdf_dir,
        settings.db_path,
        settings.log_dir,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
