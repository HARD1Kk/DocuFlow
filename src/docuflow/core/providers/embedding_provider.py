from FlagEmbedding import FlagModel

from docuflow.configs.settings import settings


def get_embedding_model():
    return FlagModel(
        settings.embedding_model,
        query_instruction_for_retrieval="Represent this sentence for searching relevant passages:",
        use_fp16=settings.use_fp16,
    )
