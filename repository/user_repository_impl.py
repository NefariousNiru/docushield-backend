from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from repository.user_repository import UserRepository
from schema.user_schema import UserSchema


class UserRepositoryImpl(UserRepository):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session


    async def add(self, user: UserSchema):
        """
        Add a user to the DB. Auto Commits
        :param user: UserSchema object
        :return: None
        """
        self.db_session.add(user)
        await self.db_session.commit()
        await self.db_session.refresh(user)


    async def find_by_email(self, email: str) -> UserSchema | None:
        """
        Searches for a user with the email
        :param email: User email to search by
        :return: UserSchema object if found or None
        """
        query = select(UserSchema).where(UserSchema.email == email)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()


    async def find_all_name_by_user_id(self, user_ids: list[UUID]) -> dict | None:
        """
        Searches for all names for a list of user_ids
        :param user_ids: A list of uploader ids
        :return: a dictionary mapping of user_ids to their names
        """
        query = select(UserSchema.id, UserSchema.name).where(UserSchema.id.in_(user_ids))
        user_result = await self.db_session.execute(query)
        return {row.id: row.name for row in user_result.fetchall()}


    async def find_by_id(self, user_id: UUID) -> UserSchema | None:
        """
        Searches for a user and returns if the user is present
        :param user_id: User id to search
        :return: user schema object
        """
        query = select(UserSchema).where(UserSchema.id == user_id)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

