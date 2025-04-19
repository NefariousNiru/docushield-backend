from sqlalchemy.ext.asyncio import AsyncSession
from repository.access_request_repository import AccessHistoryRepository


class AccessHistoryRepositoryImpl(AccessHistoryRepository):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session