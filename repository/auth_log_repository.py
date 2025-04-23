from uuid import UUID
from schema.auth_logs_schema import AuthLogsSchema
from typing import Protocol

class AuthLogsRepository(Protocol):
    async def get(self, user_id: UUID) -> AuthLogsSchema | None:
        ...


    async def create(self, user_id: UUID) -> AuthLogsSchema:
        ...


    async def upsert(self, log: AuthLogsSchema) -> None:
        ...
