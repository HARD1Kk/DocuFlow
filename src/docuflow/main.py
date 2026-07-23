#!/usr/bin/env python3
from pathlib import Path
from typing import Any

from docuflow.configs import settings
from docuflow.data_source import LoaderFactory
from docuflow.processing.chunking import ChunkingEngine
from docuflow.processing.converters import ConverterFactory
from docuflow.processing.ingestion import save_markdown
from docuflow.processing.parsers import DocumentParser
from docuflow.schemas.chunk import ChunkingConfig, DocumentType
from docuflow.schemas.document_context import DocumentContext
from docuflow.services.bge_text_embedder import BGETextEmbedder
from docuflow.services.chroma_vector_store import ChromaVectorStore
from docuflow.services.llm_service import LLMService
from docuflow.utils import ensure_directories, get_logger, log_context
from docuflow.utils.dependency_checks import check_optional_dependencies, is_paddleocr_available


def get_document_type(file_path: Path) -> DocumentType:
    """Map file extension to DocumentType for chunking engine."""
    ext = file_path.suffix.lower()
    type_map = {
        ".pdf": DocumentType.PDF,
        ".docx": DocumentType.DOCX,
        ".txt": DocumentType.TXT,
        ".md": DocumentType.MD,
        ".png": DocumentType.IMAGE,
        ".jpg": DocumentType.IMAGE,
        ".jpeg": DocumentType.IMAGE,
        ".gif": DocumentType.IMAGE,
        ".webp": DocumentType.IMAGE,
        ".xlsx": DocumentType.SPREADSHEET,
        ".csv": DocumentType.SPREADSHEET,
    }
    return type_map.get(ext, DocumentType.UNKNOWN)


def create_app() -> dict[str, Any]:
    """Composition root: create and wire concrete implementations.

    Returns a mapping with commonly used components.
    """
    parser = DocumentParser(converter_provider=ConverterFactory)
    chunking_config = ChunkingConfig()
    llm_service = LLMService(mock=False)
    chunking_engine = ChunkingEngine(config=chunking_config, llm_service=llm_service, enable_enrichment=True)
    loader_factory = LoaderFactory

    embedder = BGETextEmbedder()
    vector_store = ChromaVectorStore(db_path=settings.db_path, collection_name="documents")

    return {
        "parser": parser,
        "chunking_engine": chunking_engine,
        "loader_factory": loader_factory,
        "embedder": embedder,
        "vector_store": vector_store,
    }


def main() -> None:
    logger = get_logger(__name__)
    logger.info("Starting Docuflow Pipeline")

    # Ensure directories exist
    ensure_directories()

    # Build app components
    app = create_app()
    parser = app["parser"]
    chunking_engine = app["chunking_engine"]
    loader_factory = app["loader_factory"]
    embedder = app["embedder"]
    vector_store = app["vector_store"]

    # Run lightweight optional-dependency checks (logs availability) and set a flag
    check_optional_dependencies()
    paddle_available = is_paddleocr_available()

    input_dir = settings.input_dir
    files = list(input_dir.glob("*"))
    if not files:
        logger.info("No files found to process.")
        return

    for file_path in files:
        try:
            # Skip directories and hidden files
            if not file_path.is_file() or file_path.name.startswith("."):
                logger.debug(f"Skipping non-file or hidden: {file_path}")
                continue

            # If paddle OCR backend isn't available, skip image files early with a clear log.
            if not paddle_available and file_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
                logger.warning(f"Skipping image {file_path.name} because PaddleOCR/PPStructureV3 is not available.")
                continue

            # Load document
            try:
                loader = loader_factory.get_loader(str(file_path))
            except ValueError:
                logger.warning(f"No loader for {file_path.suffix}; skipping file")
                continue

            raw_documents = loader.load(str(file_path))
            if not raw_documents:
                logger.warning(f"No content loaded for {file_path}, skipping file.")
                continue

            raw_doc = raw_documents[0]
            doc_id = DocumentContext.generate_document_id(content=raw_doc.content, source_path=str(file_path))

            with log_context(document_id=doc_id, stage="Ingestion"):
                logger.info(
                    f"Document received: source={file_path}, type={file_path.suffix}, size={file_path.stat().st_size} bytes"
                )

                # Parse / convert & clean document to text
                parsed_text = parser.parse(raw_doc)

                # Save markdown output
                md_out = settings.md_dir / f"{file_path.stem}.md"
                save_markdown(parsed_text, md_out)
                logger.info(f"Saved markdown: {md_out}")

                # Chunk with advanced ChunkingEngine
                doc_type = get_document_type(file_path)
                doc_ctx = DocumentContext.from_source(
                    source_path=str(file_path),
                    document_type=doc_type,
                    content=raw_doc.content,
                    parser=raw_doc.metadata.get("parser", "unknown"),
                    parser_version=raw_doc.metadata.get("parser_version", "unknown"),
                )
                chunk_batch = chunking_engine.chunk(
                    content=parsed_text,
                    document_type=doc_type,
                    metadata={
                        "source": str(file_path),
                        "filename": file_path.name,
                        "document_id": doc_ctx.document_id,
                        "document_name": doc_ctx.document_name,
                        "source_path": doc_ctx.source_path,
                        "parser": doc_ctx.parser,
                        "parser_version": doc_ctx.parser_version,
                    },
                )

                logger.info(
                    f"Produced {len(chunk_batch.chunks)} chunks ({chunk_batch.total_tokens} tokens) for {file_path}"
                )

                if chunk_batch.processing_errors:
                    logger.warning(f"Chunking errors: {chunk_batch.processing_errors}")

                # Save chunk metadata to JSON locally for visual auditing
                import json

                chunks_data = [chunk.to_dict() for chunk in chunk_batch.chunks]
                json_out = settings.md_dir / f"{file_path.stem}_chunks.json"
                with open(json_out, "w", encoding="utf-8") as f:
                    json.dump(chunks_data, f, indent=2, ensure_ascii=False)
                logger.info(f"Saved chunk metadata JSON: {json_out}")

                # Embed chunks and index into ChromaDB Vector store
                if chunk_batch.chunks:
                    logger.info(f"Generating vector embeddings for {len(chunk_batch.chunks)} chunks...")
                    texts = [chunk.content for chunk in chunk_batch.chunks]
                    embeddings = embedder.embed(texts)

                    ids = [chunk.chunk_id for chunk in chunk_batch.chunks]
                    documents = texts

                    # Flatten metadata dictionaries to satisfy ChromaDB schema requirements
                    metadatas = []
                    for chunk, emb in zip(chunk_batch.chunks, embeddings):
                        chunk.embedding = emb

                        meta = chunk.to_dict()
                        if "keywords" in meta:
                            meta["keywords"] = ", ".join(meta["keywords"])
                        if "hypothetical_questions" in meta:
                            meta["hypothetical_questions"] = ", ".join(meta["hypothetical_questions"])
                        if "content_type" in meta:
                            meta["content_type"] = str(meta["content_type"])
                        if "document_type" in meta:
                            meta["document_type"] = str(meta["document_type"])

                        # Extract and flatten nested custom metadata, avoiding duplicate keys
                        nested_meta = meta.get("metadata", {})
                        if isinstance(nested_meta, dict):
                            redundant_keys = {
                                "section",
                                "section_level",
                                "source",
                                "filename",
                                "source_path",
                                "document_id",
                                "document_name",
                                "heading",
                                "heading_level",
                                "parser",
                                "parser_version",
                            }
                            for k, v in nested_meta.items():
                                if k not in redundant_keys:
                                    meta[f"meta_{k}"] = str(v)
                            meta.pop("metadata", None)

                        metadatas.append(meta)

                    logger.info("Indexing chunks into ChromaDB...")
                    vector_store.add(ids=ids, documents=documents, metadata=metadatas, embeddings=embeddings)
                    logger.info(f"Successfully indexed {len(ids)} chunks in ChromaDB vector store.")

        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}", exc_info=True)
            continue

    logger.info("Processing complete")


if __name__ == "__main__":
    main()
