from typing import Protocol
from uuid import UUID
from schema.encryption_key_store_schema import EncryptionKeyStoreSchema


class EncryptionKeyStoreRepository(Protocol):
    async def create_public_key(self, user_id: UUID, public_key: str, encrypted_private_key: str) -> EncryptionKeyStoreSchema:
        ...

    async def get_public_key_by_user_id(self, user_id: UUID) -> str | None:
        ...

    async def get_private_key_by_user_id(self, user_id: UUID) -> str | None:
        ...