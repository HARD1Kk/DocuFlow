import numpy as np

from docuflow.services.embedding_service import EmbeddingServices


def cosine_similarity(query, docs):
    query = np.array(query)
    docs = np.array(docs)

    query = query / np.linalg.norm(query)
    docs = docs / np.linalg.norm(docs, axis=1, keepdims=True)

    return np.dot(docs, query)


def test_embedding_cosine_similarity():
    service = EmbeddingServices(batch_size=2)
    texts = [
        "Artificial Intelligence(AI) is transforming the world.",
        "Machine learning enables computers to learn from data.",
        "Embeddings convert text into numerical vectors.",
        "Python is a popular programming language.",
    ]
    embeddings = service.embed_texts(texts)

    query = "what is Ai?"
    query_emb = service.embed_query(query)

    scores = cosine_similarity(query_emb, embeddings)

    # Assert we get a score for every document
    assert len(scores) == len(texts)

    # Assert the scores are floats
    assert all(isinstance(s, float) for s in scores)

    print("Cosine similarity scores:", scores)
