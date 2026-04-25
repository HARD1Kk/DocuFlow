# src/docuflow/processing/chunking/metadata_enricher.py
"""Metadata enricher for chunks - adds summaries, keywords, and hypothetical questions.

Per rag.md Section 6.3:
- Summary: Brief overview of chunk content
- Keywords: Extracted key terms for search
- Hypothetical Questions: Questions this chunk could answer
  (question-to-question matching works better than question-to-paragraph)
"""

import re
from typing import List

from docuflow.schemas.chunk import Chunk, ChunkingConfig
from docuflow.utils import get_logger

logger = get_logger(__name__)


class MetadataEnricher:
    """
    Enriches chunks with additional metadata for better retrieval.

    Single Responsibility: Only handles metadata enrichment.
    Configurable: Can use LLM or rule-based extraction.
    """

    def __init__(self, config: ChunkingConfig | None = None, llm_service=None):
        self.config = config or ChunkingConfig()
        self.llm_service = llm_service  # Optional LLM for advanced enrichment
        self.logger = get_logger(self.__class__.__name__)

    def enrich(self, chunks: List[Chunk]) -> List[Chunk]:
        """
        Enrich all chunks with metadata.

        Args:
            chunks: List of chunks to enrich

        Returns:
            Same chunks with added metadata (mutated in place)
        """
        if not self.config.enable_metadata_enrichment:
            self.logger.debug("Metadata enrichment disabled")
            return chunks

        self.logger.info(f"Enriching {len(chunks)} chunks with metadata")

        for chunk in chunks:
            self._enrich_chunk(chunk)

        return chunks

    def _enrich_chunk(self, chunk: Chunk) -> None:
        """Enrich a single chunk with all metadata types."""
        if not chunk.content:
            return

        # Extract keywords (always done - rule-based)
        chunk.keywords = self._extract_keywords(chunk.content)

        # Generate summary (LLM if available, else rule-based)
        if self.llm_service:
            chunk.summary = self._generate_summary_llm(chunk.content)
        else:
            chunk.summary = self._generate_summary_rule_based(chunk.content)

        # Generate hypothetical questions (LLM if available, else rule-based)
        if self.llm_service:
            chunk.hypothetical_questions = self._generate_questions_llm(chunk.content)
        else:
            chunk.hypothetical_questions = self._generate_questions_rule_based(chunk.content)

    def _extract_keywords(self, content: str) -> List[str]:
        """
        Extract keywords from content using rule-based approach.

        Strategy:
        - Extract noun phrases and technical terms
        - Prioritize capitalized terms (proper nouns)
        - Remove stopwords
        """
        # Stopwords to filter out
        stopwords = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "this",
            "that",
            "these",
            "those",
            "it",
            "its",
        }

        # Extract potential keywords
        keywords = []

        # Pattern 1: Capitalized words (proper nouns, acronyms)
        capitalized = re.findall(r"\b[A-Z][a-zA-Z]{2,}\b", content)
        keywords.extend(capitalized)

        # Pattern 2: Technical terms (alphanumeric with hyphens/underscores)
        tech_terms = re.findall(r"\b[A-Za-z]+[-_]?[A-Za-z0-9]*\b", content)
        keywords.extend(term for term in tech_terms if len(term) > 3)

        # Pattern 3: Quoted terms
        quoted = re.findall(r'"([^"]+)"', content)
        keywords.extend(quoted)

        # Filter and deduplicate
        filtered = set()
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower not in stopwords and len(kw_lower) > 3 and not kw_lower.isdigit():
                filtered.add(kw_lower)

        # Return top keywords (limit to 10)
        return list(filtered)[:10]

    def _generate_summary_rule_based(self, content: str) -> str:
        """
        Generate summary using extractive approach.

        Strategy:
        - Take first sentence as topic sentence
        - Add key bullet points if present
        - Limit to 2 sentences or 100 words
        """
        sentences = re.split(r"[.!?]+", content)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return ""

        # Take first sentence as primary
        summary = sentences[0]

        # Add up to 2 bullet points if present
        bullet_points = re.findall(r"^[•\-\*]\s*(.+)$", content, re.MULTILINE)
        if bullet_points:
            summary += " Key points: " + "; ".join(bullet_points[:2])

        # Truncate if too long
        word_limit = 100
        words = summary.split()
        if len(words) > word_limit:
            summary = " ".join(words[:word_limit]) + "..."

        return summary

    def _generate_summary_llm(self, content: str) -> str:
        """Generate summary using LLM (if available)."""
        if not self.llm_service:
            return self._generate_summary_rule_based(content)

        try:
            prompt = f"Summarize this text in one sentence (max 100 words):\n\n{content[:2000]}"
            response = self.llm_service.generate(prompt)
            return response.strip()
        except Exception as e:
            self.logger.warning(f"LLM summary failed, falling back to rule-based: {e}")
            return self._generate_summary_rule_based(content)

    def _generate_questions_rule_based(self, content: str) -> List[str]:
        """
        Generate hypothetical questions using rule-based approach.

        Strategy:
        - Identify key entities and relationships
        - Form questions based on content patterns
        - Focus on what, how, why patterns
        """
        questions = []

        # Pattern 1: If content defines something, create "What is" questions
        definitions = re.findall(
            r"\b([A-Z][a-zA-Z]+)\s+(?:is|refers to|means|defined as)\s+([^\.]+)",
            content,
        )
        for term, definition in definitions:
            questions.append(f"What is {term}?")

        # Pattern 2: If content lists steps/process, create "How to" questions
        steps = re.findall(r"^(?:first|next|then|finally|step)\s+", content, re.IGNORECASE | re.MULTILINE)
        if steps:
            questions.append("How is this process performed?")
            questions.append("What are the steps involved?")

        # Pattern 3: If content has comparisons, create comparison questions
        comparisons = re.findall(
            r"\b([A-Za-z]+)\s+(?:vs|versus|compared to|unlike)\s+([A-Za-z]+)",
            content,
        )
        for item1, item2 in comparisons:
            questions.append(f"What is the difference between {item1} and {item2}?")

        # Pattern 4: If content mentions benefits/advantages
        if re.search(r"\b(benefit|advantage|improve|better)\b", content, re.IGNORECASE):
            questions.append("What are the benefits of this approach?")

        # Pattern 5: If content mentions problems/issues
        if re.search(r"\b(problem|issue|challenge|difficult)\b", content, re.IGNORECASE):
            questions.append("What challenges does this address?")

        # Pattern 6: Extract heading-based questions
        headings = re.findall(r"^#+\s*(.+)$", content, re.MULTILINE)
        for heading in headings[:3]:  # Limit to first 3 headings
            # Convert heading to question
            if heading.startswith("How "):
                questions.append(heading)
            elif heading.startswith("What "):
                questions.append(heading)
            elif heading.startswith("Why "):
                questions.append(heading)
            else:
                questions.append(f"What about {heading.lower()}?")

        # Deduplicate and limit
        questions = list(dict.fromkeys(questions))  # Preserve order, remove dupes
        return questions[:5]  # Max 5 questions

    def _generate_questions_llm(self, content: str) -> List[str]:
        """Generate hypothetical questions using LLM (if available)."""
        if not self.llm_service:
            return self._generate_questions_rule_based(content)

        try:
            prompt = f"""Generate 3-5 questions that this text could answer.
Format as a JSON array of strings.

Text:
{content[:2000]}
"""
            response = self.llm_service.generate(prompt)
            # Parse JSON response (simplified - should use proper JSON parser)
            questions = re.findall(r'"([^"]+)"', response)
            return questions if questions else self._generate_questions_rule_based(content)
        except Exception as e:
            self.logger.warning(f"LLM question generation failed: {e}")
            return self._generate_questions_rule_based(content)
