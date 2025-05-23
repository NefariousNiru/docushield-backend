from fastapi import APIRouter, Request
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.constants.urls import InternalURIs
from auth import auth_service
from config.database import get_db
from model.auth_response import AuthResponse
from model.sign_in_request import SignInRequest
from model.sign_up_request import SignUpRequest

auth_controller = APIRouter()

# Sign in existing user
@auth_controller.post(InternalURIs.SIGN_IN_V1, response_model=AuthResponse)
async def sign_in(request: Request, sign_in_request: SignInRequest, db_session: AsyncSession = Depends(get_db)):
    return await auth_service.sign_in(request=request, sign_in_request=sign_in_request, db_session=db_session)


# Sign up a new user
@auth_controller.post(InternalURIs.SIGN_UP_V1, response_model=AuthResponse)
async def sign_up(request: Request, sign_up_request: SignUpRequest, db_session: AsyncSession = Depends(get_db)):
    return await auth_service.sign_up(request=request, sign_up_request=sign_up_request, db_session=db_session)


