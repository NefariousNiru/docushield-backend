from fastapi import APIRouter, Request
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.constants.urls import InternalURIs
from config.database import get_db
from service import access_service

access_controller = APIRouter()

@access_controller.get(InternalURIs.ACCESS_HISTORY_V1)
async def get_access_history(request: Request, db_session: AsyncSession = Depends(get_db)):
    user_id = request.state.user_id
    return await access_service.get_access_history(user_id=user_id, db_session=db_session)


