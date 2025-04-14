from fastapi import APIRouter, Request
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.constants.urls import InternalURIs
from config.database import get_db
from service import user_service

user_controller = APIRouter()

@user_controller.get(InternalURIs.PUBLIC_KEY_V1)
async def get_public_key(request: Request, db_session: AsyncSession = Depends(get_db)):
    user_id = request.state.user_id
    return await user_service.get_public_key(user_id=user_id, db_session=db_session)


@user_controller.get(InternalURIs.DOCUMENT_INFO_V1)
async def get_document_info(request: Request, db_session: AsyncSession = Depends(get_db)):
    user_id = request.state.user_id
    return await user_service.get_document_info(user_id=user_id, db_session=db_session)


@user_controller.get(InternalURIs.DOCUMENT_HASH_V1)
async def get_document_info(document_id: str, db_session: AsyncSession = Depends(get_db)):
    return await user_service.get_document_hash(user_id="", document_id="", db_session=db_session)



