import time
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, BIGINT
from config.database import Base


class AuthLogsSchema(Base):
    __tablename__ = "auth_logs"

    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True, unique=True, nullable=False)
    failed_attempts = Column(Integer, default=0, nullable=False)
    last_attempt = Column(BIGINT, default=lambda: int(time.time()), nullable=False)
    blocked_until = Column(BIGINT, nullable=True)
