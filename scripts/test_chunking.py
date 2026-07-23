import sys
from pathlib import Path

# Add src to python path
sys.path.append("/home/hardik/projects/DocuFlow/src")

from docuflow.processing.chunking.markdown_chunker import MarkdownChunker

md_file = Path("/home/hardik/projects/DocuFlow/data/markdown/sample_pdf.md")
content = md_file.read_text(encoding="utf-8")

print(f"File length: {len(content)} characters")

# Detect headings and lists directly using detectors
chunker = MarkdownChunker()
headings = chunker.heading_detector.detect(content)
tables = chunker.table_detector.detect(content)
lists = chunker.list_detector.detect(content)
code_blocks = chunker.code_detector.detect(content)

print(f"\n--- DETECTED HEADINGS ({len(headings)}) ---")
for h in headings:
    print(f"Heading: level={h.level}, title={repr(h.title)}, start={h.start}, end={h.end}")

print(f"\n--- DETECTED LISTS ({len(lists)}) ---")
for l in lists:
    list_content = content[l.start : l.end]
    print(f"List: items={l.items}, type={l.list_type}, start={l.start}, end={l.end}")
    print(f"  Snippet: {repr(list_content[:100])}")

print(f"\n--- DETECTED TABLES ({len(tables)}) ---")
for t in tables:
    table_content = content[t.start : t.end]
    print(f"Table: rows={t.rows}, start={t.start}, end={t.end}")
    print(f"  Snippet: {repr(table_content[:100])}")

# Let's run the chunker on the content and print details
print("\n--- CHUNKER RUN ---")
batch = chunker.chunk(content, {"source": "sample_pdf.md"})
print(f"Total chunks: {len(batch.chunks)}")
for idx, chunk in enumerate(batch.chunks):
    print(f"\nChunk #{idx}: id={chunk.chunk_id}, type={chunk.content_type}, token_count={chunk.token_count}")
    print(f"Content: {repr(chunk.content)}")
    print(f"Metadata: {chunk.metadata}")
