"""
Rule-based, deterministic text cleaning for PDF-extracted Markdown.

Replaces Gramformer with targeted fixes for extraction/OCR artifacts:
  - Stray control characters (optimized via compiled regex)
  - Unicode normalization (ligatures, etc.)
  - Hyphenated word merging across line breaks
  - Whitespace normalization
  - Space-before-punctuation correction
  - Inline code and Markdown link protection

All transformations preserve Markdown structure (headers, tables, lists, code blocks, blockquotes).
"""

from __future__ import annotations

import re
import unicodedata
from typing import Optional, Tuple

# ---------------------------------------------------------------------------
# Pre-compiled regex patterns for O(1) lookup and maximum performance
# ---------------------------------------------------------------------------

# Control characters to strip: Cc (excluding \t, \n, \r) + problematic Cf (excluding ZWJ/ZWNJ)
_CTRL_CHAR_RE = re.compile(
    r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]"  # Standard controls
    r"|[\u200b\u200e\u200f\ufeff]"              # Zero-width space, LTR/RTL marks, BOM
)

# Inline elements to protect from whitespace/punctuation destruction
_INLINE_CODE_RE = re.compile(r"`[^`]+`")
_LINK_RE = re.compile(r"!?\[[^\]]*\]\([^)]*\)")

# Placeholders using Unicode Private Use Area (U+E000 to U+F8FF)
# These will never appear in valid PDF text and are immune to NFKC normalization
_PH_PREFIX = "\ue000"
_PH_SUFFIX = "\ue001"

# Common English prefixes/words that indicate a compound hyphenated word rather than a line-wrap
_COMPOUND_PREFIXES = {
    "well", "large", "state", "self", "high", "low", "full", "half", 
    "non", "anti", "co", "pre", "post", "ex", "sub", "super", 
    "multi", "micro", "macro", "cross", "all", "ill", "off", "on"
}


class TextCleaner:
    """
    Deterministic, rule-based text cleaner for extracted Markdown.

    Parameters
    ----------
    merge_hyphens : bool, default=True
        Merge hyphenated words split across lines (e.g., "experi-\nment" → "experiment").
        Only applies to STANDARD_TEXT lines and respects compound-word patterns.
        Automatically disabled for non-English languages.

    collapse_whitespace : bool, default=True
        Collapse multiple internal spaces to one; preserve leading indentation.
        Does not apply to code blocks, protected lines, or inline code.

    strip_control_chars : bool, default=True
        Remove non-printable control characters (\\x00–\\x1f, \\x7f–\\x9f).
        Preserves tab (\\x09), newline (\\x0a), and other semantic whitespace.
        Preserves Zero-Width Joiner/Non-Joiner (U+200D/U+200C) for non-Latin scripts.

    normalize_unicode : bool, default=True
        Apply NFKC normalization (e.g., ligatures ﬁ → fi).
        Also normalizes curly quotes, dashes, and apostrophes to ASCII equivalents.

    fix_space_before_punctuation : bool, default=True
        Fix OCR artifacts: "word ." → "word.", "word ," → "word,", etc.

    language : str, default="en"
        Language code. If not "en", hyphen merging is auto-disabled (English-specific heuristic).
        Set explicitly to "en" to force hyphen merging on non-English text (not recommended).
    """

    def __init__(
        self,
        merge_hyphens: bool = True,
        collapse_whitespace: bool = True,
        strip_control_chars: bool = True,
        normalize_unicode: bool = True,
        fix_space_before_punctuation: bool = True,
        language: str = "en",
    ) -> None:
        self.merge_hyphens = merge_hyphens and (language == "en")
        self.collapse_whitespace = collapse_whitespace
        self.strip_control_chars = strip_control_chars
        self.normalize_unicode = normalize_unicode
        self.fix_space_before_punctuation = fix_space_before_punctuation
        self.language = language

    def clean(self, text: str) -> str:
        """
        Clean extracted Markdown text, preserving structure.

        Processing order (critical for idempotency):
          1. Split into lines and classify (protected vs. standard text).
          2. Apply per-line transformations (respecting protection flags).
          3. Merge hyphenated words across lines.
          4. Reconstruct and return.
        """
        if not text:
            return text

        lines = text.splitlines(keepends=False)

        # 1. Classify lines: track code fences, YAML frontmatter, and identify protected regions
        is_protected = self._classify_lines(lines)

        # 2. Apply per-line transformations (gated by protection flags)
        for i in range(len(lines)):
            if not is_protected[i]:
                lines[i] = self._clean_line(lines[i])

        # 3. Merge hyphenated words across lines (if enabled and language is English)
        if self.merge_hyphens:
            lines = self._merge_hyphens(lines, is_protected)

        # 4. Reconstruct
        result = "\n".join(lines)
        if text.endswith("\n"):
            result += "\n"
        return result

    def _classify_lines(self, lines: list[str]) -> list[bool]:
        """Classify each line as protected (True) or standard text (False)."""
        is_protected = []
        in_code_fence = False
        in_yaml_frontmatter = False

        for idx, line in enumerate(lines):
            stripped = line.strip()

            # YAML Frontmatter toggle (must start on the first line)
            if idx == 0 and stripped == "---":
                in_yaml_frontmatter = True
                is_protected.append(True)
                continue
            elif in_yaml_frontmatter and stripped == "---":
                in_yaml_frontmatter = False
                is_protected.append(True)
                continue

            if in_yaml_frontmatter:
                is_protected.append(True)
                continue

            # Code fence toggle
            if stripped.startswith("```"):
                in_code_fence = not in_code_fence
                is_protected.append(True)
                continue

            if in_code_fence:
                is_protected.append(True)
                continue

            if self._is_markdown_structure(stripped):
                is_protected.append(True)
            else:
                is_protected.append(False)

        return is_protected

    def _is_markdown_structure(self, stripped_line: str) -> bool:
        """Detect if a line is part of Markdown structure (protected from transformation)."""
        if not stripped_line:
            return False

        # Headings
        if re.match(r"^#{1,6}\s", stripped_line):
            return True

        # Blockquotes
        if stripped_line.startswith(">"):
            return True

        # Unordered lists
        if re.match(r"^[-*+]\s", stripped_line):
            return True

        # Ordered lists
        if re.match(r"^\d+\.\s", stripped_line):
            return True

        # Horizontal rules
        if re.match(r"^(?:(?:-{3,}|\*{3,}|_{3,}))\s*$", stripped_line):
            return True

        # STRICT Tables: Must have >= 2 pipes AND act as structural boundaries.
        if stripped_line.count("|") >= 2:
            is_table = (
                stripped_line.startswith("|") or
                stripped_line.endswith("|") or
                re.search(r"\s\|\s", stripped_line)
            )
            if is_table:
                return True

        # Table separator rows: |---|---|---
        if re.match(r"^\|?[\s\-:|]+\|?$", stripped_line):
            return True

        return False

    def _clean_line(self, line: str) -> str:
        """Apply all enabled transformations to a single standard text line."""
        # 1. Protect inline code and links from whitespace/punctuation destruction
        line, placeholders = self._protect_inline_elements(line)

        # 2. Unicode normalization
        if self.normalize_unicode:
            line = unicodedata.normalize("NFKC", line)
            line = self._normalize_special_chars(line)

        # 3. Strip control characters
        if self.strip_control_chars:
            line = _CTRL_CHAR_RE.sub("", line)

        # 4. Fix space-before-punctuation OCR artifacts
        if self.fix_space_before_punctuation:
            line = self._fix_space_before_punctuation(line)

        # 5. Collapse whitespace (preserve leading indentation)
        if self.collapse_whitespace:
            line = self._collapse_whitespace(line)

        # 6. Restore protected elements
        line = self._restore_inline_elements(line, placeholders)

        return line

    def _protect_inline_elements(self, text: str) -> Tuple[str, list[str]]:
        """Swap inline code and links with Private Use Area placeholders."""
        placeholders = []

        def replacer(match):
            placeholders.append(match.group(0))
            return f"{_PH_PREFIX}{len(placeholders) - 1}{_PH_SUFFIX}"

        text = _INLINE_CODE_RE.sub(replacer, text)
        text = _LINK_RE.sub(replacer, text)
        return text, placeholders

    def _restore_inline_elements(self, text: str, placeholders: list[str]) -> str:
        """Swap Private Use Area placeholders back to original text."""
        for i, original in enumerate(placeholders):
            text = text.replace(f"{_PH_PREFIX}{i}{_PH_SUFFIX}", original)
        return text

    def _normalize_special_chars(self, text: str) -> str:
        """Normalize curly quotes, dashes, and non-breaking spaces to ASCII equivalents."""
        replacements = {
            "\u201c": '"',  # Left double quote
            "\u201d": '"',  # Right double quote
            "\u2018": "'",  # Left single quote
            "\u2019": "'",  # Right single quote
            "\u2013": "-",  # En dash
            "\u2014": "--", # Em dash
            "\u00a0": " ",  # Non-breaking space
        }
        # Using str.translate is significantly faster than multiple str.replace() calls
        trans_table = str.maketrans(replacements)
        return text.translate(trans_table)

    def _fix_space_before_punctuation(self, text: str) -> str:
        """Fix OCR artifacts: 'word .' → 'word.'"""
        return re.sub(r"\s+([.,:;!?\)])", r"\1", text)

    def _collapse_whitespace(self, line: str) -> str:
        """Collapse multiple internal spaces to one; preserve leading indentation."""
        leading_match = re.match(r"^(\s*)", line)
        leading_spaces = leading_match.group(1) if leading_match else ""

        content = line.lstrip(" \t")
        content = re.sub(r" +", " ", content)
        content = content.rstrip(" ")

        return leading_spaces + content

    def _merge_hyphens(self, lines: list[str], is_protected: list[bool]) -> list[str]:
        """Merge hyphenated words split across unprotected lines."""
        merged_lines = []
        i = 0

        while i < len(lines):
            current_line = lines[i]

            # Keep merging with subsequent lines as long as possible
            while (
                i < len(lines) - 1
                and not is_protected[i]
                and not is_protected[i + 1]
                and current_line.strip()
                and lines[i + 1].strip()
            ):
                merge_result = self._try_merge_hyphen(current_line, lines[i + 1])
                if merge_result is not None:
                    current_line = merge_result
                    i += 1
                else:
                    break

            merged_lines.append(current_line)
            i += 1

        return merged_lines

    def _try_merge_hyphen(self, current_line: str, next_line: str) -> Optional[str]:
        """Attempt to merge two lines if a hyphenated word is split between them."""
        # Match a hyphen at the end of the line (optionally followed by whitespace)
        match = re.search(r"-\s*$", current_line)
        if not match:
            return None

        hyphen_index = match.start()
        if hyphen_index == 0 or not current_line[hyphen_index - 1].islower():
            return None

        next_stripped = next_line.lstrip()
        if not next_stripped or not next_stripped[0].islower():
            return None

        # Extract the word fragment directly preceding the hyphen
        word_match = re.search(r"([a-z]+)-\s*$", current_line)
        if word_match:
            prefix = word_match.group(1).lower()
            # If it's a known compound prefix, preserve the hyphen
            if prefix in _COMPOUND_PREFIXES:
                return current_line + next_stripped

        # If next fragment is a compound word (e.g., "body-builder"), keep the hyphen
        if re.match(r"^[a-z]+-[a-z]+", next_stripped):
            return current_line + next_stripped

        # Standard merge: remove the hyphen, join the words
        before_hyphen = current_line[:hyphen_index]
        return before_hyphen + next_stripped


# Backward compatibility
def create_text_cleaner(
    use_gpu: bool = False,
    max_candidates: int = 1,
    language: str = "en",
) -> TextCleaner:
    """Backward-compatible factory for TextCleaner."""
    return TextCleaner(language=language)