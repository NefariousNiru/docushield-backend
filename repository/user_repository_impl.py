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


