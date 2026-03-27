from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class UsageCostItem(BaseModel):
    service: Literal["llm", "image"]
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    images_generated: int = 0
    unit_price_input_per_1k: float = 0.0
    unit_price_output_per_1k: float = 0.0
    unit_price_per_image: float = 0.0
    currency: str = "USD"
    amount: float = 0.0
    metadata: Optional[Dict[str, Any]] = None


class UsageCostSummary(BaseModel):
    currency: str = "USD"
    total_amount: float = 0.0
    llm_amount: float = 0.0
    image_amount: float = 0.0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_tokens: int = 0
    total_images_generated: int = 0
    items: List[UsageCostItem] = Field(default_factory=list)
