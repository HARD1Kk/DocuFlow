from docuflow.services import BGETextEmbedder


def test_embed_text() -> None:
    embedding_text = BGETextEmbedder(batch_size=64)

    texts = ["ai", "ml"]

    embed = embedding_text.embed(texts)

    assert len(embed) == 2
    assert isinstance(embed[0], list)
    assert all(isinstance(x, float) for x in embed[0])
    assert len(embed[0]) == 384
