from .base_loader import BaseLoader


class ImageLoader(BaseLoader):
    """Load images: PNG, JPG, GIF, WEBP"""

    SUPPORTED_EXTENSIONS = [".png", ".jpg", ".jpeg", ".gif", ".webp"]
