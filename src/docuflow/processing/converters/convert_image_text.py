from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

import cv2
import numpy as np

os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"

_PIPELINE: Any | None = None


def _resize_image(img: np.ndarray, target_min_width: int = 1600) -> np.ndarray:
    _, width = img.shape[:2]
    if width >= target_min_width:
        return img

    scale = min(target_min_width / max(width, 1), 2.0)
    return cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)


def _normalize_contrast(gray: np.ndarray) -> np.ndarray:
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(gray)


def _cleanup_noise(gray: np.ndarray) -> np.ndarray:
    return cv2.fastNlMeansDenoising(gray, None, 12, 7, 21)


def _add_border(gray: np.ndarray, border_size: int = 24) -> np.ndarray:
    return cv2.copyMakeBorder(
        gray,
        border_size,
        border_size,
        border_size,
        border_size,
        cv2.BORDER_CONSTANT,
        value=255,
    )


def _preprocess_image(image_path: Path) -> np.ndarray:
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Unable to read image: {image_path}")

    img = _resize_image(img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = _normalize_contrast(gray)
    gray = _cleanup_noise(gray)
    gray = _add_border(gray)

    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def _get_pipeline() -> Any:
    global _PIPELINE
    if _PIPELINE is None:
        # Check whether the `paddleocr` package is available before attempting to import it.
        # This avoids triggering heavy import-time side-effects or vague ImportError traces
        # when the package is not installed in the environment.
        import importlib
        import importlib.util

        spec = importlib.util.find_spec("paddleocr")
        if spec is None:
            raise RuntimeError(
                "PaddleOCR is not installed. Install PaddlePaddle and PaddleOCR first, then rerun this script."
            )

        try:
            # Import the package only after confirming it exists.
            paddleocr = importlib.import_module("paddleocr")
            PPStructureV3 = getattr(paddleocr, "PPStructureV3", None)
            if PPStructureV3 is None:
                # Installed paddleocr but missing the expected API/class — provide a clear message.
                raise RuntimeError(
                    "PaddleOCR is installed but `PPStructureV3` is not available. "
                    "Please ensure you have a compatible version of PaddleOCR that provides PPStructureV3."
                )
        except Exception as exc:
            # Normalize and re-raise with a helpful message so callers can decide how to handle it.
            raise RuntimeError(
                f"Failed to import or initialize PaddleOCR: {exc}. "
                "Install/upgrade PaddlePaddle and PaddleOCR and try again."
            ) from exc

        _PIPELINE = PPStructureV3(
            lang="en",
            ocr_version="PP-OCRv5",
            use_doc_orientation_classify=True,
            use_doc_unwarping=True,
            use_textline_orientation=True,
            text_detection_model_name="PP-OCRv5_server_det",
            text_recognition_model_name="PP-OCRv5_server_rec",
            text_det_limit_side_len=1216,
            text_det_limit_type="min",
            device="cpu",
        )

    return _PIPELINE


def _extract_markdown_text(markdown_result: Any) -> str:
    if isinstance(markdown_result, str):
        return markdown_result
    if hasattr(markdown_result, "markdown_texts"):
        return str(markdown_result.markdown_texts)
    if isinstance(markdown_result, dict):
        return str(markdown_result.get("markdown_texts", ""))
    return str(markdown_result)


def convert_image_to_markdown(image_path: Path) -> str:
    image_path = image_path.expanduser().resolve()
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    pipeline = _get_pipeline()
    processed = _preprocess_image(image_path)
    results = pipeline.predict(processed)
    markdown_pages = [result.markdown for result in results]
    markdown_result = pipeline.concatenate_markdown_pages(markdown_pages)
    return _extract_markdown_text(markdown_result)


def save_image_markdown(image_path: Path, output_dir: Path) -> Path:
    image_path = image_path.expanduser().resolve()
    output_dir = output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    markdown_text = convert_image_to_markdown(image_path)
    markdown_path = output_dir / f"{image_path.stem}.md"
    markdown_path.write_text(markdown_text, encoding="utf-8")
    return markdown_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert an image to Markdown using PaddleOCR PP-StructureV3.")
    parser.add_argument("image", type=Path, help="Path to the image file")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output/ppstructure"),
        help="Directory where Markdown will be saved",
    )
    args = parser.parse_args()

    print(save_image_markdown(args.image, args.output_dir))


if __name__ == "__main__":
    main()
