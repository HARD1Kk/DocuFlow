import argparse
import sys

sys.path.insert(0, "/home/hardik/projects/DocuFlow/src")

from docuflow.configs import settings
from docuflow.processing.rag.rag import RAGChain
from docuflow.services.bge_text_embedder import BGETextEmbedder
from docuflow.services.chroma_vector_store import ChromaVectorStore
from docuflow.services.llm_service import LLMService
from docuflow.services.reranker import Reranker
from docuflow.services.retriever_chain import VectorRetriever


def main():
    parser = argparse.ArgumentParser(description="Test RAG Retrieval & Generation")
    parser.add_argument("--query", type=str, required=True, help="Query to run against the indexed documents")
    parser.add_argument("--top_k", type=int, default=3, help="Number of documents to retrieve")
    parser.add_argument("--mock-llm", action="store_true", help="Use mock LLM for generation instead of live Groq API")
    args = parser.parse_args()

    print("\n" + "=" * 80)
    print(f"RAG PIPELINE QUERY: '{args.query}'")
    print("=" * 80)

    # 1. Initialize Components
    print("Initializing services...")
    embedder = BGETextEmbedder()
    vector_store = ChromaVectorStore(db_path=settings.db_path, collection_name="documents")
    retriever = VectorRetriever(embedder=embedder, vector_store=vector_store)
    reranker = Reranker()
    llm = LLMService(mock=args.mock_llm)

    # 2. Retrieve
    print("\n[STEP 1] RETRIEVAL FROM CHROMADB")
    chunks = retriever.retrieve(args.query, top_k=args.top_k)
    if not chunks:
        print("❌ No matching chunks found in database.")
        return

    for idx, chunk in enumerate(chunks):
        print(f"\n  Chunk {idx + 1} (Semantic Score: {chunk.score:.4f}):")
        print(f"  Content: {chunk.content}")
        if chunk.metadata:
            print(f"  Summary: {chunk.metadata.get('summary')}")
            print(f"  Keywords: {chunk.metadata.get('keywords')}")
            print(f"  Questions: {chunk.metadata.get('hypothetical_questions')}")

    # 3. Rerank
    print("\n[STEP 2] RERANKING")
    reranked_chunks = reranker.rerank(args.query, chunks)
    for idx, chunk in enumerate(reranked_chunks):
        print(f"\n  Reranked Chunk {idx + 1} (Reranked Score: {chunk.score:.4f}):")
        print(f"  Content Preview: {chunk.content[:200]}...")

    # 4. Generate RAG Answer
    print("\n[STEP 3] LLM GENERATION")
    chain = RAGChain(retriever=retriever, reranker=reranker, llm_service=llm)

    print("Executing LLM generation...")
    answer = chain.query(args.query, top_k=args.top_k)

    print("\n" + "-" * 80)
    print("FINAL LLM RESPONSE:")
    print("-" * 80)
    print(answer)
    print("-" * 80 + "\n")


if __name__ == "__main__":
    main()
