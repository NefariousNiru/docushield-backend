from uuid import UUID
from pydantic import BaseModel


class RequestAccessPayload(BaseModel):
    document_id: str
    owner_id: UUID