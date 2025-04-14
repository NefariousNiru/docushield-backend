from sqlalchemy import Column, ForeignKey, String, BigInteger, Integer
from sqlalchemy.dialects.postgresql import UUID
from config.database import Base


class AuthTokenSchema(Base):
    __tablename__ = "auth_token"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    token = Column(String, nullable=False)
    created_at = Column(BigInteger, nullable=False)
    expires_at = Column(BigInteger, nullable=False)
