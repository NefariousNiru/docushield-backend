from config.database import Base
from sqlalchemy import Column, Enum, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from util.enums import AccessStatus


class AccessRequestSchema(Base):
    __tablename__ = "access_request"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    requester_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    doc_id = Column(UUID(as_uuid=True), ForeignKey("document.id"), nullable=False)
    status = Column(Enum(AccessStatus), default=AccessStatus.PENDING, nullable=False)
    requested_at = Column(BigInteger, nullable=False)
    approved_at = Column(BigInteger, nullable=True)