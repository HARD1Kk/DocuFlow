from docuflow.processing.converters import ConverterFactory
from docuflow.schemas import RawDocument
from docuflow.utils import TextCleaner, get_logger


class DocumentParser:
    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.cleaner = TextCleaner()

    def parse(self, raw_document: RawDocument) -> str:
        """Extract text from document formats using the converter layer."""
        file_format = raw_document.metadata.get("format", "").lower()

        try:
            self.logger.info(f"Parsing {raw_document.source} ({file_format})")
            result = ConverterFactory.get_converter(raw_document.source).convert(raw_document)

            if result is None:
                self.logger.error(f"Conversion returned None for {file_format}")
                raise RuntimeError("Conversion failed: None returned")

            cleaned_result = self._clean_text(result, raw_document.source)
            self.logger.info(f"Successfully parsed: {len(cleaned_result)} chars")
            return cleaned_result

        except Exception as e:
            self.logger.error(f"Error parsing {raw_document.source}: {e}")
            raise

    def _clean_text(self, text: str, source: str) -> str:
        try:
            cleaned_text = self.cleaner.clean(text)
            self.logger.info(f"Applied text cleaning to {source}")
            return cleaned_text
        except Exception as exc:
            self.logger.warning(f"Text cleaning failed for {source}: {exc}")
            return text


if __name__ == "__main__":
    from docuflow.core.loaders import LoaderFactory

    # Use your actual file
    document_path = "/home/hardik/projects/DocuFlow/data/sample2.docx"

    print(f"Loading: {document_path}")

    # Load
    loader = LoaderFactory.get_loader(document_path)
    raw_documents = loader.load(document_path)

    if not raw_documents:
        print("❌ Failed to load")
        exit(1)

    raw_doc = raw_documents[0]
    print(f"✅ Loaded: {raw_doc.metadata['filename']}")

    # Parse
    try:
        parser = DocumentParser()
        result = parser.parse(raw_doc)

        print("✅ Parsed successfully!")
        print(f"Content length: {len(result)} chars")
        print(f"\nPreview:\n{result[:500]}...")

        # Save to file for inspection
        output_file = "parsed_output.md"
        with open(output_file, "w") as f:
            f.write(result)
        print(f"\n✅ Saved to: {output_file}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
