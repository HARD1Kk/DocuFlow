# Graph Report - /home/hardik/projects/DocuFlow  (2026-05-11)

## Corpus Check
- 117 files · ~156,208 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 560 nodes · 796 edges · 68 communities (37 shown, 31 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 171 edges (avg confidence: 0.65)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Code Block Detection|Code Block Detection]]
- [[_COMMUNITY_Spreadsheet Processing|Spreadsheet Processing]]
- [[_COMMUNITY_Document Parsing Interfaces|Document Parsing Interfaces]]
- [[_COMMUNITY_Chunk Creation Logic|Chunk Creation Logic]]
- [[_COMMUNITY_Chunking Tests|Chunking Tests]]
- [[_COMMUNITY_Image Parsing|Image Parsing]]
- [[_COMMUNITY_Base Loader|Base Loader]]
- [[_COMMUNITY_Chunking Quality Evaluation|Chunking Quality Evaluation]]
- [[_COMMUNITY_Base Chunker|Base Chunker]]
- [[_COMMUNITY_Markdown Chunking|Markdown Chunking]]
- [[_COMMUNITY_PDF Processing|PDF Processing]]
- [[_COMMUNITY_Vector Storage|Vector Storage]]
- [[_COMMUNITY_Data Source Loaders|Data Source Loaders]]
- [[_COMMUNITY_Embedding Services|Embedding Services]]
- [[_COMMUNITY_Retriever Chain|Retriever Chain]]
- [[_COMMUNITY_Document Converters|Document Converters]]
- [[_COMMUNITY_Table Detection|Table Detection]]
- [[_COMMUNITY_List Detection|List Detection]]
- [[_COMMUNITY_Heading Detection|Heading Detection]]
- [[_COMMUNITY_Schema Definitions|Schema Definitions]]
- [[_COMMUNITY_Utilities & Helpers|Utilities & Helpers]]
- [[_COMMUNITY_Configuration|Configuration]]
- [[_COMMUNITY_Pipeline Processing|Pipeline Processing]]
- [[_COMMUNITY_Logging & Monitoring|Logging & Monitoring]]
- [[_COMMUNITY_Error Handling|Error Handling]]
- [[_COMMUNITY_Type Definitions|Type Definitions]]
- [[_COMMUNITY_Validation Logic|Validation Logic]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]

## God Nodes (most connected - your core abstractions)
1. `MarkdownChunker` - 32 edges
2. `ChunkingEngine` - 29 edges
3. `TestChunkingQuality` - 26 edges
4. `CodeChunker` - 26 edges
5. `ChunkingConfig` - 25 edges
6. `SpreadsheetChunker` - 19 edges
7. `ChunkBatch` - 18 edges
8. `UniversalDocumentTester` - 16 edges
9. `BaseChunker` - 16 edges
10. `DocumentType` - 16 edges

## Surprising Connections (you probably didn't know these)
- `UniversalDocumentTester` --uses--> `HeadingDetector`  [INFERRED]
  tests/test_show_actual_content.py → src/docuflow/processing/chunking/detectors.py
- `UniversalDocumentTester` --uses--> `TableDetector`  [INFERRED]
  tests/test_show_actual_content.py → src/docuflow/processing/chunking/detectors.py
- `UniversalDocumentTester` --uses--> `ListDetector`  [INFERRED]
  tests/test_show_actual_content.py → src/docuflow/processing/chunking/detectors.py
- `ChunkingQualityMetrics` --uses--> `ChunkingEngine`  [INFERRED]
  tests/test_chunking_quality.py → src/docuflow/processing/chunking/chunking_engine.py
- `ChunkingQualityMetrics` --uses--> `CodeChunker`  [INFERRED]
  tests/test_chunking_quality.py → src/docuflow/processing/chunking/code_chunker.py

## Communities (68 total, 31 thin omitted)

### Community 0 - "Code Block Detection"
Cohesion: 0.05
Nodes (32): CodeBlock, CodeBlockDetector, DetectedElement, Heading, HeadingDetector, ListBlock, ListDetector, Detect all headings in content. (+24 more)

### Community 1 - "Spreadsheet Processing"
Cohesion: 0.06
Nodes (29): BaseConverter, Chunker for spreadsheet data.      Strategy:     - Each row becomes a chunk (if, Convert a row to markdown table format with headers., Split a large row into column groups., Create a chunk for a group of columns., Chunk spreadsheet content into row-based chunks., Create chunks from data rows., SpreadsheetChunker (+21 more)

### Community 2 - "Document Parsing Interfaces"
Cohesion: 0.05
Nodes (16): IRetriever, ITextEmbedder, IVectorStore, DocumentParser, Extract text from document formats using the converter layer., Analyze and clean structure, Clean and normalize parsed content, StructureAnalyzer (+8 more)

### Community 3 - "Chunk Creation Logic"
Cohesion: 0.05
Nodes (20): ABC, chunk(), Helper to create a chunk with consistent token counting., Approximate token count (4 chars per token average)., BaseConverter, Base contract for file converters., IDatasource, DATA SOURCE LAYER - Extraction only.      Responsibility: Load files and extract (+12 more)

### Community 4 - "Chunking Tests"
Cohesion: 0.06
Nodes (17): Test suite for evaluating chunking quality., Test that chunking engine initializes correctly., Test that markdown content is chunked into multiple chunks., Test that all chunks contain required fields., Test that chunks respect size constraints., Test that chunks meet minimum size requirements., Test that content is preserved after chunking., Test that token counts are consistent and non-zero. (+9 more)

### Community 5 - "Image Parsing"
Cohesion: 0.09
Nodes (18): ImageParser, Extract text from image formats using the converter layer., Test any document format, Load any document format, Parse document based on format, Clean document structure, Detect structure in document, Display detected headings (+10 more)

### Community 6 - "Base Loader"
Cohesion: 0.09
Nodes (16): BaseLoader, BaseLoader, Base loader with common implementation.     Subclasses only need to define SUPP, Verify file exists and is supported, Load file as raw bytes - same for all formats, DocumentLoader, Load documents: PDF, DOCX, TXT, MD, ImageLoader (+8 more)

### Community 7 - "Chunking Quality Evaluation"
Cohesion: 0.13
Nodes (14): ChunkingAnalysis, ChunkingQualityEvaluator, main(), Practical chunking quality evaluator for converted documents.  Usage:     pyt, Evaluates chunking quality for converted documents., Infer document type from file extension., Evaluate chunking quality for a single file., Calculate overall quality score (0-100). (+6 more)

### Community 8 - "Base Chunker"
Cohesion: 0.12
Nodes (13): BaseChunker, Abstract base for document-type specific chunkers.      Single Responsibility: E, Generate unique chunk ID., ChunkingEngine, Return list of supported document types., Main orchestrator for document chunking.      Responsibilities:     - Route cont, Initialize the chunking engine.          Args:             config: Chunking conf, Register all built-in chunkers. (+5 more)

### Community 9 - "Markdown Chunking"
Cohesion: 0.13
Nodes (11): MarkdownChunker, Chunk a single section respecting structure., Find protected elements within section content., Chunk content while keeping protected elements intact., Structure-aware chunker for markdown content.      Respects:     - Heading bound, Split regular text into chunks with size limits and overlap., Find natural split points (paragraph boundaries)., Force split content at max size boundaries. (+3 more)

### Community 10 - "PDF Processing"
Cohesion: 0.1
Nodes (10): Find the end of a code block using indentation., Create chunks from code structure., Merge overlapping or adjacent blocks., Check if a range is already covered by existing ranges., Split a large class into method chunks., Get content not covered by any range., Chunk remaining content by size., Chunk source code respecting code structure. (+2 more)

### Community 11 - "Vector Storage"
Cohesion: 0.16
Nodes (9): MetadataEnricher, Generate summary using extractive approach.          Strategy:         - Take fi, Generate summary using LLM (if available)., Generate hypothetical questions using rule-based approach.          Strategy:, Enriches chunks with additional metadata for better retrieval.      Single Respo, Generate hypothetical questions using LLM (if available)., Enrich all chunks with metadata.          Args:             chunks: List of chun, Enrich a single chunk with all metadata types. (+1 more)

### Community 12 - "Data Source Loaders"
Cohesion: 0.15
Nodes (12): get_document_type(), main(), Map file extension to DocumentType for chunking engine., Save markdown text to a file.      Args:         md_text: Markdown content to sa, save_markdown(), ensure_directories(), check_optional_dependencies(), _check_paddleocr() (+4 more)

### Community 13 - "Embedding Services"
Cohesion: 0.17
Nodes (10): ChunkingTestResult, main(), Results from chunking accuracy tests., Run chunking test on a single sample., Run all chunking tests., Add a chunk to the results., Calculate final metrics., Calculate overall chunking quality score (0-100). (+2 more)

### Community 14 - "Retriever Chain"
Cohesion: 0.17
Nodes (12): CodeChunker, Chunker for source code files.      Strategy:     - Respect function/class bound, Enum, Chunk, ContentType, DocumentType, Type of content in chunk., Source document type. (+4 more)

### Community 15 - "Document Converters"
Cohesion: 0.17
Nodes (9): BaseChunker, ImageChunker, Build image-specific metadata., Chunker for OCR-extracted text from images.      Strategy:     - OCR text is typ, Chunk OCR-extracted text from images., Chunk OCR text by line groups., ChunkBatch, Collection of chunks from one document. (+1 more)

### Community 17 - "List Detection"
Cohesion: 0.22
Nodes (6): ChunkingQualityMetrics, Generate a human-readable quality report., Metrics for evaluating chunking quality., Test quality metrics for markdown document., Test that chunking quality meets basic assertions., Test complete chunking workflow from raw content to metrics.

### Community 18 - "Heading Detection"
Cohesion: 0.25
Nodes (6): PaddleConfig, get_model_path(), get_paddle_ocr(), Utility functions for PaddleOCR configuration and initialization., Initialize and return a PaddleOCR instance with the given configuration.      Ar, Get the path to a cached PaddleOCR model.      Args:         model_name: Name of

### Community 19 - "Schema Definitions"
Cohesion: 0.33
Nodes (3): Chunk document content.          Args:             content: The document content, Get appropriate chunker for document type., Chunk multiple documents.          Args:             documents: List of dicts wi

### Community 22 - "Pipeline Processing"
Cohesion: 0.5
Nodes (3): BaseModel, Document, A single document or chunk to store in chroma

## Knowledge Gaps
- **202 isolated node(s):** `Test any document format`, `Process document through complete pipeline`, `Load any document format`, `Parse document based on format`, `Clean document structure` (+197 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **31 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MarkdownChunker` connect `Markdown Chunking` to `Code Block Detection`, `Chunking Tests`, `Base Chunker`, `Retriever Chain`, `Document Converters`, `List Detection`?**
  _High betweenness centrality (0.170) - this node is a cross-community bridge._
- **Why does `get_logger()` connect `Document Parsing Interfaces` to `Code Block Detection`, `Image Parsing`, `Base Loader`, `Base Chunker`, `Vector Storage`, `Data Source Loaders`?**
  _High betweenness centrality (0.144) - this node is a cross-community bridge._
- **Why does `ChunkingEngine` connect `Base Chunker` to `Spreadsheet Processing`, `Chunking Tests`, `Chunking Quality Evaluation`, `Markdown Chunking`, `Vector Storage`, `Data Source Loaders`, `Embedding Services`, `Retriever Chain`, `Document Converters`, `List Detection`, `Schema Definitions`?**
  _High betweenness centrality (0.130) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `MarkdownChunker` (e.g. with `ChunkingQualityMetrics` and `TestChunkingQuality`) actually correct?**
  _`MarkdownChunker` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `ChunkingEngine` (e.g. with `ChunkingQualityMetrics` and `TestChunkingQuality`) actually correct?**
  _`ChunkingEngine` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `TestChunkingQuality` (e.g. with `ChunkingEngine` and `CodeChunker`) actually correct?**
  _`TestChunkingQuality` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `CodeChunker` (e.g. with `ChunkingQualityMetrics` and `TestChunkingQuality`) actually correct?**
  _`CodeChunker` has 12 INFERRED edges - model-reasoned connections that need verification._