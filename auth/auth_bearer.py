from uuid import UUID

import jwt
from fastapi.security import HTTPBearer
from fastapi import Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from auth import auth_service
from config.constants.errors import ACCESS_DENIED_INVALID_TOKEN
from config.constants.keys import Keys


class JWTBearer(HTTPBearer):
    def __init__(self, db_session: AsyncSession):
        super().__init__()
        self.db_session = db_session

    async def __call__(self, request: Request) -> str:
        jwt_token = request.cookies.get("access_token")
        if not jwt_token:
            raise HTTPException(status_code=403, detail=ACCESS_DENIED_INVALID_TOKEN)

        session_validity = await auth_service.check_session(request=request, db_session=self.db_session)
        if not session_validity["valid"]:
            raise HTTPException(status_code=403, detail=ACCESS_DENIED_INVALID_TOKEN)

        payload = jwt.decode(jwt_token, Keys.JWT_SECRET, algorithms=["HS256"])
        request.state.user_id = session_validity["payload"]["user_id"]
        request.state.role = session_validity["payload"]["role"]
        request.state.payload = payload
        return jwt_token
