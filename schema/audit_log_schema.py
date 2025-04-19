from config.database import Base
from sqlalchemy import Column, Enum, ForeignKey, BigInteger, Text, String
from sqlalchemy.dialects.postgresql import UUID
from util.enums import AuditAction


class AuditLogSchema(Base):
    __tablename__ = "audit_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    action = Column(Enum(AuditAction), nullable=False)
    doc_id = Column(String(64), ForeignKey("document.id"), nullable=True)
    timestamp = Column(BigInteger, nullable=False)
    ip_address = Column(String(45), nullable=False)  # supports IPv6
    user_agent = Column(Text, nullable=False)

