from uuid import UUID
from pydantic import BaseModel


class PendingAccessResponse(BaseModel):
    request_id: UUID
    document_title: str
    requester_name: str
    issuer_name: str
    requested_at: int
