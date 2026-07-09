# src/docuflow/processing/chunking/code_chunker.py
"""Chunker for source code files."""

import re
from typing import Dict, List

from docuflow.processing.chunking.base_chunker import BaseChunker
from docuflow.schemas.chunk import Chunk, ChunkBatch, ChunkingConfig, ContentType, DocumentType


class CodeChunker(BaseChunker):
    """
    Chunker for source code files.

    Strategy:
    - Respect function/class boundaries (don't split mid-function)
    - Group related functions (methods in same class)
    - Preserve imports and docstrings with their code
    - Add language-specific metadata
    """

    @property
    def supported_document_types(self) -> List[DocumentType]:
        return [DocumentType.CODE]

    # Language-specific patterns for code boundaries
    LANGUAGE_PATTERNS = {
        "python": {
            "function": re.compile(r"^(\s*)def\s+(\w+)\s*\(", re.MULTILINE),
            "class": re.compile(r"^(\s*)class\s+(\w+)", re.MULTILINE),
            "import": re.compile(r"^(import\s+\w+|from\s+\w+\s+import)", re.MULTILINE),
        },
        "javascript": {
            "function": re.compile(r"(?:function\s+\w+|\(\s*\w*\s*\)\s*=>|const\s+\w+\s*=\s*function)", re.MULTILINE),
            "class": re.compile(r"^(\s*)class\s+(\w+)", re.MULTILINE),
            "import": re.compile(r"^(import\s+|export\s+)", re.MULTILINE),
        },
        "java": {
            "method": re.compile(r"^\s*(public|private|protected)?\s*(static)?\s*\w+\s+\w+\s*\(", re.MULTILINE),
            "class": re.compile(r"^\s*(public|private)?\s*class\s+(\w+)", re.MULTILINE),
            "import": re.compile(r"^(import\s+|package\s+)", re.MULTILINE),
        },
    }

    def __init__(self, config: ChunkingConfig | None = None):
        super().__init__(config)
        self.language = "unknown"

    def chunk(self, content: str, metadata: Dict[str, any]) -> ChunkBatch:
        """Chunk source code respecting code structure."""
        if not content or not content.strip():
            return ChunkBatch(
                source=metadata.get("source", "unknown"),
                format=DocumentType.CODE,
                total_pages=1,
                total_tokens=0,
                processing_errors=["Empty code content"],
            )

        self.language = metadata.get("language", self._detect_language(content))
        patterns = self.LANGUAGE_PATTERNS.get(self.language, self.LANGUAGE_PATTERNS["python"])

        # Find code structure
        functions = self._find_code_blocks(content, patterns.get("function"))
        classes = self._find_code_blocks(content, patterns.get("class"))
        imports = self._find_code_blocks(content, patterns.get("import"))

        # Create chunks based on code structure
        chunks = self._create_code_chunks(content, functions, classes, imports, metadata)

        total_tokens = sum(c.token_count for c in chunks)

        return ChunkBatch(
            source=metadata.get("source", "unknown"),
            format=DocumentType.CODE,
            total_pages=1,
            total_tokens=total_tokens,
            chunks=chunks,
        )

    def _detect_language(self, content: str) -> str:
        """Detect programming language from content."""
        # Check for language-specific patterns
        if re.search(r"\bimport\s+\w+\s+from\s+\w+", content):
            return "python"
        elif re.search(r"\bfunction\s+\w+\s*\(|=>\s*\{", content):
            return "javascript"
        elif re.search(r"\bpublic\s+class\s+\w+|\bSystem\.out\.println", content):
            return "java"
        elif re.search(r"\bfunc\s+\w+\s*\(|package\s+\w+", content):
            return "go"
        return "unknown"

    def _find_code_blocks(self, content: str, pattern) -> List[Dict[str, any]]:
        """Find all occurrences of a code pattern."""
        if not pattern:
            return []

        blocks = []

        for match in pattern.finditer(content):
            start = match.start()
            start_line = content[:start].count("\n")

            # Find the end of this code block (next block or end of file)
            end = self._find_block_end(content, match.end())

            blocks.append(
                {
                    "start": start,
                    "end": end,
                    "start_line": start_line,
                    "name": match.group(2) if match.lastindex and match.lastindex >= 2 else "unknown",
                }
            )

        return blocks

    def _find_block_end(self, content: str, start: int) -> int:
        """Find the end of a code block using indentation."""
        lines = content[start:].split("\n")
        if not lines:
            return len(content)

        # Get initial indentation
        initial_indent = len(lines[0]) - len(lines[0].lstrip())

        end = start
        for i, line in enumerate(lines[1:], 1):
            if not line.strip():  # Empty line - continue
                continue

            current_indent = len(line) - len(line.lstrip())

            # If indentation decreases, we've exited the block
            if current_indent <= initial_indent and line.strip():
                break

            end = start + sum(len(li) + 1 for li in lines[: i + 1])

        return end

    def _create_code_chunks(
        self,
        content: str,
        functions: List[Dict[str, any]],
        classes: List[Dict[str, any]],
        imports: List[Dict[str, any]],
        metadata: Dict[str, any],
    ) -> List[Chunk]:
        """Create chunks from code structure."""
        chunks = []

        # Strategy: Group related code
        # 1. Imports as one chunk (if small enough)
        # 2. Each class as a chunk (or split if too large)
        # 3. Standalone functions as chunks
        # 4. Remaining code split by size

        covered_ranges: List[tuple[int, int]] = []

        # Add imports chunk
        if imports:
            import_content = self._merge_overlapping(content, imports)
            if self._count_tokens(import_content) <= self.config.max_chunk_size:
                chunk = self._create_chunk(
                    chunk_id=self._generate_chunk_id(metadata.get("source", "code"), len(chunks)),
                    content=import_content.strip(),
                    content_type=ContentType.CODE.value,
                    metadata={
                        "language": self.language,
                        "code_type": "imports",
                        "lines": import_content.count("\n") + 1,
                    },
                )
                chunks.append(chunk)
                covered_ranges.append((imports[0]["start"], imports[-1]["end"]))

        # Add class chunks
        for cls in classes:
            if self._is_covered(cls["start"], cls["end"], covered_ranges):
                continue

            class_content = content[cls["start"] : cls["end"]]
            class_tokens = self._count_tokens(class_content)

            if class_tokens <= self.config.max_chunk_size:
                chunk = self._create_chunk(
                    chunk_id=self._generate_chunk_id(metadata.get("source", "code"), len(chunks)),
                    content=class_content.strip(),
                    content_type=ContentType.CODE.value,
                    metadata={
                        "language": self.language,
                        "code_type": "class",
                        "name": cls["name"],
                        "lines": class_content.count("\n") + 1,
                    },
                )
                chunks.append(chunk)
                covered_ranges.append((cls["start"], cls["end"]))
            else:
                # Class too large - split by methods
                method_chunks = self._split_class_by_methods(class_content, cls["name"], len(chunks))
                chunks.extend(method_chunks)

        # Add function chunks
        for func in functions:
            if self._is_covered(func["start"], func["end"], covered_ranges):
                continue

            func_content = content[func["start"] : func["end"]]
            func_tokens = self._count_tokens(func_content)

            if func_tokens <= self.config.max_chunk_size:
                chunk = self._create_chunk(
                    chunk_id=self._generate_chunk_id(metadata.get("source", "code"), len(chunks)),
                    content=func_content.strip(),
                    content_type=ContentType.CODE.value,
                    metadata={
                        "language": self.language,
                        "code_type": "function",
                        "name": func["name"],
                        "lines": func_content.count("\n") + 1,
                    },
                )
                chunks.append(chunk)
                covered_ranges.append((func["start"], func["end"]))

        # Handle remaining code
        remaining = self._get_remaining_content(content, covered_ranges)
        if remaining:
            remaining_chunks = self._chunk_remaining(remaining, metadata, len(chunks))
            chunks.extend(remaining_chunks)

        return chunks

    def _merge_overlapping(self, content: str, blocks: List[Dict[str, any]]) -> str:
        """Merge overlapping or adjacent blocks."""
        if not blocks:
            return ""

        # Sort by start position
        sorted_blocks = sorted(blocks, key=lambda b: b["start"])

        merged = [sorted_blocks[0]]
        for block in sorted_blocks[1:]:
            if block["start"] <= merged[-1]["end"]:
                # Overlapping - extend the last block
                merged[-1]["end"] = max(merged[-1]["end"], block["end"])
            else:
                merged.append(block)

        # Extract content from merged blocks
        return "\n\n".join(content[b["start"] : b["end"]] for b in merged)

    def _is_covered(self, start: int, end: int, ranges: List[tuple[int, int]]) -> bool:
        """Check if a range is already covered by existing ranges."""
        for range_start, range_end in ranges:
            if start >= range_start and end <= range_end:
                return True
        return False

    def _split_class_by_methods(
        self,
        class_content: str,
        class_name: str,
        chunk_index: int,
    ) -> List[Chunk]:
        """Split a large class into method chunks."""
        chunks = []
        lines = class_content.split("\n")

        current_method: List[str] = []
        current_tokens = 0

        for line in lines:
            line_tokens = self._count_tokens(line)

            if current_tokens + line_tokens > self.config.max_chunk_size and current_method:
                # Emit current method
                method_content = "\n".join(current_method)
                chunk = self._create_chunk(
                    chunk_id=self._generate_chunk_id(f"{class_name}_method", chunk_index + len(chunks)),
                    content=method_content.strip(),
                    content_type=ContentType.CODE.value,
                    metadata={
                        "language": self.language,
                        "code_type": "class_method",
                        "class_name": class_name,
                        "lines": len(current_method),
                    },
                )
                chunks.append(chunk)
                current_method = []
                current_tokens = 0

            current_method.append(line)
            current_tokens += line_tokens

        # Emit final method
        if current_method:
            method_content = "\n".join(current_method)
            chunk = self._create_chunk(
                chunk_id=self._generate_chunk_id(f"{class_name}_method", chunk_index + len(chunks)),
                content=method_content.strip(),
                content_type=ContentType.CODE.value,
                metadata={
                    "language": self.language,
                    "code_type": "class_method",
                    "class_name": class_name,
                    "lines": len(current_method),
                },
            )
            chunks.append(chunk)

        return chunks

    def _get_remaining_content(self, content: str, covered_ranges: List[tuple[int, int]]) -> str:
        """Get content not covered by any range."""
        if not covered_ranges:
            return content

        # Sort ranges
        sorted_ranges = sorted(covered_ranges)

        remaining_parts = []
        last_end = 0

        for start, end in sorted_ranges:
            if start > last_end:
                remaining_parts.append(content[last_end:start])
            last_end = max(last_end, end)

        if last_end < len(content):
            remaining_parts.append(content[last_end:])

        return "\n\n".join(p for p in remaining_parts if p.strip())

    def _chunk_remaining(self, content: str, metadata: Dict[str, any], chunk_index: int) -> List[Chunk]:
        """Chunk remaining content by size."""
        chunks = []
        tokens = self._count_tokens(content)

        if tokens <= self.config.max_chunk_size:
            chunk = self._create_chunk(
                chunk_id=self._generate_chunk_id(metadata.get("source", "code"), chunk_index),
                content=content.strip(),
                content_type=ContentType.CODE.value,
                metadata={
                    "language": self.language,
                    "code_type": "other",
                    "lines": content.count("\n") + 1,
                },
            )
            chunks.append(chunk)
        else:
            # Split by lines
            lines = content.split("\n")
            current_lines: List[str] = []
            current_tokens = 0

            for line in lines:
                line_tokens = self._count_tokens(line)
                if current_tokens + line_tokens > self.config.max_chunk_size and current_lines:
                    chunk_content = "\n".join(current_lines)
                    chunk = self._create_chunk(
                        chunk_id=self._generate_chunk_id(metadata.get("source", "code"), chunk_index + len(chunks)),
                        content=chunk_content.strip(),
                        content_type=ContentType.CODE.value,
                        metadata={
                            "language": self.language,
                            "code_type": "other",
                            "lines": len(current_lines),
                        },
                    )
                    chunks.append(chunk)
                    current_lines = []
                    current_tokens = 0

                current_lines.append(line)
                current_tokens += line_tokens

            if current_lines:
                chunk_content = "\n".join(current_lines)
                chunk = self._create_chunk(
                    chunk_id=self._generate_chunk_id(metadata.get("source", "code"), chunk_index + len(chunks)),
                    content=chunk_content.strip(),
                    content_type=ContentType.CODE.value,
                    metadata={
                        "language": self.language,
                        "code_type": "other",
                        "lines": len(current_lines),
                    },
                )
                chunks.append(chunk)

        return chunks
