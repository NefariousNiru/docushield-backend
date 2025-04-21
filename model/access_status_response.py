from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class AccessStatusDetails(BaseModel):
    access_id: UUID
    document_title: str
    owner_name: str
    requested_at: int
    approved_at: Optional[int] = None
    status: str


class AccessStatusResponse(BaseModel):
    pending: list[AccessStatusDetails]
    approved: list[AccessStatusDetails]
    declined: list[AccessStatusDetails]
    completed: list[AccessStatusDetails]