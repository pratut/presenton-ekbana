from typing import List, Optional
from datetime import datetime
import uuid

from pydantic import BaseModel

from models.sql.slide import SlideModel
from models.usage_cost import UsageCostSummary


class PresentationWithSlides(BaseModel):
    id: uuid.UUID
    content: str
    n_slides: int
    language: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    tone: Optional[str] = None
    verbosity: Optional[str] = None
    theme: Optional[dict] = None
    usage_cost: Optional[UsageCostSummary] = None
    slides: List[SlideModel]
