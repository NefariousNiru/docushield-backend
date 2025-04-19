from typing import Optional
from pydantic import BaseModel


class AccessHistoryResponse(BaseModel):
    document_title: str
    organization_name: str
    status: str
    requested_at: int
    approved_at: Optional[int] = None
