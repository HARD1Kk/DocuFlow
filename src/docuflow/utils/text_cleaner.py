from __future__ import annotations

import re
from typing import Any


class TextCleaner:
    def __init__(self, use_gpu: bool = False, max_candidates: int = 1):
        self.use_gpu = use_gpu
        self.max_candidates = max_candidates
        self._tool: Any | None = None
        self._disabled_reason: str | None = None

    def clean(self, text: str) -> str:
        if not text:
            return text

        tool = self._get_tool()
        if tool is None:
            return text

        cleaned_lines = [self._clean_line(tool, line) for line in text.splitlines()]
        return "\n".join(cleaned_lines)

    def _get_tool(self) -> Any | None:
        if self._disabled_reason is not None:
            return None

        if self._tool is None:
            try:
                from gramformer import Gramformer

                self._tool = Gramformer(models=1, use_gpu=self.use_gpu)
            except Exception as exc:
                self._disabled_reason = str(exc)
                return None

        return self._tool

    def _clean_line(self, tool: Any, line: str) -> str:
        if not line.strip() or self._should_skip_line(line):
            return line

        sentence_parts = re.split(r"(?<=[.!?])\s+", line.strip())
        corrected_parts: list[str] = []

        for part in sentence_parts:
            if not part:
                continue

            try:
                candidates = list(tool.correct(part, max_candidates=self.max_candidates))
                corrected_parts.append(candidates[0] if candidates else part)
            except Exception:
                corrected_parts.append(part)

        corrected_line = " ".join(corrected_parts)
        return self._restore_indentation(line, corrected_line)

    def _should_skip_line(self, line: str) -> bool:
        stripped = line.strip()
        return (
            stripped.startswith("#")
            or stripped.startswith("```")
            or stripped.startswith("|")
            or stripped.startswith(">")
            or stripped.startswith("-")
            or stripped.startswith("*")
            or re.match(r"^\d+\.\s", stripped) is not None
        )

    def _restore_indentation(self, original_line: str, cleaned_line: str) -> str:
        leading_spaces = len(original_line) - len(original_line.lstrip(" "))
        return f"{' ' * leading_spaces}{cleaned_line}"
