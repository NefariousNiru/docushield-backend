from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from repository.encryption_key_store_repository import EncryptionKeyStoreRepository
from uuid import UUID
import time

from schema.encryption_key_store_schema import EncryptionKeyStoreSchema


class EncryptionKeyStoreRepositoryImpl(EncryptionKeyStoreRepository):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_public_key(self, user_id: UUID, public_key: str, encrypted_private_key: str) -> EncryptionKeyStoreSchema:
        key_store = EncryptionKeyStoreSchema(
            user_id=user_id,
            public_key=public_key,
            encrypted_private_key=encrypted_private_key,
            created_at=int(time.time())
        )
        self.db_session.add(key_store)
        await self.db_session.flush()
        return key_store


    async def get_public_key_by_user_id(self, user_id: UUID) -> str | None:
        query = select(EncryptionKeyStoreSchema.public_key).where(EncryptionKeyStoreSchema.user_id == user_id)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()
