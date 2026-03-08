from typing import List

from docuflow.interfaces import ILoader
from docuflow.schemas import Chunk


class CodeLoader(BaseLoader):
    """Load code files: Python, JavaScript, Java, etc."""
    SUPPORTED_EXTENSIONS = [
        ".py", ".js", ".ts", ".java", ".cpp", ".c", 
        ".go", ".rs", ".rb", ".php", ".swift", ".kt"
    ]