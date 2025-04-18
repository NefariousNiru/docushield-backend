from sqlalchemy import Column, ForeignKey, String, Text, BigInteger
from sqlalchemy.dialects.postgresql import UUID, BYTEA
from config.database import Base


class DocumentSchema(Base):
    __tablename__ = "document"

    id = Column(UUID(as_uuid=True), primary_key=True)
    uploader_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)

    encrypted_data = Column(BYTEA, nullable=False)
    hash = Column(String(64), unique=True, nullable=False)
    created_at = Column(BigInteger, nullable=False)
    title = Column(Text, nullable=False)
