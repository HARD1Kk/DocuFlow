import logging

import chromadb

from docuflow.core.ingestion.conversion import convert_pdf_to_md
from docuflow.services.embedding_service import embed_texts
from docuflow.utils.load_fie import get_all_pdfs
from docuflow.utils.settings import settings
import numpy as np
logger = logging.getLogger(__name__)


def store_documents():
    """Load PDFs, generate embeddings, store in ChromaDB"""
    pdfs = get_all_pdfs(settings.pdf_dir)
    print(type(pdfs))

    
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