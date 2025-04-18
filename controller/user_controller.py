from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, Form, Request, Depends, APIRouter
from aop.require_role import require_role
from config.constants.urls import InternalURIs
from config.database import get_db
from model.document import DocumentResponse
from model.document_upload_request import DocumentUploadRequest
from repository.document_repository import DocumentRepository
from repository.document_repository_impl import DocumentRepositoryImpl
from service import user_service, document_service
from util.enums import AccountType

user_controller = APIRouter()

@user_controller.get(InternalURIs.PUBLIC_KEY_V1)
async def get_public_key(request: Request, db_session: AsyncSession = Depends(get_db)):
    user_id = request.state.user_id
    return await user_service.get_public_key(user_id=user_id, db_session=db_session)


@user_controller.get(InternalURIs.DOCUMENT_V1, response_model=list[DocumentResponse])
async def get_document_info(request: Request, db_session: AsyncSession = Depends(get_db)):
    user_id = request.state.user_id
    return await document_service.get_document_info(user_id=user_id, db_session=db_session)


@user_controller.get(InternalURIs.DOCUMENT_DOWNLOAD_V1)
async def get_document(request: Request, document_id: UUID, db_session: AsyncSession = Depends(get_db)):
    user_id = request.state.user_id
    return await document_service.get_document(document_id=document_id, user_id=user_id, db_session=db_session)


@user_controller.get(InternalURIs.DOCUMENT_HASH_V1)
async def get_document_hash(document_id: UUID, request: Request, db_session: AsyncSession = Depends(get_db)):
    user_id = request.state.user_id
    return await document_service.get_document_hash(user_id=user_id, document_id=document_id, db_session=db_session)


######################################################
# ORGANIZATION ONLY CONTROLLERS
######################################################


@user_controller.post(InternalURIs.DOCUMENT_V1, dependencies=[Depends(require_role(AccountType.ORGANIZATION))])
async def add_document(
    request: Request,
    title: str = Form(...),
    owner_id: UUID = Form(...),
    owner_public_key: str = Form(...),
    file: UploadFile = Form(...),
    db_session: AsyncSession = Depends(get_db)
):
    uploader_id = request.state.user_id
    form_data = DocumentUploadRequest(
        title=title,
        owner_id=owner_id,
        owner_public_key=owner_public_key
    )
    return await document_service.add_document(
        form_data=form_data,
        uploader_id=uploader_id,
        file=file,
        db_session=db_session
    )


@user_controller.get(InternalURIs.DOCUMENT_UPLOADS_V1, dependencies=[Depends(require_role(AccountType.ORGANIZATION))])
async def get_document_by_uploader_id(request: Request, db_session: AsyncSession = Depends(get_db)):
    user_id = request.state.user_id
    return await document_service.get_document_by_uploader_id(uploader_id=user_id, db_session=db_session)
