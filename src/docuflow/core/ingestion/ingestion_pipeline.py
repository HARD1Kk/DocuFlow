import logging

from docuflow.core.ingestion.chunking import get_sections
from docuflow.core.ingestion.conversion import convert_pdf_to_md, save_markdown
from docuflow.services.embedding_service import embed_texts
from docuflow.utils.load_fie import get_all_pdfs
from docuflow.configs.settings import settings

logger = logging.getLogger(__name__)


def ingest_data() -> None:
    """Main entrypoint to convert and save a PDF to markdown.

    Automatically picks the latest PDF from the configured directory.
    """
    # Get all PDFs from the directory
    pdfs = get_all_pdfs(settings.pdf_dir)

    for pdf_path in pdfs:
        logger.info(f"Processing PDF: {pdf_path.name}")

        # Convert PDF to markdown
        md_text = convert_pdf_to_md(str(pdf_path))

        # Generate output filename based on input PDF name
        output_filename = pdf_path.stem + ".md"  # stem gets filename without extension
        output_path = settings.output_dir / output_filename

        # Save the markdown
        save_markdown(md_text, str(output_path))

        # 3. Create Chunks
        chunks = get_sections(md_text)

        logger.info(f"Generated {len(chunks)} chunks from {pdf_path.name}")

        # Log first chunk for debug (optional)
        if chunks:
            logger.info(f"First chunk preview: {chunks[0].page_content[:200]}...")

        # Extract text content from chunks
        chunk_texts = [chunk.page_content for chunk in chunks]
        vectors = embed_texts(chunk_texts)
        logger.info(f"Generated {len(vectors)} vectors")
