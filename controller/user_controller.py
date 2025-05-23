from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, Form, Request, Depends, APIRouter

from aop.audit_log import audit_log
from aop.require_role import require_role
from auth import auth_service
from config.constants.urls import InternalURIs
from config.database import get_db
from model.document_response import DocumentResponse
from model.document_upload_request import DocumentUploadRequest
from repository.document_repository import DocumentRepository
from repository.document_repository_impl import DocumentRepositoryImpl
from service import user_service, document_service
from util.enums import AccountType, AuditAction

user_controller = APIRouter()


@user_controller.get(InternalURIs.ME_V1)
async def who_am_i(request: Request):
    return {"user_id": request.state.user_id, "role": request.state.role}


@user_controller.post(InternalURIs.LOGOUT_V1)
@audit_log(AuditAction.LOGOUT)
async def logout(request: Request, db_session: AsyncSession = Depends(get_db)):
    return await auth_service.logout(request=request, db_session=db_session)


@user_controller.get(InternalURIs.PUBLIC_KEY_V1)
async def get_public_key(request: Request, db_session: AsyncSession = Depends(get_db)):
    # User gets their public key
    user_id = request.state.user_id
    return await user_service.get_public_key(user_id=user_id, db_session=db_session)


@user_controller.get(InternalURIs.DOCUMENT_V1, response_model=list[DocumentResponse])
async def get_document_info(request: Request, db_session: AsyncSession = Depends(get_db)):
    # Get document info
    user_id = request.state.user_id
    return await document_service.get_document_info(user_id=user_id, db_session=db_session)


@user_controller.get(InternalURIs.DOCUMENT_DOWNLOAD_V1)
async def get_document(request: Request, document_id: str, db_session: AsyncSession = Depends(get_db)):
    # TODO: Individual can also download files. Not plugged in yet.
    user_id = request.state.user_id
    return await document_service.get_document(document_id=document_id, user_id=user_id, db_session=db_session)


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
    # Organization adds a document
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
    # Organization gets their own uploaded files.
    user_id = request.state.user_id
    return await document_service.get_document_by_uploader_id(uploader_id=user_id, db_session=db_session)
