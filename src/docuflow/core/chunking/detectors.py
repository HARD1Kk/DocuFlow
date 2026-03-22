# src/docuflow/core/processing/chunking/structure_detectors.py

import re
from dataclasses import dataclass
from typing import Any, Dict, List

from docuflow.utils import get_logger

logger = get_logger(__name__)


@dataclass
class Heading:
    """Detected heading"""

    title: str  # "Introduction"
    level: int  # 1, 2, 3
    position: int  # Character position in text
    line_number: int  # Line number


@dataclass
class Table:
    """Detected table"""

    start: int  # Start position
    end: int  # End position
    rows: int  # Number of rows


@dataclass
class ListBlock:
    """Detected list"""

    start: int  # Start position
    end: int  # End position
    items: int  # Number of items


class HeadingDetector:
    """Detect markdown headings (# ## ###)"""

    def __init__(self):
        self.logger = logger
        # Regex to find headings
        self.heading_pattern = r"^(#{1,6})\s+(.+)$"

    def detect(self, content: str) -> List[Dict[str, Any]]:
        """
        Detect all headings in content

        Args:
            content: Text content

        Returns:
            List of heading info
        """

        if not content or not content.strip():
            return []

        headings = []
        lines = content.split("\n")
        char_pos = 0

        for line_num, line in enumerate(lines):
            # Check if line is a heading
            match = re.match(self.heading_pattern, line)

            if match:
                # Extract heading info
                hash_marks = match.group(1)  # "##"
                title = match.group(2)  # "Introduction"
                level = len(hash_marks)  # 2

                heading = {
                    "title": title,
                    "level": level,
                    "position": char_pos,
                    "line_number": line_num,
                    "id": f"h{level}_{line_num}",
                }

                headings.append(heading)

                self.logger.debug(f"Found heading level {level}: '{title}' at pos {char_pos}")

            # Update character position
            char_pos += len(line) + 1  # +1 for newline

        self.logger.info(f"Detected {len(headings)} headings")
        return headings


class TableDetector:
    """Detect markdown tables (| header | data |)"""

    def __init__(self):
        self.logger = logger
        # Pattern for table row: | data | data |
        self.table_row_pattern = r"^\s*\|.+\|\s*$"
        # Pattern for table separator: |---|---|
        self.separator_pattern = r"^\s*\|[\s\-|:]+\|\s*$"

    def detect(self, content: str) -> List[Dict[str, Any]]:
        """
        Detect all tables in content

        Args:
            content: Text content

        Returns:
            List of table info
        """

        if not content or not content.strip():
            return []

        tables = []
        lines = content.split("\n")
        char_pos = 0
        i = 0

        while i < len(lines):
            line = lines[i]

            # Check if this is start of table
            if re.match(self.table_row_pattern, line):
                # Next line should be separator
                if i + 1 < len(lines) and re.match(self.separator_pattern, lines[i + 1]):
                    table_start = char_pos
                    table_rows = 0

                    # Count table rows
                    j = i
                    while j < len(lines) and re.match(self.table_row_pattern, lines[j]):
                        table_rows += 1
                        j += 1

                    table_end = sum(len(lines[k]) + 1 for k in range(i, j))

                    table = {
                        "start": table_start,
                        "end": table_start + table_end,
                        "rows": table_rows,
                        "position": char_pos,
                        "id": f"table_{len(tables)}",
                    }

                    tables.append(table)

                    self.logger.debug(f"Found table with {table_rows} rows at pos {table_start}")

                    # Skip past table
                    i = j - 1

            # Update character position
            char_pos += len(line) + 1
            i += 1

        self.logger.info(f"Detected {len(tables)} tables")
        return tables


class ListDetector:
    """Detect markdown lists (- item, * item)"""

    def __init__(self):
        self.logger = logger
        # Pattern for list item: - item or * item
        self.list_item_pattern = r"^\s*[-*]\s+.+$"

    def detect(self, content: str) -> List[Dict[str, Any]]:
        """
        Detect all lists in content

        Args:
            content: Text content

        Returns:
            List of list info
        """

        if not content or not content.strip():
            return []

        lists = []
        lines = content.split("\n")
        char_pos = 0
        i = 0

        while i < len(lines):
            line = lines[i]

            # Check if this is start of list
            if re.match(self.list_item_pattern, line):
                list_start = char_pos
                list_items = 0

                # Count list items
                j = i
                while j < len(lines) and (
                    re.match(self.list_item_pattern, lines[j]) or lines[j].strip() == ""  # Allow blank lines in list
                ):
                    if re.match(self.list_item_pattern, lines[j]):
                        list_items += 1
                    j += 1

                list_end = sum(len(lines[k]) + 1 for k in range(i, j))

                list_info = {
                    "start": list_start,
                    "end": list_start + list_end,
                    "items": list_items,
                    "position": char_pos,
                    "id": f"list_{len(lists)}",
                }

                lists.append(list_info)

                self.logger.debug(f"Found list with {list_items} items at pos {list_start}")

                # Skip past list
                i = j - 1

            # Update character position
            char_pos += len(line) + 1
            i += 1

        self.logger.info(f"Detected {len(lists)} lists")
        return lists


# Optional: Combined detector
class StructureDetector:
    """Detect all structure elements at once"""

    def __init__(self):
        self.heading_detector = HeadingDetector()
        self.table_detector = TableDetector()
        self.list_detector = ListDetector()
        self.logger = logger

    def detect(self, content: str) -> Dict[str, List[Any]]:
        """
        Detect all structure elements

        Args:
            content: Text content

        Returns:
            Dict with all structure info
        """

        self.logger.info("Detecting all structure elements...")

        return {
            "headings": self.heading_detector.detect(content),
            "tables": self.table_detector.detect(content),
            "lists": self.list_detector.detect(content),
        }
