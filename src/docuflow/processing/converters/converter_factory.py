from pathlib import Path
from typing import Type

from docuflow.processing.converters.base_converter import BaseConverter
from docuflow.processing.converters.document_converter import DocumentConverter
from docuflow.processing.converters.image_converter import ImageConverter


class ConverterFactory:
    """Route files to the correct converter based on extension."""

    _converters: dict[str, Type[BaseConverter]] = {}

    @classmethod
    def register(cls, converter_class: Type[BaseConverter]) -> None:
        for extension in converter_class.SUPPORTED_EXTENSIONS:
            cls._converters[extension] = converter_class

    @classmethod
    def get_converter(cls, source_path: str) -> BaseConverter:
        extension = Path(source_path).suffix.lower()
        converter_class = cls._converters.get(extension)
        if converter_class is None:
            raise ValueError(f"No converter for {extension}")
        return converter_class()


ConverterFactory.register(DocumentConverter)
ConverterFactory.register(ImageConverter)
