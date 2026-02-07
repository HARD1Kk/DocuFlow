import logging

from utils.chunking import get_sections
from utils.conversion import convert_pdf_to_md, save_markdown
from utils.load_fie import get_all_pdfs
from utils.settings import settings


def ingest_data() -> None:
    """Main entrypoint to convert and save a PDF to markdown.

    Automatically picks the latest PDF from the configured directory.
    """
    # Get all PDFs from the directory
    pdfs = get_all_pdfs(settings.pdf_dir)

    for pdf_path in pdfs:
        logging.info(f"Processing PDF: {pdf_path.name}")

        # Convert PDF to markdown
        md_text = convert_pdf_to_md(str(pdf_path))

        # Generate output filename based on input PDF name
        output_filename = pdf_path.stem + ".md"  # stem gets filename without extension
        output_path = settings.output_dir / output_filename

        # Save the markdown
        saved_path = save_markdown(md_text, str(output_path))

        # 3. Create Chunks
        chunks = get_sections(md_text)
        logging.info(f"Generated {len(chunks)} chunks from {pdf_path.name}")

        # Log first chunk for debug (optional)
        if chunks:
            logging.info(f"First chunk preview: {chunks[0].page_content[:200]}...")

        logging.info(f"Saved markdown to: {saved_path}")
