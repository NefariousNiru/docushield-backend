from uuid import UUID
import time
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from repository.auth_log_repository import AuthLogsRepository
from schema.auth_logs_schema import AuthLogsSchema

class AuthLogsRepositoryImpl(AuthLogsRepository):
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get(self, user_id: UUID) -> AuthLogsSchema | None:
        q = select(AuthLogsSchema).where(AuthLogsSchema.user_id == user_id)
        r = await self.db.execute(q)
        return r.scalar_one_or_none()

    async def create(self, user_id: UUID) -> AuthLogsSchema:
        now = int(time.time())
        log = AuthLogsSchema(user_id=user_id, failed_attempts=0, last_attempt=now)
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def upsert(self, log: AuthLogsSchema) -> None:
        # Because `log` is already attached to session, just commit
        await self.db.commit()
