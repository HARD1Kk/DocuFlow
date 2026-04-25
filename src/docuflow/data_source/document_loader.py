from docuflow.data_source.base_loader import BaseLoader


class DocumentLoader(BaseLoader):
    """Load documents: PDF, DOCX, TXT, MD"""

    SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".txt", ".md"]


if __name__ == "__main__":
    from docuflow.data_source.loader_factory import LoaderFactory

    # Let the factory pick the right loader
    path = "/home/hardik/projects/DocuFlow/data/sample2.docx"

    # Factory automatically detects it's a .docx and uses DocumentLoader
    loader = LoaderFactory.get_loader(path)
    raw_documents = loader.load(path)

    if raw_documents:
        raw_doc = raw_documents[0]
        print(f"✅ Loaded: {raw_doc.source}")
        print(f"Content length: {len(raw_doc.content)}")
        print(f"Metadata: {raw_doc.metadata}")
    else:
        print(f"❌ Failed to load: {path}")
