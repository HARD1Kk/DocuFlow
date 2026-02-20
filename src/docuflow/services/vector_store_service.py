import logging

import chromadb

from docuflow.configs.settings import settings
from docuflow.utils.document_helper import get_meta_content_id

logger = logging.getLogger(__name__)

class VectorStoreService():
    def __init__(self,db_path:str,collection_name:str):
        self.client = chroma.PersistentClient(path=db_path)
        self.collection = self.client.create_collection(name="my_docuflow_collection")

    def add_document(self,ids, documents,embeddings,metadatas=None):
        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )        
    def query(self,query_embeddings,n_results=5):
        return self.collection.query(
            query_embeddings = [query_embeddings],
            n_results= n_results
        )

    def delete(self, ids):
        self.collection.delete(ids=ids)    

# def store_documents(documents):
#     """Load PDFs, generate embeddings, store in ChromaDB"""

#     client = chromadb.PersistentClient(path=settings.db_path)
#     print(f"client : {client}")
#     # print(client.heartbeat())

#     data = get_meta_content_id(documents)

#     print(type(data))
#     texts = data["documents"]
#     embeddings = embed_texts(texts)

#     print(embeddings)
#     collection = client.create_collection(name="my_docuflow_collection")

#     collection.upsert(
#         ids=data["ids"],
#         documents=data["documents"],
#         embeddings=embeddings,
#         metadatas=data["metadatas"],
#     )

#     query = "what are my skills"
#     embedding = embed_query(query)
#     results = collection.query(query_embeddings=[query], n_results=3)
#     print(results)

#     # print(client.get_collection(name="my_docuflow_collection"))

#     return "Documents stored successfully"


# if __name__ == "__main__":
#     pdf = "data/sample_test_document.pdf"
#     print(pdf)
#     documents = convert_pdf_to_md(pdf)
#     print(documents)
#     store_documents(documents)
