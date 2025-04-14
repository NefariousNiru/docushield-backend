from fastapi import FastAPI, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from controller.auth_controller import auth_controller
from config.database import get_db
from auth.auth_bearer import JWTBearer
from controller.user_controller import user_controller


async def get_auth_dependency(request: Request, session: AsyncSession = Depends(get_db)) -> None:
    jwt_bearer = JWTBearer(db_session=session)
    await jwt_bearer(request)


def register(app: FastAPI):
    # Unprotected routes
    app.include_router(auth_controller)

    # Protected Routes
    app.include_router(user_controller, dependencies=[Depends(get_auth_dependency)])