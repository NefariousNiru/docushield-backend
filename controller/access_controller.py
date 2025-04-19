from uuid import UUID
from fastapi import APIRouter, Request
from fastapi.params import Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession
from aop.require_role import require_role
from config.constants.urls import InternalURIs
from config.database import get_db
from model.request_access_payload import RequestAccessPayload
from service import access_service
from util.enums import AccountType

access_controller = APIRouter()

@access_controller.get(InternalURIs.ACCESS_HISTORY_V1)
async def get_access_history(request: Request, db_session: AsyncSession = Depends(get_db)):
    user_id = request.state.user_id
    return await access_service.get_access_history(user_id=user_id, db_session=db_session)


@access_controller.get(InternalURIs.GRANT_ACCESS_V1)
async def get_requested_access(request: Request, db_session: AsyncSession = Depends(get_db)):
    user_id = request.state.user_id
    return await access_service.get_requested_access(user_id=user_id, db_session=db_session)


@access_controller.post(InternalURIs.GRANT_ACCESS_V1)
async def grant_access(request: Request, access_id: UUID, db_session: AsyncSession = Depends(get_db)):
    user_id = request.state.user_id
    return await access_service.grant_access(user_id=user_id, access_id=access_id, db_session=db_session)
    pass



######################################################
# ORGANIZATION ONLY CONTROLLERS
######################################################

@access_controller.post(InternalURIs.REQUEST_ACCESS_V1, dependencies=[Depends(require_role(AccountType.ORGANIZATION))])
async def request_access(request: Request, request_payload: RequestAccessPayload,  db_session: AsyncSession = Depends(get_db)):
    user_id = request.state.user_id
    return await access_service.request_access(user_id=user_id, owner_id=request_payload.owner_id, document_id=request_payload.document_id, db_session=db_session)

