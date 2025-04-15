from typing import Protocol
from uuid import UUID
from typing import List
from schema.document_schema import DocumentSchema

class DocumentRepository(Protocol):
    async def get_by_owner_id(self, owner_id: UUID) -> List[DocumentSchema]:
        ...

    async def get_by_id(self, document_id: UUID) -> DocumentSchema | None:
        ...

    async def add(self, document: DocumentSchema):
        ...