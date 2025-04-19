from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from repository.access_request_repository import AccessHistoryRepository
from schema.access_request_schema import AccessRequestSchema
from util.enums import AccessStatus


class AccessHistoryRepositoryImpl(AccessHistoryRepository):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session


    async def get_by_doc_id(self, doc_id: list[UUID]) -> list[AccessRequestSchema]:
        query = select(AccessRequestSchema).where(AccessRequestSchema.doc_id.in_(doc_id))
        result = await self.db_session.execute(query)
        return result.scalars().all()


    async def add(self, request: AccessRequestSchema):
        self.db_session.add(request)
        await self.db_session.commit()
        await self.db_session.refresh(request)


    async def get_pending_requests_by_owner_id(self, owner_id: UUID):
        query = select(AccessRequestSchema).where(
            (AccessRequestSchema.owner_id == owner_id) &
            (AccessRequestSchema.status == AccessStatus.PENDING)
        )
        result = await self.db_session.execute(query)
        return result.scalars().all()


    async def get_by_id(self, access_id: UUID) -> AccessRequestSchema:
        query = select(AccessRequestSchema).where(AccessRequestSchema.id == access_id)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()


    async def get_by_requester_id(self, user_id: UUID) -> list[AccessRequestSchema]:
        query = select(AccessRequestSchema).where(AccessRequestSchema.requester_id == user_id)
        result = await self.db_session.execute(query)
        return result.scalars().all()