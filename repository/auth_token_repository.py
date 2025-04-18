from typing import Protocol
from uuid import UUID

from schema.auth_token_schema import AuthTokenSchema


class AuthTokenRepository(Protocol):
    async def add(self, user_id: UUID, token: str, created_at: int, expires_at: int):
        ...

    async def find_by_auth_token(self, auth_token: str) -> AuthTokenSchema:
        ...