# src/docuflow/processing/chunking/detectors.py
"""Structure detectors for identifying document elements.

Each detector follows Single Responsibility Principle - one detector per element type.
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from docuflow.utils import get_logger

logger = get_logger(__name__)


def clean_heading_title(title: str) -> str:
    """Clean markdown formatting from heading titles to produce plain text.

    E.g. '**Introduction**' -> 'Introduction'
         '**1.** Objectives' -> '1. Objectives'
    """
    if not title:
        return ""
    # Strip leading hashes if present
    text = re.sub(r"^#+\s*", "", title)
    # Remove bold/italic/code formatting: **, *, __, _, `
    text = re.sub(r"(\*\*|__|\*|_|`)(.*?)\1", r"\2", text)
    # Strip any remaining surrounding markdown punctuation
    text = text.strip("*_`").strip()
    return text


@dataclass
class DetectedElement:
    """Base class for detected structural elements."""

    start: int
    end: int
    element_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.end <= self.start:
            raise ValueError(f"Invalid element: end ({self.end}) must be > start ({self.start})")


@dataclass
class Heading(DetectedElement):
    """Detected heading with level and title."""

    title: str = ""
    level: int = 0
    line_number: int = 0
    element_type: str = "heading"

    def __post_init__(self):
        super().__post_init__()


@dataclass
class Table(DetectedElement):
    """Detected table with row count."""

    rows: int = 0
    columns: int = 0
    has_header: bool = True
    element_type: str = "table"

    def __post_init__(self):
        super().__post_init__()


@dataclass
class ListBlock(DetectedElement):
    """Detected list block."""

    items: int = 0
    list_type: str = "unordered"  # or "ordered"
    max_depth: int = 1
    element_type: str = "list"

    def __post_init__(self):
        super().__post_init__()


@dataclass
class CodeBlock(DetectedElement):
    """Detected code block."""

    language: str = ""
    lines: int = 0
    element_type: str = "code"

    def __post_init__(self):
        super().__post_init__()


class StructureDetector(ABC):
    """Abstract base for all structure detectors.

    Open/Closed Principle: Open for extension (new detectors), closed for modification.
    """

    @abstractmethod
    def detect(self, content: str) -> List[DetectedElement]:
        """Detect all elements of this type in content."""
        pass


class HeadingDetector(StructureDetector):
    """Detect markdown headings (# ## ###) and text headings (ALL CAPS, Underlined)."""

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        # Markdown headings: # H1, ## H2, etc.
        self.md_heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
        # Text headings: ALL CAPS or Title Case followed by newline
        self.cap_heading_pattern = re.compile(r"^([A-Z][A-Z\s]{3,30})\n", re.MULTILINE)
        # Underlined headings (text with === or --- below)
        self.underline_pattern = re.compile(r"^(.+)\n(=+|-+)\s*$", re.MULTILINE)

    def detect(self, content: str) -> List[Heading]:
        """Detect all headings in content."""
        if not content or not content.strip():
            return []

        headings: List[Heading] = []

        # Find markdown headings
        headings.extend(self._detect_markdown_headings(content))

        # Find capitalized headings
        headings.extend(self._detect_cap_headings(content))

        # Find underlined headings
        headings.extend(self._detect_underlined_headings(content))

        # Sort by position
        headings.sort(key=lambda h: h.start)

        # Deduplicate overlapping headings
        headings = self._deduplicate_headings(headings)

        self.logger.info(f"Detected {len(headings)} headings")
        return headings

    def _detect_markdown_headings(self, content: str) -> List[Heading]:
        """Detect markdown-style headings."""
        headings = []
        lines = content.split("\n")
        char_pos = 0

        for line_num, line in enumerate(lines):
            match = self.md_heading_pattern.match(line)
            if match:
                hash_marks = match.group(1)
                raw_title = match.group(2).strip()
                title = clean_heading_title(raw_title)
                level = len(hash_marks)

                heading = Heading(
                    start=char_pos,
                    end=char_pos + len(line),
                    title=title,
                    level=level,
                    line_number=line_num,
                    metadata={"style": "markdown"},
                )
                headings.append(heading)

            char_pos += len(line) + 1

        return headings

    def _detect_cap_headings(self, content: str) -> List[Heading]:
        """Detect ALL CAPS headings."""
        headings = []

        for match in self.cap_heading_pattern.finditer(content):
            raw_title = match.group(1).strip()
            title = clean_heading_title(raw_title)
            start = match.start()

            heading = Heading(
                start=start,
                end=match.end(),
                title=title,
                level=2,  # Treat as H2 equivalent
                line_number=content[:start].count("\n"),
                metadata={"style": "caps"},
            )
            headings.append(heading)

        return headings

    def _detect_underlined_headings(self, content: str) -> List[Heading]:
        """Detect underlined headings (=== or --- below)."""
        headings = []

        for match in self.underline_pattern.finditer(content):
            raw_title = match.group(1).strip()
            title = clean_heading_title(raw_title)
            underline = match.group(2)
            level = 1 if "=" in underline else 2

            heading = Heading(
                start=match.start(),
                end=match.end(),
                title=title,
                level=level,
                line_number=content[: match.start()].count("\n"),
                metadata={"style": "underlined", "underline_char": underline[0]},
            )
            headings.append(heading)

        return headings

    def _deduplicate_headings(self, headings: List[Heading]) -> List[Heading]:
        """Remove overlapping headings, keep the most specific one."""
        if not headings:
            return []

        deduped: List[Heading] = []
        last_end = -1

        for heading in sorted(headings, key=lambda h: (h.start, -h.level)):
            if heading.start >= last_end:
                deduped.append(heading)
                last_end = heading.end

        return deduped


class TableDetector(StructureDetector):
    """Detect markdown tables and ASCII tables."""

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.table_row_pattern = re.compile(r"^\s*\|.+\|\s*$")
        self.separator_pattern = re.compile(r"^\s*\|[\s\-:|]+\|\s*$")
        # ASCII tables (using +---+---+)
        self.ascii_border_pattern = re.compile(r"^\s*\+[-+]+\+\s*$")

    def detect(self, content: str) -> List[Table]:
        """Detect all tables in content."""
        if not content or not content.strip():
            return []

        tables: List[Table] = []

        # Find markdown tables
        tables.extend(self._detect_markdown_tables(content))

        # Find ASCII tables
        tables.extend(self._detect_ascii_tables(content))

        # Sort by position
        tables.sort(key=lambda t: t.start)

        self.logger.info(f"Detected {len(tables)} tables")
        return tables

    def _detect_markdown_tables(self, content: str) -> List[Table]:
        """Detect markdown-style tables."""
        tables = []
        lines = content.split("\n")
        char_pos = 0
        i = 0

        while i < len(lines):
            line = lines[i]

            if self.table_row_pattern.match(line):
                # Check for separator on next line
                if i + 1 < len(lines) and self.separator_pattern.match(lines[i + 1]):
                    table_start = char_pos
                    table_rows = 0
                    cols = len([c for c in line.split("|") if c.strip()])

                    # Count all table rows
                    j = i
                    while j < len(lines) and self.table_row_pattern.match(lines[j]):
                        table_rows += 1
                        j += 1

                    table_end = sum(len(lines[k]) + 1 for k in range(i, j))

                    table = Table(
                        start=table_start,
                        end=table_start + table_end,
                        rows=table_rows - 1,  # Exclude header
                        columns=cols,
                        has_header=True,
                        metadata={"style": "markdown"},
                    )
                    tables.append(table)

                    i = j - 1

            char_pos += len(line) + 1
            i += 1

        return tables

    def _detect_ascii_tables(self, content: str) -> List[Table]:
        """Detect ASCII art tables with +---+ borders."""
        tables = []
        lines = content.split("\n")
        i = 0

        while i < len(lines):
            if self.ascii_border_pattern.match(lines[i]):
                table_start = sum(len(lines[k]) + 1 for k in range(i))
                table_rows = 0
                cols = lines[i].count("+") - 1

                j = i
                while j < len(lines):
                    if self.ascii_border_pattern.match(lines[j]):
                        table_rows += 1
                    elif not (lines[j].strip() == "" or lines[j][0] in "|+"):
                        break
                    j += 1

                if table_rows >= 2:  # At least top and bottom border
                    table_end = sum(len(lines[k]) + 1 for k in range(i, j))

                    table = Table(
                        start=table_start,
                        end=table_start + table_end,
                        rows=table_rows - 1,
                        columns=cols,
                        has_header=True,
                        metadata={"style": "ascii"},
                    )
                    tables.append(table)

                i = j - 1

            i += 1

        return tables


class ListDetector(StructureDetector):
    """Detect ordered and unordered lists."""

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.unordered_patterns = [
            re.compile(r"^\s*[-*+]\s+\S"),  # -, *, + bullets
            re.compile(r"^\s*[•◦▪▸►]"),  # Unicode bullets
        ]
        self.ordered_pattern = re.compile(r"^\s*(\d+\.|[ivxlcdm]+\)|\([ivxlcdm]+\))\s+\S", re.IGNORECASE)

    def detect(self, content: str) -> List[ListBlock]:
        """Detect all lists in content."""
        if not content or not content.strip():
            return []

        lists: List[ListBlock] = []
        lines = content.split("\n")
        char_pos = 0
        i = 0

        while i < len(lines):
            line = lines[i]
            list_type = self._get_list_type(line)

            if list_type:
                list_start = char_pos
                list_items = 0
                max_depth = 1

                # Count list items and track depth
                j = i
                while j < len(lines):
                    check_line = lines[j]
                    depth = (len(check_line) - len(check_line.lstrip())) // 2 + 1

                    if self._is_list_item(check_line):
                        list_items += 1
                        max_depth = max(max_depth, depth)
                        j += 1
                    elif check_line.strip() == "":
                        # Allow blank lines within list
                        j += 1
                    else:
                        break

                list_end = sum(len(lines[k]) + 1 for k in range(i, j))

                list_block = ListBlock(
                    start=list_start,
                    end=list_start + list_end,
                    items=list_items,
                    list_type=list_type,
                    max_depth=max_depth,
                    metadata={"depth": max_depth},
                )
                lists.append(list_block)

                i = j - 1

            char_pos += len(line) + 1
            i += 1

        self.logger.info(f"Detected {len(lists)} lists")
        return lists

    def _get_list_type(self, line: str) -> Optional[str]:
        """Determine list type from line."""
        for pattern in self.unordered_patterns:
            if pattern.match(line):
                return "unordered"

        if self.ordered_pattern.match(line):
            return "ordered"

        return None

    def _is_list_item(self, line: str) -> bool:
        """Check if line is a list item."""
        return self._get_list_type(line) is not None


class CodeBlockDetector(StructureDetector):
    """Detect code blocks (markdown fences and indented code)."""

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.fence_pattern = re.compile(r"^(```|~~~)(\w*)\s*$", re.MULTILINE)
        self.indent_pattern = re.compile(r"^(    |\t).+$", re.MULTILINE)

    def detect(self, content: str) -> List[CodeBlock]:
        """Detect all code blocks in content."""
        if not content or not content.strip():
            return []

        code_blocks: List[CodeBlock] = []
        lines = content.split("\n")

        # Find fenced code blocks
        code_blocks.extend(self._detect_fenced_blocks(content, lines))

        # Find indented code blocks
        code_blocks.extend(self._detect_indented_blocks(content, lines))

        # Sort by position
        code_blocks.sort(key=lambda c: c.start)

        self.logger.info(f"Detected {len(code_blocks)} code blocks")
        return code_blocks

    def _detect_fenced_blocks(self, content: str, lines: List[str]) -> List[CodeBlock]:
        """Detect fenced code blocks (``` or ~~~)."""
        blocks = []
        i = 0

        while i < len(lines):
            match = self.fence_pattern.match(lines[i])
            if match:
                language = match.group(2) or "unknown"
                start_pos = sum(len(lines[k]) + 1 for k in range(i))
                fence = match.group(1)

                # Find closing fence
                j = i + 1
                while j < len(lines):
                    if self.fence_pattern.match(lines[j]):
                        end_pos = sum(len(lines[k]) + 1 for k in range(i, j + 1))

                        block = CodeBlock(
                            start=start_pos,
                            end=end_pos,
                            language=language,
                            lines=j - i - 1,
                            metadata={"fence": fence},
                        )
                        blocks.append(block)
                        i = j
                        break
                    j += 1

            i += 1

        return blocks

    def _detect_indented_blocks(self, content: str, lines: List[str]) -> List[CodeBlock]:
        """Detect indented code blocks (4 spaces or tab)."""
        blocks = []
        i = 0

        while i < len(lines):
            if self.indent_pattern.match(lines[i]):
                start_pos = sum(len(lines[k]) + 1 for k in range(i))
                start_line = i

                # Continue while lines are indented or blank
                while i < len(lines) and (self.indent_pattern.match(lines[i]) or lines[i].strip() == ""):
                    i += 1

                # Must have at least 2 indented lines to be a code block
                if i - start_line >= 2:
                    end_pos = sum(len(lines[k]) + 1 for k in range(start_line, i))

                    block = CodeBlock(
                        start=start_pos,
                        end=end_pos,
                        language="text",
                        lines=i - start_line,
                        metadata={"style": "indented"},
                    )
                    blocks.append(block)

            i += 1

        return blocks
