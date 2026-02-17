import base64
import hashlib


def generate_chunk_id(content: str) -> str:
    digest = hashlib.sha1(content.encode()).digest()
    return base64.urlsafe_b64encode(digest)[:8].decode()
