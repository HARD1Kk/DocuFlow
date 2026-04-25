# DocuFlow/src/docuflow/utils/dependency_checks.py
"""
Lightweight optional-dependency checks.

This module performs non-invasive availability checks for optional libraries
(e.g. PaddleOCR) used by features such as image OCR. Checks are performed
using importlib.util.find_spec to avoid triggering heavy import-time side
effects when a package is not installed.

Provide:
- check_optional_dependencies() -> dict describing availability
- convenience helpers for common checks (is_paddleocr_available)

Keep this module minimal and safe to import at startup.
"""

from importlib import import_module
from importlib import util as importlib_util
from typing import Dict

from docuflow.utils.logger import get_logger

logger = get_logger(__name__)


def _check_paddleocr() -> Dict[str, bool]:
    """
    Check PaddleOCR availability and whether it exposes PPStructureV3.

    Returns:
        {
            "installed": bool,
            "ppstructure_v3": bool
        }
    """
    result = {"installed": False, "ppstructure_v3": False}

    spec = importlib_util.find_spec("paddleocr")
    if spec is None:
        logger.debug("paddleocr not found (find_spec returned None).")
        return result

    result["installed"] = True
    try:
        # Import only after confirming presence to avoid expensive import-time behavior
        paddleocr = import_module("paddleocr")
        ppv3 = getattr(paddleocr, "PPStructureV3", None)
        result["ppstructure_v3"] = ppv3 is not None
        if result["ppstructure_v3"]:
            logger.info("Optional dependency available: paddleocr (with PPStructureV3)")
        else:
            logger.warning(
                "paddleocr is installed but `PPStructureV3` is not available. "
                "Image-structure OCR features will be disabled unless you install a compatible PaddleOCR version."
            )
    except Exception as exc:  # pragma: no cover - defensive logging
        # If import fails unexpectedly (e.g. environment issues), treat as unavailable
        logger.warning("paddleocr import attempted but failed: %s. Image OCR features will be unavailable.", exc)
        result["installed"] = False
        result["ppstructure_v3"] = False

    return result


def check_optional_dependencies() -> Dict[str, Dict[str, bool]]:
    """
    Run lightweight checks for optional dependencies.

    Returns:
        A mapping of dependency name -> metadata dict describing availability.

        Example:
        {
            "paddleocr": {"installed": True, "ppstructure_v3": False},
            ...
        }
    """
    deps: Dict[str, Dict[str, bool]] = {}

    # PaddleOCR (PP-Structure v3)
    deps["paddleocr"] = _check_paddleocr()

    # Log a concise summary for operators
    for name, info in deps.items():
        if info.get("installed"):
            logger.info("Optional dependency present: %s", name)
        else:
            logger.warning("Optional dependency missing: %s — related features will be disabled.", name)

    return deps


def is_paddleocr_available() -> bool:
    """
    Convenience helper: True if paddleocr is installed and PPStructureV3 is available.
    """
    info = _check_paddleocr()
    return info.get("installed", False) and info.get("ppstructure_v3", False)


__all__ = ["check_optional_dependencies", "is_paddleocr_available"]
