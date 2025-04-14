from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse

from exceptions.public_key_not_found import PublicKeyNotFoundError
from repository.encryption_key_store_repository import EncryptionKeyStoreRepository
from repository.encryption_key_store_repository_impl import EncryptionKeyStoreRepositoryImpl
from util.logger import logger
from fastapi.exceptions import HTTPException


async def get_public_key(user_id: UUID, db_session: AsyncSession) -> JSONResponse:
    try:
        encryption_repo: EncryptionKeyStoreRepository =  EncryptionKeyStoreRepositoryImpl(db_session=db_session)
        public_key: str | None =  await encryption_repo.get_public_key_by_user_id(user_id=user_id)
        if public_key is not None:
            return JSONResponse({"public_key": public_key})
        else:
            raise PublicKeyNotFoundError(f"Public key not found for user: {user_id}")
    except Exception as e:
        logger.error(f"Unable to get Public Key for user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def get_document_info(user_id: UUID, db_session: AsyncSession):
    # fetch by user id all documents
    pass


async def get_document_hash(user_id: UUID, document_id: UUID, db_session: AsyncSession):
    # fetch by user id all documents
    pass