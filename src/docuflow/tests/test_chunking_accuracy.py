#!/usr/bin/env python3
"""Test script for chunking accuracy and scoring."""

from typing import Dict, List, Tuple

from docuflow.processing.chunking import ChunkingEngine
from docuflow.schemas.chunk import ChunkingConfig, DocumentType
from docuflow.utils import get_logger

logger = get_logger(__name__)


class ChunkingTestResult:
    """Results from chunking accuracy tests."""

    def __init__(self):
        self.total_chunks = 0
        self.total_tokens = 0
        self.avg_chunk_size = 0.0
        self.min_chunk_size = float("inf")
        self.max_chunk_size = 0
        self.overlap_ratio = 0.0
        self.structure_preserved = 0
        self.structure_total = 0
        self.errors: List[str] = []

    def add_chunk(self, chunk_text: str, has_structure: bool = False):
        """Add a chunk to the results."""
        chunk_size = len(chunk_text.split())
        self.total_chunks += 1
        self.total_tokens += chunk_size
        self.min_chunk_size = min(self.min_chunk_size, chunk_size)
        self.max_chunk_size = max(self.max_chunk_size, chunk_size)
        if has_structure:
            self.structure_preserved += 1
        self.structure_total += 1

    def finalize(self):
        """Calculate final metrics."""
        if self.total_chunks > 0:
            self.avg_chunk_size = self.total_tokens / self.total_chunks
        if self.structure_total > 0:
            self.structure_preservation_ratio = self.structure_preserved / self.structure_total

    def get_score(self) -> float:
        """Calculate overall chunking quality score (0-100)."""
        score = 100.0

        # Penalize chunks that are too small (< 50 tokens)
        if self.min_chunk_size < 50:
            score -= 10

        # Penalize chunks that are too large (> 1000 tokens)
        if self.max_chunk_size > 1000:
            score -= 10

        # Penalize high variance in chunk sizes
        if self.max_chunk_size > 0 and self.min_chunk_size != float("inf"):
            variance = (self.max_chunk_size - self.min_chunk_size) / self.avg_chunk_size
            if variance > 5:
                score -= 15

        # Reward structure preservation
        if hasattr(self, "structure_preservation_ratio"):
            score += self.structure_preservation_ratio * 10

        # Penalize errors
        score -= len(self.errors) * 5

        return max(0, min(100, score))

    def __str__(self) -> str:
        """String representation of results."""
        lines = [
            "Chunking Test Results:",
            f"  Total Chunks: {self.total_chunks}",
            f"  Total Tokens: {self.total_tokens}",
            f"  Avg Chunk Size: {self.avg_chunk_size:.1f} tokens",
            f"  Min Chunk Size: {self.min_chunk_size if self.min_chunk_size != float('inf') else 0} tokens",
            f"  Max Chunk Size: {self.max_chunk_size} tokens",
        ]
        if hasattr(self, "structure_preservation_ratio"):
            lines.append(f"  Structure Preservation: {self.structure_preservation_ratio:.1%}")
        lines.append(f"  Errors: {len(self.errors)}")
        lines.append(f"  Overall Score: {self.get_score():.1f}/100")
        if self.errors:
            lines.append("  Error Details:")
            for err in self.errors:
                lines.append(f"    - {err}")
        return "\n".join(lines)


# Test content samples
TEST_SAMPLES: Dict[str, Tuple[str, DocumentType]] = {
    "markdown_with_headings": (
        """# Introduction

This is the introduction section with some text.

## Background

Here is some background information about the topic.

### Details

More detailed information goes here.

## Conclusion

This concludes the document.
""",
        DocumentType.MD,
    ),
    "markdown_with_lists": (
        """# Features

Here are the main features:

- Feature 1: Description
- Feature 2: Description
- Feature 3: Description

## Requirements

1. Requirement A
2. Requirement B
3. Requirement C
""",
        DocumentType.MD,
    ),
    "markdown_with_tables": (
        """# Data Table

| Name | Age | City |
|------|-----|------|
| John | 25  | NYC  |
| Jane | 30  | LA   |

## Summary

The table shows user data.
""",
        DocumentType.MD,
    ),
    "markdown_with_code": (
        """# Code Example

Here is some Python code:

```python
def hello():
    print("Hello, World!")
```

## Usage

Call the function to see output.
""",
        DocumentType.MD,
    ),
    "plain_text": (
        """This is a plain text document without any special formatting.
It contains multiple paragraphs of text that should be chunked appropriately.
The chunking engine should handle this well and create reasonable chunks.
Each paragraph contains some information that is relevant to the document.
""",
        DocumentType.TXT,
    ),
    "pdf_like": (
        """Document Title

Chapter 1: Introduction

This chapter introduces the main concepts. It provides an overview of the document structure and the key topics that will be covered.

Chapter 2: Methodology

This chapter describes the methodology used in the research. It explains the approach taken and the rationale behind the decisions made.

Chapter 3: Results

This chapter presents the results of the analysis. It includes tables and figures that summarize the findings.
""",
        DocumentType.PDF,
    ),
}


def run_chunking_test(content: str, doc_type: DocumentType, config: ChunkingConfig) -> ChunkingTestResult:
    """Run chunking test on a single sample."""
    result = ChunkingTestResult()

    try:
        engine = ChunkingEngine(config=config, enable_enrichment=True)
        chunk_batch = engine.chunk(
            content=content,
            document_type=doc_type,
            metadata={"test": True},
        )

        for chunk in chunk_batch.chunks:
            result.add_chunk(chunk.content, has_structure=bool(chunk.metadata))

        if chunk_batch.processing_errors:
            result.errors.extend(chunk_batch.processing_errors)

    except Exception as e:
        result.errors.append(f"Chunking failed: {e}")

    result.finalize()
    return result


def main():
    """Run all chunking tests."""
    logger.info("Starting Chunking Accuracy Tests")

    config = ChunkingConfig()
    overall_score = 0.0
    test_count = 0

    for name, (content, doc_type) in TEST_SAMPLES.items():
        logger.info(f"\nTesting: {name} ({doc_type.value})")
        result = run_chunking_test(content, doc_type, config)
        print(result)
        overall_score += result.get_score()
        test_count += 1

    if test_count > 0:
        avg_score = overall_score / test_count
        print(f"\n{'=' * 50}")
        print(f"Average Score Across All Tests: {avg_score:.1f}/100")
        print(f"{'=' * 50}")

        if avg_score >= 80:
            print("✓ Chunking quality is GOOD")
        elif avg_score >= 60:
            print("⚠ Chunking quality is ACCEPTABLE")
        else:
            print("✗ Chunking quality needs IMPROVEMENT")

    logger.info("Chunking tests complete")


if __name__ == "__main__":
    main()
