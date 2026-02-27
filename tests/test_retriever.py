from docuflow.services import BGETextEmbedder,ChromaVectorStore,VectorRetriever


import pytest
from unittest.mock import Mock



def test_retrieve_returns_structured_chunks():
    # 1️⃣ Mock embedder
    mock_embedder = Mock()
    mock_embedder.embed.return_value = [[0.1, 0.2, 0.3]]

    # 2️⃣ Mock vector store
    mock_vector_store = Mock()
    mock_vector_store.query.return_value = {
        "documents": [["Refund policy text"]],
        "distances": [[0.21]],
        "metadatas": [[{"page": 3}]],
    }

    # 3️⃣ Create retriever
    retriever = VectorRetriever(mock_embedder, mock_vector_store)
    
    # 4️⃣ Call retrieve
    results = retriever.retrieve("What is refund policy?", top_k=1)
    print(results)
    # 5️⃣ Assertions
    assert len(results) == 1
    assert isinstance(results[0], RetrievedChunk)
    assert results[0].content == "Refund policy text"
    assert results[0].score == 0.21
    assert results[0].metadata == {"page": 3}