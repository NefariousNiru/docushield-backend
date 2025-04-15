import time
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from fastapi import Request

from config.constants.errors import INTERNAL_SERVER_ERROR
from repository.encryption_key_store_repository import EncryptionKeyStoreRepository
from repository.encryption_key_store_repository_impl import EncryptionKeyStoreRepositoryImpl
from schema.auth_token_schema import AuthTokenSchema
from util import utils
from config.constants.keys import Keys
from exceptions.token_creation import TokenCreationError
from model.sign_in_request import SignInRequest
from model.sign_up_request import SignUpRequest
from repository.auth_token_repository import AuthTokenRepository
from repository.auth_token_repository_impl import AuthTokenRepositoryImpl
from repository.user_repository import UserRepository
from repository.user_repository_impl import UserRepositoryImpl
from schema.user_schema import UserSchema
from uuid import uuid4
from passlib.hash import bcrypt
from util.logger import logger
import jwt


async def sign_up(request: SignUpRequest, db_session: AsyncSession) -> JSONResponse | None:
    user = UserSchema(
        id=uuid4(),
        email=request.email,
        name=request.name,
        password=bcrypt.hash(request.password),
        role=request.account_type,
        is_active=True
    )
    try:
        # Add a user
        user_repository: UserRepository = UserRepositoryImpl(db_session=db_session)
        existing_user = await user_repository.find_by_email(request.email)
        if existing_user:
            raise HTTPException(status_code=409, detail="User already exists with this email.")
        await user_repository.add(user=user)

        # Create a token
        token: str = await create_token(user=user, db_session=db_session)

        # Create public/private key pair
        public_key, encrypted_private_key = utils.generate_encryption_key_pair()
        encryption_repository: EncryptionKeyStoreRepository = EncryptionKeyStoreRepositoryImpl(db_session=db_session)
        await encryption_repository.create_public_key(user_id=user.id, public_key=public_key, encrypted_private_key=encrypted_private_key)

        await db_session.commit()

        response = JSONResponse(content={"message": "Success", "role": user.role.value})
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            secure=False,  # HTTPS is used in prod
            samesite="lax",
            max_age=Keys.TOKEN_MAX_AGE
        )
        return response

    except HTTPException as http_exc:
        await db_session.rollback()
        logger.warning(f"Auth failed: {http_exc.detail}")
        raise http_exc

    except Exception as e:
        logger.error(f"Sign up error: {e}")
        await db_session.rollback()
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


async def sign_in(request: SignInRequest, db_session: AsyncSession) -> JSONResponse | None:
    try:
        # Check for user
        user_repository: UserRepository = UserRepositoryImpl(db_session=db_session)
        user: UserSchema = await user_repository.find_by_email(request.email)

        # Check if user is valid
        if not user or not bcrypt.verify(request.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid Credentials")

        # Create a token
        token: str = await create_token(user=user, db_session=db_session)
        await db_session.commit()

        response = JSONResponse(content={"message": "Success", "role": user.role.value})
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            secure=False,  # Make sure HTTPS is used in prod
            samesite="lax",
            max_age=Keys.TOKEN_MAX_AGE
        )
        return response

    except HTTPException as http_exc:
        await db_session.rollback()
        logger.warning(f"Auth failed: {http_exc.detail}")
        raise http_exc

    except Exception as e:
        logger.error(f"Sign in error: {e}")
        await db_session.rollback()
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


async def create_token(user: UserSchema, db_session: AsyncSession) -> str | None:
    try:
        created_at = int(time.time())
        expires_at = created_at + Keys.TOKEN_MAX_AGE
        token = jwt.encode({"user_id": str(user.id), "iat": created_at, "exp": expires_at, "role": user.role.value}, Keys.JWT_SECRET, algorithm='HS256')
        auth_token_repo: AuthTokenRepository = AuthTokenRepositoryImpl(db_session=db_session)
        await auth_token_repo.add(user_id=user.id, token=token, created_at=created_at, expires_at=expires_at)
        return token
    except Exception as e:
        raise TokenCreationError(f"Token creation failed: {str(e)}")


async def check_session(request: Request, db_session: AsyncSession) -> dict:
    jwt_token = request.cookies.get("access_token")
    if not jwt_token:
        return { "valid": False }

    try:
        payload = jwt.decode(jwt_token, Keys.JWT_SECRET, algorithms=["HS256"])
        auth_repo: AuthTokenRepository = AuthTokenRepositoryImpl(db_session=db_session)
        auth_token: AuthTokenSchema = await auth_repo.find_by_auth_token(jwt_token)
        if not auth_token:
            return { "valid": False }
        return { "valid": True, "payload": payload }
    except (jwt.ExpiredSignatureError, jwt.DecodeError):
        return { "valid": False }
