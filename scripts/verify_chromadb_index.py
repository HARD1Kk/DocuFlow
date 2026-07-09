import sys

sys.path.insert(0, "/home/hardik/projects/DocuFlow/src")

from docuflow.configs import settings
from docuflow.services.chroma_vector_store import ChromaVectorStore

# Load vector store
vector_store = ChromaVectorStore(db_path=settings.db_path, collection_name="documents")

print("\n================ CHROMADB INDEX STATUS ================")
print(f"Total count of indexed documents: {vector_store.collection.count()}")

# Fetch all chunks
results = vector_store.collection.get()
ids = results.get("ids", [])
documents = results.get("documents", [])
metadatas = results.get("metadatas", [])

for idx, (cid, doc, meta) in enumerate(zip(ids, documents, metadatas)):
    print(f"\n--- Document {idx + 1} (ID: {cid}) ---")
    print(f"Document content preview: {doc[:150]}...")
    print(f"Keywords: {meta.get('keywords')}")
    print(f"Summary: {meta.get('summary')}")
    print(f"Hypothetical Questions: {meta.get('hypothetical_questions')}")
    print("---------------------------------------------")
