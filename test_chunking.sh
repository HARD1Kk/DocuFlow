#!/usr/bin/env bash
# Quick test runner for chunking quality evaluation
# Usage: ./test_chunking.sh

set -e

cd "$(dirname "$0")" || exit 1

echo "🔍 DocuFlow Chunking Quality Test Suite"
echo "========================================"
echo ""

# Run pytest tests
echo "📋 Running pytest test suite (19 tests)..."
uv run pytest tests/test_chunking_quality.py -v --tb=short 2>&1 | tail -30

echo ""
echo "📊 Analyzing markdown documents..."
echo "========================================"

# Run evaluator on markdown directory
uv run python src/docuflow/utils/chunking_quality_evaluator.py --dir data/markdown

echo ""
echo "✅ Testing complete!"
echo "📖 See CHUNKING_QUALITY_GUIDE.md for detailed documentation"
