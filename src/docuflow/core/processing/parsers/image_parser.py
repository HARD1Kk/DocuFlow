from pathlib import Path

from docuflow.core.ingestion import convert_image_content
from docuflow.schemas import RawDocument
from docuflow.utils import get_logger


class ImageParser:
    def __init__(self) -> None:
        self.logger = get_logger(__name__)

    def parse(self, raw_document: RawDocument) -> str:
        """Extract text from image"""
        try:
            format = raw_document.metadata.get("format", "").lower()

            self.logger.info(f"Parsing {raw_document.source} ({format})")

            if format in [".jpg", ".jpeg", ".png", ".webp"]:
                result = convert_image_content(Path(raw_document.source))
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


if __name__ == "__main__":
    from docuflow.core.loaders import LoaderFactory

    image_path = "/home/hardik/projects/DocuFlow/data/image.png"

    print(f"Loading: {image_path}")

    # Check file exists
    if not Path(image_path).exists():
        print(f"❌ Image not found: {image_path}")
    else:
        # Load
        loader = LoaderFactory.get_loader(image_path)
        raw_documents = loader.load(image_path)

        if not raw_documents:
            print("❌ Failed to load image")
        else:
            raw_doc = raw_documents[0]
            print(f"✅ Loaded: {raw_doc.metadata['filename']}")

            # Parse
            parser = ImageParser()

            result = parser.parse(raw_doc)

            print(f"✅ Extracted {len(result)} chars")
            print(f"\nPreview:\n{result[:300]}...")
