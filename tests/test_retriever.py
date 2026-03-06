from pathlib import Path

from docuflow.services import BGETextEmbedder, ChromaVectorStore, VectorRetriever


def test_retrieve_returns_structured_chunks():
    embedder = BGETextEmbedder(batch_size=64)
    vector_store = ChromaVectorStore(db_path=Path("chroma_test_r"), collection_name="test_collection_r")

    retrieve = VectorRetriever(embedder=embedder, vector_store=vector_store)

    query = "What is ai"
    result = retrieve.retrieve(query=query, top_k=5)
    print(result)
