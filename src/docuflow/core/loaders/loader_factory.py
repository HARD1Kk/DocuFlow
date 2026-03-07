from pathlib import Path
from typing import Dict, Type

from .code_loader import CodeLoader
from .document_loader import DocumentLoader
from .image_loader import ImageLoader


class LoaderFactory:
    """Routes files to correct loader based on extension"""

    _loaders: Dict[str, Type[ILoader]] = {}

    @classmethod
    def register(cls, loader_class: Type[ILoader]) -> None:
        """Register loader for its supported extensions"""
        for ext in loader_class.SUPPORTED_EXTENSIONS:
            cls._loaders[ext] = loader_class

    @classmethod
    def get_loader(cls, source_path: str) -> ILoader:
        """Get appropriate loader for file type"""
        ext = Path(source_path).suffix.lower()
        loader_class = cls._loaders.get(ext)

        if not loader_class:
            raise ValueError(f"No loader for {ext}")

        return loader_class()


# Register all loaders
LoaderFactory.register(DocumentLoader)
LoaderFactory.register(ImageLoader)
LoaderFactory.register(CodeLoader)
