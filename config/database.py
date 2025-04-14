import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config.constants.errors import INVALID_DATABASE_URL
from config.constants.keys import Keys

DATABASE_URL = os.getenv(Keys.DATABASE_ENV_KEY)

if not DATABASE_URL:
    raise RuntimeError(INVALID_DATABASE_URL)

engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()