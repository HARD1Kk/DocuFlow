import pytest

from docuflow.services.embedding_service import EmbeddingServices


# Define a fixture for embedding service setup
@pytest.fixture
def embedding_service():
    service = EmbeddingServices(batch_size=2)
    return service


def test_embed_texts(embedding_service):
    texts = [
        "Quantum computing uses quantum bits (qubits) to perform computations.",
        "The internet of things (IoT) connects everyday objects to the internet.",
    ]

    # Generate Embeddings
    embeddings = embedding_service.embed_texts(texts)

    # Assert correct number of embeddings
    assert len(embeddings) == len(texts), (
        "Embeddings count should match number of texts"
    )

    # Assert that each embedding is a list of floats
    assert all(isinstance(embedding, list) for embedding in embeddings), (
        "Each embedding should be a list"
    )
    assert all(
        isinstance(val, float) for embedding in embeddings for val in embedding
    ), "Each embedding value should be a float"


@pytest.mark.parametrize(
    "text,expected_length",
    [
        ("AI is transforming the world.", 384),
        ("Machine learning enables computers to learn from data.", 384),
    ],
)
def test_embedding_dimension(embedding_service, text, expected_length):
    embedding = embedding_service.embed_query(text)
    assert len(embedding) == expected_length, (
        f"Expected {expected_length} dimensions, but got {len(embedding)}"
    )


def test_empty_input(embedding_service):
    # Test empty input for embed_texts
    embeddings = embedding_service.embed_texts([])
    assert embeddings == [], "Expected empty list for empty input"

    # Test empty input for embed_query
    query_embedding = embedding_service.embed_query("")
    assert query_embedding == [], "Expected empty list for empty query"
