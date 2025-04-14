from pydantic import BaseModel

from util.enums import AccountType


class AuthResponse(BaseModel):
    message: str
    role: AccountType