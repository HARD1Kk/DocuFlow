import re

from docuflow.utils import get_logger


class StructureAnalyzer:
    """Clean and normalize parsed content"""

    def __init__(self) -> None:
        self.logger = get_logger(__name__)

    def analyze(self, content: str) -> str:
        """Analyze and clean structure"""

        try:
            self.logger.info(f"Analyzing content: {len(content)} chars")

            # Remove Pandoc metadata anchors
            content = re.sub(r"\s*\{[^}]+\}\s*", "", content)
            self.logger.info("✅ Removed Pandoc anchors")

            # Remove image sizing attributes
            content = re.sub(r'\{width="[^"]+"\s+height="[^"]+"\}', "", content)
            self.logger.info("✅ Removed image sizing")

            # Remove empty headings
            content = re.sub(r"^#+\s*$", "", content, flags=re.MULTILINE)
            self.logger.info("✅ Removed empty headings")

            # Clean extra blank lines
            content = re.sub(r"\n\n\n+", "\n\n", content)
            self.logger.info("✅ Cleaned blank lines")

            # Strip
            content = content.strip()

            self.logger.info(f"✅ Analysis complete: {len(content)} chars")
            return content

        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            raise
