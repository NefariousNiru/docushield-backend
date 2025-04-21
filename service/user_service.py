from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from config.constants.errors import INTERNAL_SERVER_ERROR
from exceptions.object_not_found import ObjectNotFoundError
from repository.encryption_key_store_repository import EncryptionKeyStoreRepository
from repository.encryption_key_store_repository_impl import EncryptionKeyStoreRepositoryImpl
from util.logger import logger
from fastapi.exceptions import HTTPException


async def get_public_key(user_id: UUID, db_session: AsyncSession) -> JSONResponse:
    try:
        encryption_repo: EncryptionKeyStoreRepository =  EncryptionKeyStoreRepositoryImpl(db_session=db_session)
        public_key: str | None =  await encryption_repo.get_public_key_by_user_id(user_id=user_id)
        if public_key is not None:
            return JSONResponse({"public_key": public_key, "user_id": user_id})
        else:
            raise ObjectNotFoundError(f"Public key not found for user: {user_id}")
    except Exception as e:
        await db_session.rollback()
        logger.error(f"Unable to get Public Key for user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)