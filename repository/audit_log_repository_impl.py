import time
from sqlalchemy.ext.asyncio import AsyncSession
from schema.audit_log_schema import AuditLogSchema
from repository.audit_log_repository import AuditLogRepository

class AuditLogRepositoryImpl(AuditLogRepository):
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def add(self, log: AuditLogSchema):
        self.db.add(log)
