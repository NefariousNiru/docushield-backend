from typing import Protocol
from uuid import UUID
from schema.access_request_schema import AccessRequestSchema


class AccessHistoryRepository(Protocol):

    async def get_by_doc_id(self, doc_id: list[UUID]) -> list[AccessRequestSchema]:
        ...

    async def add(self, request: AccessRequestSchema):
        ...

    async def get_pending_requests_by_owner_id(self, owner_id: UUID) -> list[AccessRequestSchema]:
        ...