from docuflow.core.loaders.base_loader import BaseLoader


class DocumentLoader(BaseLoader):
    """Load documents: PDF, DOCX, TXT, MD"""

    SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".txt", ".md"]


if __name__ == "__main__":
    doc = DocumentLoader()

    path = "/home/hardik/projects/DocuFlow/data/sample2.docx"
    # path = "/home/hardik/projects/DocuFlow/data/doc.docx"
    # Load document
    raw_documents = doc.load(path)
    # print(raw_documents)

    # Check result
    if raw_documents:
        raw_doc = raw_documents[0]
        print(f"✅ Loaded: {raw_doc.source}")
        print(f"Content length: {len(raw_doc.content)}")
        print(f"Metadata: {raw_doc.metadata}")
    else:
        print(f"❌ Failed to load: {path}")
