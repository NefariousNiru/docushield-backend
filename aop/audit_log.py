import time
from functools import wraps
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from repository.audit_log_repository import AuditLogRepository
from repository.audit_log_repository_impl import AuditLogRepositoryImpl
from schema.audit_log_schema import AuditAction, AuditLogSchema


def audit_log(action: AuditAction, doc_id_arg: str | None = None):
    """
    Decorator for FastAPI endpoint or service function.
    :param action:      which AuditAction to record
    :param doc_id_arg:  name of the kwarg that holds the document UUID (optional)
    """
    def decorator(fn):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            # find Request & DB session in args/kwargs
            request: Request               = kwargs.get("request") \
                or next((a for a in args if isinstance(a, Request)), None)
            db_session: AsyncSession       = kwargs.get("db_session") \
                or next((a for a in args if hasattr(a, "execute")), None)
            if not request or not db_session:
                # missing dependencies: just run original
                return await fn(*args, **kwargs)

            # call the real handler
            result = await fn(*args, **kwargs)

            # extract doc_id if provided
            doc_id = None
            if doc_id_arg and doc_id_arg in kwargs:
                doc_id = kwargs[doc_id_arg]

            # build repository & log
            repo: AuditLogRepository = AuditLogRepositoryImpl(db_session)
            audit_log_obj: AuditLogSchema = AuditLogSchema(
                user_id    = request.state.user_id,
                doc_id     = doc_id,
                action     = action,
                timestamp  = int(time.time()),
                ip_address = request.client.host,
                user_agent = request.headers.get("user-agent", "")
            )
            await repo.add(audit_log_obj)
            await db_session.commit()
            await db_session.refresh(audit_log_obj)
            return result
        return wrapper
    return decorator