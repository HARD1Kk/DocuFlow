1. Restructuring Layer

Raw documents are parsed to understand structure such as:

headings

paragraphs

tables

code blocks

Structure must be preserved because it carries meaning.





2. Structure-Aware Chunking


Basic tutorials split text every fixed token size (e.g., 500 tokens).

Production systems instead use structure-aware chunking.

Examples:

headings stay attached to their paragraphs

tables remain intact

code functions are not split

Typical chunk size used by many teams:

256 – 512 tokens

Additionally:

Chunks often include overlap to preserve context between boundaries. 




3. Metadata Creation

Each chunk is enriched with additional information.

Metadata can include:

summaries

keywords

hypothetical questions the chunk could answer

Purpose of Hypothetical Questions

When the system performs retrieval, it matches:

user questions ↔ stored questions

This improves retrieval compared to matching:

question ↔ random paragraph

This technique increases search accuracy