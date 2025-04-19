from typing import Optional

from pydantic import BaseModel
from uuid import UUID

class DocumentResponse(BaseModel):
    id: str
    title: str
    uploaded_by: str | None
    uploaded_for: str | None
    created_at: int