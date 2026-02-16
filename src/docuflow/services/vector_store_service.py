import logging

import chromadb

from docuflow.configs.settings import settings
from docuflow.utils.load_fie import get_all_pdfs

logger = logging.getLogger(__name__)


def store_documents():
    """Load PDFs, generate embeddings, store in ChromaDB"""
    pdfs = get_all_pdfs(settings.pdf_dir)
    print(type(pdfs))
    print(pdfs)

    client = chromadb.PersistentClient(path=settings.db_path)
    print(client)
    print(type(client))

    # documents  = []

    # documents.convert_pdf_to_md(pdfs)

    # all_embeddings = embed_texts(documents)
    # print(type(all_embeddings))
    # client = chromadb.PersistentClient(path="./chromadb/vector_db")

    # collections = client.get_or_create_collection(name="my_docs")

    # ids = [f"doc_{i}" for i in range(len(documents))]

    # collections.add(embeddings=np.array(all_embeddings), documents=documents, ids=ids)

    # logger.info(f"Stored {collections.count()} documents")

    # return collections


if __name__ == "__main__":
    store_documents()
