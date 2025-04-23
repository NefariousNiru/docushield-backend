import time
from sqlalchemy.ext.asyncio import AsyncSession
from schema.audit_log_schema import AuditLogSchema
from repository.audit_log_repository import AuditLogRepository

class AuditLogRepositoryImpl(AuditLogRepository):
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def add(
        self,
        user_id,
        action,
        ip_address,
        user_agent,
        doc_id=None
    ):
        log = AuditLogSchema(
            user_id    = user_id,
            action     = action,
            doc_id     = doc_id,
            timestamp  = int(time.time()),
            ip_address = ip_address,
            user_agent = user_agent
        )
        self.db.add(log)
