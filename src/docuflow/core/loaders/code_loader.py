from .base_loader import BaseLoader


class CodeLoader(BaseLoader):
    """Load code files: Python, JavaScript, Java, etc."""

    SUPPORTED_EXTENSIONS = [".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rs", ".rb", ".php", ".swift", ".kt"]
