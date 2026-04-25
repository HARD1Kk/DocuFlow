from pathlib import Path

__all__ = ["save_markdown"]


def save_markdown(md_text: str, output_path: Path) -> Path:
    """
    Save markdown text to a file.

    Args:
        md_text: Markdown content to save
        output_path: Path where MD file will be written

    Returns:
        Path to the saved file
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(md_text, encoding="utf-8")
    return output_file
