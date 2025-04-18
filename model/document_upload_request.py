from pydantic import BaseModel
from uuid import UUID

class DocumentUploadRequest(BaseModel):
    title: str
    owner_id: UUID
    owner_public_key: str
