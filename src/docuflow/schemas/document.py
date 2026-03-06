from typing import Dict

from pydantic import BaseModel, Field


class Document(BaseModel):
    """
    A single document or chunk to store in chroma

    """

    page_content: str = Field(..., description="The text content of the document or chunk")

    metadata: Dict[str, str | int | float | bool] = Field(
        default_factory=dict,
        description="Optional metadata about the document (source, page number, etc.)",
    )
