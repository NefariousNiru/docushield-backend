from uuid import UUID
from fastapi import APIRouter, Request
from fastapi.params import Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession
from aop.audit_log import audit_log
from aop.require_role import require_role
from config.constants.urls import InternalURIs
from config.database import get_db
from model.grant_access_request import GrantAccessRequest
from model.request_access_payload import RequestAccessPayload
from service import access_service, document_service
from util.enums import AccountType, AuditAction

access_controller = APIRouter()

@access_controller.get(InternalURIs.ACCESS_HISTORY_V1)
async def get_access_history(request: Request, db_session: AsyncSession = Depends(get_db)):
    #
    user_id = request.state.user_id
    return await access_service.get_access_history(user_id=user_id, db_session=db_session)


@access_controller.get(InternalURIs.GRANT_ACCESS_V1)
async def get_requested_access(request: Request, db_session: AsyncSession = Depends(get_db)):
    # Individual (GETS) all pending requests
    user_id = request.state.user_id
    return await access_service.get_requested_access(user_id=user_id, db_session=db_session)


@access_controller.post(InternalURIs.GRANT_ACCESS_V1)
@audit_log(AuditAction.MODIFIED_REQUEST)
async def grant_access(request: Request, access_request: GrantAccessRequest, db_session: AsyncSession = Depends(get_db)):
    # Individual approves/declines (POST) a pending request
    user_id = request.state.user_id
    return await access_service.grant_access(user_id=user_id, access_id=access_request.access_id, approve=access_request.approve, db_session=db_session)


######################################################
# ORGANIZATION ONLY CONTROLLERS
######################################################

@access_controller.post(InternalURIs.REQUEST_ACCESS_V1, dependencies=[Depends(require_role(AccountType.ORGANIZATION))])
@audit_log(AuditAction.REQUESTED_DOCUMENT)
async def request_access(request: Request, request_payload: RequestAccessPayload,  db_session: AsyncSession = Depends(get_db)):
    # Organization requests access to a document
    user_id = request.state.user_id
    return await access_service.request_access(user_id=user_id, owner_id=request_payload.owner_id, document_id=request_payload.document_id, db_session=db_session)


@access_controller.get(InternalURIs.REQUEST_STATUS_V1, dependencies=[Depends(require_role(AccountType.ORGANIZATION))])
async def request_access_status(request: Request, db_session: AsyncSession = Depends(get_db)):
    # Organization asks for all its historical requests
    user_id = request.state.user_id
    return await access_service.request_access_status(user_id=user_id, db_session=db_session)


@access_controller.get(InternalURIs.DOWNLOAD_V1, dependencies=[Depends(require_role(AccountType.ORGANIZATION))])
@audit_log(AuditAction.DOWNLOADED_DOCUMENT)
async def download_document(request: Request, access_id: UUID, db_session: AsyncSession = Depends(get_db)):
    # Organization requests to download a document
    user_id = request.state.user_id
    return await document_service.document_download(user_id=user_id, access_id=access_id, db_session=db_session)