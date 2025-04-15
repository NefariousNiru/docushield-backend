from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID
from schema.document_schema import DocumentSchema
from repository.document_repository import DocumentRepository

class DocumentRepositoryImpl(DocumentRepository):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_by_owner_id(self, owner_id: UUID) -> List[DocumentSchema] | None:
        query = select(DocumentSchema).where(DocumentSchema.owner_id == owner_id).order_by(DocumentSchema.created_at.desc())
        result = await self.db_session.execute(query)
        return result.scalars().all()


    async def get_by_id(self, document_id: UUID) -> DocumentSchema | None:
        query = select(DocumentSchema).where(DocumentSchema.id == document_id)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()


    async def add(self, document: DocumentSchema):
        self.db_session.add(document)
        await self.db_session.commit()
        await self.db_session.refresh(document)

