import chromadb
from ingestion.conversion import convert_pdf_to_md

from utils.load_fie import get_all_pdfs
from utils.settings import settings

from .embedding_services import embed_texts


def store_documents():
    """Load PDFs, generate embeddings, store in ChromaDB"""
    pdfs = get_all_pdfs(settings.pdf_dir)
    documents = convert_pdf_to_md(pdfs)
    all_embeddings = embed_texts(documents)
    client = chromadb.PersistentClient(path="./chromadb/vector_db")

    collections = client.get_or_create_collection(name="my_docs")

    ids = [f"doc_{i}" for i in range(len(documents))]

    collections.add(embeddings=all_embeddings, documents=documents, ids=ids)

    logging.info(f"Stored {collections.count()} documents")

    return collections