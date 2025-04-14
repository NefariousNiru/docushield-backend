from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from repository.auth_token_repository import AuthTokenRepository
from schema.auth_token_schema import AuthTokenSchema


class AuthTokenRepositoryImpl(AuthTokenRepository):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def add_token(self, user_id: UUID, token: str, created_at: int, expires_at: int):
        auth_token = AuthTokenSchema(
            user_id=user_id,
            token=token,
            created_at=created_at,
            expires_at=expires_at
        )
        self.db_session.add(auth_token)


    async def find_by_auth_token(self, auth_token: str) -> AuthTokenSchema | None:
        query = select(AuthTokenSchema).where(AuthTokenSchema.token == auth_token)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()
