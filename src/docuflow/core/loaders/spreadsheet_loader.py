from .base_loader import BaseLoader


class SpreadsheetLoader(BaseLoader):
    """Load spreadsheets: XLSX, CSV, TSV"""
    SUPPORTED_EXTENSIONS = [".xlsx", ".csv", ".tsv"]