from .base_loader import BaseLoader


class ImageLoader(BaseLoader):
    """Load images: PNG, JPG, GIF, WEBP"""

    SUPPORTED_EXTENSIONS = [".png", ".jpg", ".jpeg", ".gif", ".webp"]


if __name__ == "__main__":
    doc = ImageLoader()

    path = "/home/hardik/projects/DocuFlow/data/image.png"
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
