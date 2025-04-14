from typing import Protocol
from schema.user_schema import UserSchema


class UserRepository(Protocol):
    async def add(self, user: UserSchema):
        ...


    async def find_by_email(self, email: str):
        ...