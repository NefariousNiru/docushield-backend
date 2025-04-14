import time
from sqlalchemy import Column, ForeignKey, String, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from config.database import Base


class EncryptionKeyStoreSchema(Base):
    __tablename__ = "encryption_key_store"

    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True, unique=True, nullable=False)
    public_key = Column(String, nullable=False)
    encrypted_private_key = Column(String, nullable=False)
    created_at = Column(BigInteger, nullable=False, default=lambda: int(time.time()))
