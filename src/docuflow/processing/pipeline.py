# NEW: Main processing orchestrator

from pathlib import Path

from docuflow.data_source import LoaderFactory
from docuflow.processing.parsers import DocumentParser
from docuflow.utils import get_logger


class Pipeline:
    def __init__(self):
        self.logger = get_logger()

    def run(self, source_path: str):
        self.logger.info("Pipeline started")

        # Accept the input file path.
        document_path = Path(source_path)
        document_str = str(document_path)

        # Validate that the path was actually provided.

        if not document_path.exists():
            self.logger.error(f"File not found: {document_path}")
            return

        # Ask LoaderFactory for the correct loader based on extension.
        loader = LoaderFactory.get_loader(document_str)
        raw_document = loader.load(document_str)
        raw_document = raw_document[0]
        parser = DocumentParser()
        parsed_document = parser.parse(raw_document)
        print(parsed_document)
        self.logger.info("Pipeline finished")


if __name__ == "__main__":
    pipeline = Pipeline()
    pipeline.run("data/resume.jpg")
