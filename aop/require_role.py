from fastapi import Depends, HTTPException, Request, status
from config.constants.errors import ACCESS_DENIED_INVALID_ROLE
from util.enums import AccountType


def require_role(expected_role: AccountType):
    async def verify_role(request: Request):
        payload = request.state.payload
        role = payload.get("role")
        if role != expected_role.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ACCESS_DENIED_INVALID_ROLE
            )
    return verify_role
