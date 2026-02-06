from pathlib import Path
from typing import List


def get_all_pdfs(pdf_dir: Path) -> List[Path]:
    """Returns a list of all PDF files in the directory."""
    if not pdf_dir.exists():
        raise FileNotFoundError(f"Directory not found: {pdf_dir}")

    pdfs = list(pdf_dir.glob("*.pdf"))
    return pdfs


def get_latest_pdf(pdf_dir: Path) -> Path:
    """Returns the most recently modified PDF file."""
    pdfs = get_all_pdfs(pdf_dir)

    if not pdfs:
        raise FileNotFoundError("No PDF found in directory")

    return max(pdfs, key=lambda p: p.stat().st_mtime)
