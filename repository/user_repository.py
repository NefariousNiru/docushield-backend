from typing import Protocol
from uuid import UUID

from schema.user_schema import UserSchema


class UserRepository(Protocol):
    async def add(self, user: UserSchema):
        ...


    async def find_by_email(self, email: str) -> UserSchema | None:
        ...


    async def find_all_name_by_user_id(self, user_ids: list[UUID]) -> dict | None:
        ...

    async def find_by_id(self, owner_id) -> UserSchema | None:
        ...