from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class AccessHistoryResponse(BaseModel):
    access_id: UUID
    document_title: str
    organization_name: str
    status: str
    requested_at: int
    approved_at: Optional[int] = None
