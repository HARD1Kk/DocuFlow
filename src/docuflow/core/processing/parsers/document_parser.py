from pathlib import Path

from docuflow.core.ingestion import convert_docx_to_md, convert_pdf_to_md, extract_text_content
from docuflow.schemas import RawDocument
from docuflow.utils import get_logger


class DocumentParser:
    def __init__(self):
        self.logger = get_logger(__name__)

    def parse(self, raw_document: RawDocument) -> str:
        """Extract text from document"""
        format = raw_document.metadata["format"]

        try:
            self.logger.info(f"Parsing {raw_document.source} ({format})")

            if format == ".pdf":
                result = convert_pdf_to_md(Path(raw_document.source))
            elif format == ".docx":
                result = convert_docx_to_md(Path(raw_document.source))
            elif format in [".txt", ".md"]:
                result = extract_text_content(Path(raw_document.source))
            else:
                raise ValueError(f"Unsupported format: {format}")

            # ✅ Check result is not None
            if result is None:
                self.logger.error(f"Conversion returned None for {format}")
                raise RuntimeError("Conversion failed: None returned")

            self.logger.info(f"Successfully parsed: {len(result)} chars")
            return result

        except Exception as e:
            self.logger.error(f"Error parsing {raw_document.source}: {e}")
            raise


# src/docuflow/core/processing/parsers/document_parser.py

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
