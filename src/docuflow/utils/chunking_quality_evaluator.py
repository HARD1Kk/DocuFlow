"""
Practical chunking quality evaluator for converted documents.

Usage:
    python chunking_quality_evaluator.py --file path/to/converted_document.md
    python chunking_quality_evaluator.py --dir path/to/markdown/directory
"""

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Optional

from docuflow.processing.chunking.chunking_engine import ChunkingEngine
from docuflow.schemas.chunk import ChunkingConfig, DocumentType
from docuflow.utils import get_logger

logger = get_logger(__name__)


@dataclass
class ChunkingAnalysis:
    """Detailed analysis results for a single document."""

    file_path: str
    document_type: str
    file_size_bytes: int
    total_chunks: int
    total_tokens: int
    avg_chunk_size_chars: float
    min_chunk_size_chars: int
    max_chunk_size_chars: int
    avg_tokens_per_chunk: float
    chunks_with_summary: int
    chunks_with_keywords: int
    chunks_with_hypothetical_questions: int
    avg_keywords_per_chunk: float
    content_types_distribution: Dict[str, int]
    quality_score: float
    recommendations: list[str]

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(asdict(self), indent=2)

    def print_summary(self) -> None:
        """Print human-readable summary."""
        print("\n" + "=" * 70)
        print(f"CHUNKING QUALITY ANALYSIS: {Path(self.file_path).name}")
        print("=" * 70)
        print("\nDocument Info:")
        print(f"  File Size: {self.file_size_bytes:,} bytes")
        print(f"  Document Type: {self.document_type}")
        print("\nChunking Statistics:")
        print(f"  Total Chunks: {self.total_chunks}")
        print(f"  Total Tokens: {self.total_tokens:,}")
        print(f"  Avg Chunk Size: {self.avg_chunk_size_chars:,.0f} characters")
        print(f"  Min Chunk Size: {self.min_chunk_size_chars:,} characters")
        print(f"  Max Chunk Size: {self.max_chunk_size_chars:,} characters")
        print(f"  Avg Tokens/Chunk: {self.avg_tokens_per_chunk:.1f}")

        print("\nMetadata Enrichment:")
        summary_pct = (self.chunks_with_summary / self.total_chunks * 100) if self.total_chunks > 0 else 0
        keywords_pct = (self.chunks_with_keywords / self.total_chunks * 100) if self.total_chunks > 0 else 0
        hyp_pct = (self.chunks_with_hypothetical_questions / self.total_chunks * 100) if self.total_chunks > 0 else 0

        print(f"  Chunks with Summary: {self.chunks_with_summary}/{self.total_chunks} ({summary_pct:.1f}%)")
        print(f"  Chunks with Keywords: {self.chunks_with_keywords}/{self.total_chunks} ({keywords_pct:.1f}%)")
        print(
            f"  Chunks with Questions: {self.chunks_with_hypothetical_questions}/{self.total_chunks} ({hyp_pct:.1f}%)"
        )
        print(f"  Avg Keywords/Chunk: {self.avg_keywords_per_chunk:.1f}")

        print("\nContent Type Distribution:")
        for content_type, count in self.content_types_distribution.items():
            pct = (count / self.total_chunks * 100) if self.total_chunks > 0 else 0
            print(f"  {content_type}: {count} ({pct:.1f}%)")

        print("\nQuality Assessment:")
        print(f"  Overall Score: {self.quality_score:.2f}/100")
        score_label = self._get_score_label()
        print(f"  Rating: {score_label}")

        if self.recommendations:
            print("\nRecommendations:")
            for i, rec in enumerate(self.recommendations, 1):
                print(f"  {i}. {rec}")

        print("=" * 70 + "\n")

    def _get_score_label(self) -> str:
        """Get human-readable score label."""
        if self.quality_score >= 90:
            return "Excellent ⭐⭐⭐⭐⭐"
        elif self.quality_score >= 75:
            return "Good ⭐⭐⭐⭐"
        elif self.quality_score >= 60:
            return "Fair ⭐⭐⭐"
        elif self.quality_score >= 45:
            return "Poor ⭐⭐"
        else:
            return "Very Poor ⭐"


class ChunkingQualityEvaluator:
    """Evaluates chunking quality for converted documents."""

    def __init__(self, enable_enrichment: bool = False):
        config = ChunkingConfig()
        self.engine = ChunkingEngine(config=config, enable_enrichment=enable_enrichment)
        self.config = config

    def infer_document_type(self, file_path: Path) -> DocumentType:
        """Infer document type from file extension."""
        ext = file_path.suffix.lower()
        type_map = {
            ".md": DocumentType.MD,
            ".txt": DocumentType.TXT,
            ".py": DocumentType.CODE,
            ".js": DocumentType.CODE,
            ".ts": DocumentType.CODE,
            ".java": DocumentType.CODE,
            ".csv": DocumentType.SPREADSHEET,
        }
        return type_map.get(ext, DocumentType.UNKNOWN)

    def evaluate_file(self, file_path: Path) -> Optional[ChunkingAnalysis]:
        """Evaluate chunking quality for a single file."""
        try:
            # Read file
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return None

            content = file_path.read_text(encoding="utf-8")
            file_size = file_path.stat().st_size

            # Infer document type
            doc_type = self.infer_document_type(file_path)

            logger.info(f"Analyzing: {file_path.name} ({doc_type.value})")

            # Perform chunking
            chunk_batch = self.engine.chunk(
                content=content,
                document_type=doc_type,
                metadata={
                    "source": str(file_path),
                    "file_size": file_size,
                },
            )

            # Compute metrics
            chunks = chunk_batch.chunks
            if not chunks:
                logger.warning(f"No chunks created for {file_path.name}")
                return None

            chunk_sizes = [len(c.content) for c in chunks]
            token_counts = [c.token_count for c in chunks]
            content_types = {}
            for chunk in chunks:
                ct = chunk.content_type.value if hasattr(chunk.content_type, "value") else str(chunk.content_type)
                content_types[ct] = content_types.get(ct, 0) + 1

            chunks_with_summary = sum(1 for c in chunks if c.summary)
            chunks_with_keywords = sum(1 for c in chunks if c.keywords)
            chunks_with_questions = sum(1 for c in chunks if c.hypothetical_questions)
            total_keywords = sum(len(c.keywords) for c in chunks)

            # Calculate quality score
            quality_score = self._calculate_quality_score(
                num_chunks=len(chunks),
                chunk_sizes=chunk_sizes,
                token_counts=token_counts,
                has_metadata=(chunks_with_summary + chunks_with_keywords + chunks_with_questions),
            )

            # Generate recommendations
            recommendations = self._generate_recommendations(
                num_chunks=len(chunks),
                chunk_sizes=chunk_sizes,
                token_counts=token_counts,
                has_metadata=(chunks_with_summary + chunks_with_keywords + chunks_with_questions),
            )

            analysis = ChunkingAnalysis(
                file_path=str(file_path),
                document_type=doc_type.value,
                file_size_bytes=file_size,
                total_chunks=len(chunks),
                total_tokens=sum(token_counts),
                avg_chunk_size_chars=sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0,
                min_chunk_size_chars=min(chunk_sizes) if chunk_sizes else 0,
                max_chunk_size_chars=max(chunk_sizes) if chunk_sizes else 0,
                avg_tokens_per_chunk=sum(token_counts) / len(token_counts) if token_counts else 0,
                chunks_with_summary=chunks_with_summary,
                chunks_with_keywords=chunks_with_keywords,
                chunks_with_hypothetical_questions=chunks_with_questions,
                avg_keywords_per_chunk=total_keywords / len(chunks) if chunks else 0,
                content_types_distribution=content_types,
                quality_score=quality_score,
                recommendations=recommendations,
            )

            return analysis

        except Exception as e:
            logger.error(f"Error evaluating {file_path}: {e}", exc_info=True)
            return None

    def _calculate_quality_score(
        self,
        num_chunks: int,
        chunk_sizes: list[int],
        token_counts: list[int],
        has_metadata: int,
    ) -> float:
        """Calculate overall quality score (0-100)."""
        score = 50.0  # Base score

        # Bonus for having chunks
        if num_chunks > 0:
            score += 10
        else:
            return 0

        # Bonus for size consistency (standard deviation)
        if len(chunk_sizes) > 1:
            avg_size = sum(chunk_sizes) / len(chunk_sizes)
            variance = sum((x - avg_size) ** 2 for x in chunk_sizes) / len(chunk_sizes)
            std_dev = variance**0.5
            consistency_ratio = std_dev / (avg_size + 1)
            # Lower consistency ratio = higher score
            consistency_score = max(0, 15 - (consistency_ratio * 15))
            score += consistency_score
        else:
            score += 15

        # Bonus for token consistency
        if token_counts:
            avg_tokens = sum(token_counts) / len(token_counts)
            if 100 <= avg_tokens <= 1000:
                score += 15
            elif 50 <= avg_tokens <= 2000:
                score += 10
            else:
                score += 5

        # Bonus for metadata enrichment
        metadata_score = (has_metadata / num_chunks * 100) if num_chunks > 0 else 0
        score += metadata_score * 0.1  # Up to 10 points

        return min(100, max(0, score))

    def _generate_recommendations(
        self,
        num_chunks: int,
        chunk_sizes: list[int],
        token_counts: list[int],
        has_metadata: int,
    ) -> list[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []

        if not chunk_sizes:
            recommendations.append("No chunks created - verify input content is valid")
            return recommendations

        avg_size = sum(chunk_sizes) / len(chunk_sizes)

        # Size recommendations
        if avg_size < 50:
            recommendations.append("Chunks are very small - consider increasing min_chunk_tokens")
        elif avg_size > 5000:
            recommendations.append("Chunks are very large - consider decreasing max_chunk_tokens")

        # Token consistency recommendations
        if token_counts:
            avg_tokens = sum(token_counts) / len(token_counts)
            token_variance = sum((x - avg_tokens) ** 2 for x in token_counts) / len(token_counts)
            token_std = token_variance**0.5
            if token_std > avg_tokens * 0.5:
                recommendations.append(
                    "Token count varies significantly - consider adjusting chunk overlap or size constraints"
                )

            if avg_tokens < 50:
                recommendations.append("Average tokens/chunk is low - chunks may be too small")
            elif avg_tokens > 1500:
                recommendations.append("Average tokens/chunk is high - chunks may be too large for retrieval")

        # Metadata recommendations
        if has_metadata == 0:
            recommendations.append("No metadata enrichment detected - enable enrichment for better retrieval")

        # Content structure recommendations
        if len(chunk_sizes) < 3:
            recommendations.append("Few chunks created - verify the document has sufficient structure")

        return recommendations if recommendations else ["Chunking quality is good!"]

    def evaluate_directory(self, directory: Path) -> list[ChunkingAnalysis]:
        """Evaluate all markdown files in a directory."""
        results = []
        markdown_files = list(directory.glob("*.md")) + list(directory.glob("*.txt"))

        if not markdown_files:
            logger.warning(f"No markdown/text files found in {directory}")
            return results

        logger.info(f"Found {len(markdown_files)} files to analyze")

        for file_path in markdown_files:
            analysis = self.evaluate_file(file_path)
            if analysis:
                results.append(analysis)

        return results


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Evaluate chunking quality for converted documents")
    parser.add_argument(
        "--file",
        type=Path,
        help="Path to a single file to analyze",
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path("data/markdown"),
        help="Directory containing files to analyze (default: data/markdown)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--enrichment",
        action="store_true",
        help="Enable metadata enrichment during evaluation",
    )

    args = parser.parse_args()

    evaluator = ChunkingQualityEvaluator(enable_enrichment=args.enrichment)

    if args.file:
        # Single file analysis
        logger.info(f"Analyzing single file: {args.file}")
        analysis = evaluator.evaluate_file(args.file)
        if analysis:
            if args.json:
                print(analysis.to_json())
            else:
                analysis.print_summary()
        else:
            logger.error("Failed to analyze file")
            return 1

    else:
        # Directory analysis
        if not args.dir.exists():
            logger.error(f"Directory not found: {args.dir}")
            return 1

        logger.info(f"Analyzing directory: {args.dir}")
        results = evaluator.evaluate_directory(args.dir)

        if not results:
            logger.warning("No analyses completed")
            return 1

        # Print summaries
        for analysis in results:
            if args.json:
                print(analysis.to_json())
            else:
                analysis.print_summary()

        # Print comparison if multiple files
        if len(results) > 1:
            print("\n" + "=" * 70)
            print("COMPARISON SUMMARY")
            print("=" * 70)
            print(f"{'File':<30} {'Chunks':<10} {'Avg Size':<15} {'Quality':<10}")
            print("-" * 70)
            for analysis in sorted(results, key=lambda x: x.quality_score, reverse=True):
                filename = Path(analysis.file_path).name
                print(
                    f"{filename:<30} {analysis.total_chunks:<10} "
                    f"{analysis.avg_chunk_size_chars:<15.0f} {analysis.quality_score:<10.1f}"
                )
            print("=" * 70)

    return 0


if __name__ == "__main__":
    exit(main())
