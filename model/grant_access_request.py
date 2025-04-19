from uuid import UUID
from pydantic import BaseModel


class GrantAccessRequest(BaseModel):
    access_id: UUID
    approve: bool