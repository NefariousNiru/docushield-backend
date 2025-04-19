from typing import Protocol
from uuid import UUID
from schema.access_request_schema import AccessRequestSchema


class AccessHistoryRepository(Protocol):

    async def get_by_doc_id(self, doc_id: list[UUID]) -> list[AccessRequestSchema]:
        ...