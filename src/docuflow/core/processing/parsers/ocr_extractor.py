import easyocr

from docuflow.schemas import RawDocument
from docuflow.utils import get_logger
from docuflow.core.ingestion import convert_image_content
from pathlib import Path
class ImageParser:
    def __init__(self):
        self.logger = get_logger(__name__)

    def _get_reader(self):
        """Lazy load OCR reader"""
        if self.reader is None:
            logger.info("Loading EasyOCR...")
            self.reader = easyocr.Reader(["en"])
        return self.reader

    def parse(self, raw_document: RawDocument) -> str:
        """Extract text from image"""
        try:
            self.logger.info(f"Parsing {raw_document.source} ({format})")

            if format == [".jpg", ".jpeg",".png", "webp"]:   
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

    image = ImageParser()

    loader = LoaderFactory.get_loader(image_path)
    raw_documents = loader.load(image_path)

    raw_doc = raw_documents[0]

    result = image.parse(raw_doc)
    print(result)
