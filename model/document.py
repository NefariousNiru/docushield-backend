from pydantic import BaseModel
from uuid import UUID

class DocumentResponse(BaseModel):
    id: UUID
    title: str
    uploaded_by: str
    created_at: int