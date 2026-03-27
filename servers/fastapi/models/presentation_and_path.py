from pydantic import BaseModel
import uuid

from models.usage_cost import UsageCostSummary


class PresentationAndPath(BaseModel):
    presentation_id: uuid.UUID
    path: str
    usage_cost: UsageCostSummary | None = None


class PresentationPathAndEditPath(PresentationAndPath):
    edit_path: str
