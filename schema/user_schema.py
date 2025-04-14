from config.database import Base
from sqlalchemy import Column, String, Enum, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from util.enums import AccountType

class UserSchema(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)  # hashed
    role = Column(Enum(AccountType), nullable=False)
    is_active = Column(Boolean, nullable=False)