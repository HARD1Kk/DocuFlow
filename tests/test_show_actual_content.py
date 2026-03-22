# tests/test_universal_document_processor.py

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from docuflow.core.chunking import StructureDetector
from docuflow.core.loaders import LoaderFactory
from docuflow.core.processing.parsers import DocumentParser, StructureAnalyzer


class UniversalDocumentTester:
    """Test any document format"""

    def __init__(self, document_path: str):
        self.document_path = Path(document_path)
        self.format = self.document_path.suffix.lower()

        # Validation
        if not self.document_path.exists():
            raise FileNotFoundError(f"Document not found: {document_path}")

        print(f"\n{'=' * 80}")
        print("UNIVERSAL DOCUMENT PROCESSOR TEST")
        print(f"{'=' * 80}")
        print(f"\nDocument: {self.document_path.name}")
        print(f"Format: {self.format}")
        print(f"Size: {self.document_path.stat().st_size} bytes")

    def process(self) -> dict:
        """Process document through complete pipeline"""

        results = {
            "document": self.document_path.name,
            "format": self.format,
            "size_bytes": self.document_path.stat().st_size,
            "steps": {},
        }

        try:
            # Step 1: Load
            print(f"\n{'─' * 80}")
            print("📂 STEP 1: LOAD DOCUMENT")
            print(f"{'─' * 80}")

            content, metadata = self._load_document()
            results["steps"]["load"] = {
                "status": "✅",
                "bytes_loaded": len(content) if isinstance(content, bytes) else len(content.encode()),
            }
            print("✅ Loaded successfully")
            print(f"   Content type: {type(content).__name__}")
            print(f"   Size: {len(content)} bytes")

            # Step 2: Parse
            print(f"\n{'─' * 80}")
            print("📖 STEP 2: PARSE DOCUMENT")
            print(f"{'─' * 80}")

            parsed_content = self._parse_document(content)
            with open("output.txt", "w", encoding="utf-8") as f:
                f.write(parsed_content)

            results["steps"]["parse"] = {"status": "✅", "chars": len(parsed_content), "preview": parsed_content[:200]}
            print("✅ Parsed successfully")
            print(f"   Characters: {len(parsed_content)}")
            print("\n📝 First 200 characters:")

            print(f"{'─' * 80}")
            print(parsed_content[:200])
            print(f"{'─' * 80}")

            # Step 3: Clean
            print(f"\n{'─' * 80}")
            print("🧹 STEP 3: CLEAN STRUCTURE")
            print(f"{'─' * 80}")

            cleaned_content = self._clean_document(parsed_content)
            removed = len(parsed_content) - len(cleaned_content)
            reduction = (removed / len(parsed_content) * 100) if parsed_content else 0

            results["steps"]["clean"] = {
                "status": "✅",
                "chars_after": len(cleaned_content),
                "chars_removed": removed,
                "reduction_percent": reduction,
            }
            print("✅ Cleaned successfully")
            print(f"   Original: {len(parsed_content)} chars")
            print(f"   Cleaned: {len(cleaned_content)} chars")
            print(f"   Removed: {removed} chars ({reduction:.1f}%)")

            # Step 4: Detect Structure
            print(f"\n{'─' * 80}")
            print("🔍 STEP 4: DETECT STRUCTURE")
            print(f"{'─' * 80}")

            structure = self._detect_structure(cleaned_content)
            results["steps"]["detect"] = {
                "status": "✅",
                "headings": len(structure["headings"]),
                "tables": len(structure["tables"]),
                "lists": len(structure["lists"]),
            }
            print("✅ Detection complete!")
            print(f"   📋 Headings: {len(structure['headings'])}")
            print(f"   📊 Tables: {len(structure['tables'])}")
            print(f"   📝 Lists: {len(structure['lists'])}")

            # Step 5: Show Results
            print(f"\n{'─' * 80}")
            print("📊 DETAILED RESULTS")
            print(f"{'─' * 80}")

            self._show_headings(structure["headings"])
            self._show_tables(structure["tables"], cleaned_content)
            self._show_lists(structure["lists"], cleaned_content)

            # Step 6: Summary
            print(f"\n{'=' * 80}")
            print("SUMMARY")
            print(f"{'=' * 80}")
            print(f"Document: {self.document_path.name}")
            print(f"Format: {self.format}")
            print(f"Original size: {len(parsed_content)} chars")
            print(f"Cleaned size: {len(cleaned_content)} chars")
            print(f"Reduction: {reduction:.1f}%")
            print("\nStructure detected:")
            print(f"  ✅ {len(structure['headings'])} headings")
            print(f"  ✅ {len(structure['tables'])} tables")
            print(f"  ✅ {len(structure['lists'])} lists")
            print(f"{'=' * 80}\n")

            results["status"] = "SUCCESS"
            results["structure"] = structure

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback

            traceback.print_exc()
            results["status"] = "FAILED"
            results["error"] = str(e)

        return results

    # ============ STEP IMPLEMENTATIONS ============

    def _load_document(self) -> tuple:
        """Load any document format"""

        try:
            # Use LoaderFactory to handle all formats
            loader = LoaderFactory.get_loader(str(self.document_path))
            raw_docs = loader.load(str(self.document_path))

            if not raw_docs:
                raise ValueError("No content loaded")

            raw_doc = raw_docs[0]

            # Return content and metadata
            return raw_doc.content, raw_doc.metadata

        except Exception as e:
            raise Exception(f"Failed to load {self.format} document: {e}")

    def _parse_document(self, content) -> str:
        """Parse document based on format"""

        try:
            # If content is bytes, we need to parse it
            if isinstance(content, bytes):
                # Create a temporary RawDocument for parser
                from docuflow.schemas import RawDocument

                raw_doc = RawDocument(
                    content=content,
                    source=str(self.document_path),
                    metadata={"filename": self.document_path.name, "format": self.format, "file_size": len(content)},
                )

                # Use appropriate parser
                if self.format in [".pdf", ".docx", ".txt", ".md"]:
                    parser = DocumentParser()
                    return parser.parse(raw_doc)
                elif self.format in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
                    from docuflow.core.processing.parsers.image_parser import ImageParser

                    parser = ImageParser()
                    return parser.parse(raw_doc)
                else:
                    raise ValueError(f"Unsupported format: {self.format}")

            # If content is already string, return as is
            return str(content)

        except Exception as e:
            raise Exception(f"Failed to parse {self.format} document: {e}")

    def _clean_document(self, content: str) -> str:
        """Clean document structure"""

        try:
            analyzer = StructureAnalyzer()
            return analyzer.analyze(content)
        except Exception as e:
            raise Exception(f"Failed to clean document: {e}")

    def _detect_structure(self, content: str) -> dict:
        """Detect structure in document"""

        try:
            detector = StructureDetector()
            return detector.detect(content)
        except Exception as e:
            raise Exception(f"Failed to detect structure: {e}")

    def _show_headings(self, headings: list) -> None:
        """Display detected headings"""

        if not headings:
            print("\n⚠️  No headings detected")
            return

        print(f"\n{'─' * 80}")
        print(f"HEADINGS ({len(headings)} total)")
        print(f"{'─' * 80}")

        for i, h in enumerate(headings[:10], 1):  # Show first 10
            indent = "  " * (h["level"] - 1)
            print(f"{i:2d}. {indent}{'#' * h['level']} {h['title']}")

        if len(headings) > 10:
            print(f"... and {len(headings) - 10} more headings")

    def _show_tables(self, tables: list, content: str) -> None:
        """Display detected tables"""

        if not tables:
            print("\n⚠️  No tables detected")
            return

        print(f"\n{'─' * 80}")
        print(f"TABLES ({len(tables)} total)")
        print(f"{'─' * 80}")

        for i, t in enumerate(tables[:5], 1):  # Show first 5
            print(f"\n{i}. Table at position {t['position']}")
            print(f"   ├─ Type: {t.get('type', 'unknown')}")
            print(f"   ├─ Rows: {t['rows']}")
            print(f"   ├─ Columns: {t.get('columns', 'N/A')}")
            print(f"   ├─ Size: {t['end'] - t['start']} characters")

            # Show preview
            table_content = content[t["start"] : t["end"]]
            preview = table_content[:150].replace("\n", " ")
            print(f"   └─ Preview: {preview}...")

        if len(tables) > 5:
            print(f"\n... and {len(tables) - 5} more tables")

    def _show_lists(self, lists: list, content: str) -> None:
        """Display detected lists"""

        if not lists:
            print("\n⚠️  No lists detected")
            return

        print(f"\n{'─' * 80}")
        print(f"LISTS ({len(lists)} total)")
        print(f"{'─' * 80}")

        for i, li in enumerate(lists[:5], 1):  # Show first 5
            print(f"\n{i}. List at position {li['position']}")
            print(f"   ├─ Items: {li['items']}")
            print(f"   ├─ Size: {li['end'] - li['start']} characters")

            # Show preview
            list_content = content[li["start"] : li["end"]]
            lines = list_content.split("\n")[:3]
            for line in lines:
                if line.strip():
                    print(f"   ├─ {line.strip()[:60]}")

        if len(lists) > 5:
            print(f"... and {len(lists) - 5} more lists")


# ============ MAIN TEST FUNCTION ============


def test_document(document_path: str, verbose: bool = True) -> dict:
    """
    Test any document

    Args:
        document_path: Path to document (PDF, DOCX, PNG, JPG, etc.)
        verbose: Print detailed output

    Returns:
        Dictionary with results
    """

    try:
        tester = UniversalDocumentTester(document_path)
        results = tester.process()
        return results

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback

        traceback.print_exc()
        return {"status": "FAILED", "error": str(e)}


# ============ PYTEST INTEGRATION ============


def test_sample_docx():
    """Test sample DOCX file"""
    results = test_document("/home/hardik/projects/DocuFlow/data/sample2.docx")
    assert results["status"] == "SUCCESS"


def test_document_from_env():
    """Test document specified in TEST_DOCUMENT env variable"""
    import os

    doc_path = os.environ.get("TEST_DOCUMENT")

    if not doc_path:
        print("Set TEST_DOCUMENT environment variable to test a specific document")
        return

    results = test_document(doc_path)
    assert results["status"] == "SUCCESS"


# ============ CLI USAGE ============

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Universal document processor test")
    parser.add_argument(
        "document",
        nargs="?",
        default="/home/hardik/projects/DocuFlow/data/sample2.docx",
        help="Path to document (PDF, DOCX, PNG, JPG, etc.)",
    )
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")

    args = parser.parse_args()

    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + " UNIVERSAL DOCUMENT PROCESSOR TEST ".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")

    results = test_document(args.document, verbose=args.verbose)

    # Exit code based on results
    sys.exit(0 if results["status"] == "SUCCESS" else 1)
