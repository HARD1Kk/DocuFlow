import shutil
from pathlib import Path

from docuflow.services.chroma_vector_store import ChromaVectorStore


def test_chroma_vector_store_add_and_query():
    db_path = Path("chroma_test")

    if db_path.exists():
        shutil.rmtree(db_path)

    store = ChromaVectorStore(db_path=db_path, collection_name="test_collection")

    ids = ["1", "2"]
    documents = ["AI is amazing", "Cricket is popular"]
    metadata = [{"topic": "tech"}, {"topic": "sports"}]
    embeddings = [
        [0.1, 0.2, 0.3],
        [0.9, 0.8, 0.7],
    ]

    store.add(ids, documents, metadata, embeddings)

    results = store.query([0.1, 0.2, 0.3], n_results=1)

    assert results is not None
    assert len(results["ids"][0]) == 1
