from typing import Protocol
from uuid import UUID
from util.enums import AuditAction


class AuditLogRepository(Protocol):
    async def add(
            self,
            user_id: UUID,
            action: AuditAction,
            ip_address: str,
            user_agent: str,
            doc_id: UUID | None = None
    ) -> None:
        ...