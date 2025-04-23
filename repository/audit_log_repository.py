from typing import Protocol
from uuid import UUID

from schema.audit_log_schema import AuditLogSchema
from util.enums import AuditAction


class AuditLogRepository(Protocol):
    async def add(self, log: AuditLogSchema) -> None:
        ...