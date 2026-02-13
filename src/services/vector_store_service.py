import logging

import chromadb

from core.ingestion.conversion import convert_pdf_to_md
from services.embedding_service import embed_texts
from utils.load_fie import get_all_pdfs
from utils.settings import settings

logger = logging.getLogger(__name__)


def store_documents():
    """Load PDFs, generate embeddings, store in ChromaDB"""
    pdfs = get_all_pdfs(settings.pdf_dir)
    print(type(pdfs))

    documents = convert_pdf_to_md(str(pdfs))
    print(type(documents))
    all_embeddings = embed_texts(documents)
    print(type(all_embeddings))
    client = chromadb.PersistentClient(path="./chromadb/vector_db")
    print(type(client))
    collections = client.get_or_create_collection(name="my_docs")
    print(type(collections))
    ids = [f"doc_{i}" for i in range(len(documents))]
    print(type(ids))
    collections.add(embeddings=all_embeddings, documents=documents, ids=ids)

    logger.info(f"Stored {collections.count()} documents")

    return collections
