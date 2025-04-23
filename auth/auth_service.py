import time
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from fastapi import Request
from config.constants.errors import INTERNAL_SERVER_ERROR
from repository.audit_log_repository import AuditLogRepository
from repository.audit_log_repository_impl import AuditLogRepositoryImpl
from repository.auth_log_repository import AuthLogsRepository
from repository.auth_log_repository_impl import AuthLogsRepositoryImpl
from repository.encryption_key_store_repository import EncryptionKeyStoreRepository
from repository.encryption_key_store_repository_impl import EncryptionKeyStoreRepositoryImpl
from schema.auth_logs_schema import AuthLogsSchema
from schema.auth_token_schema import AuthTokenSchema
from util import utils
from config.constants.keys import Keys, ENVIRONMENT
from exceptions.token_creation import TokenCreationError
from model.sign_in_request import SignInRequest
from model.sign_up_request import SignUpRequest
from repository.auth_token_repository import AuthTokenRepository
from repository.auth_token_repository_impl import AuthTokenRepositoryImpl
from repository.user_repository import UserRepository
from repository.user_repository_impl import UserRepositoryImpl
from schema.user_schema import UserSchema
from uuid import uuid4, UUID
from passlib.hash import bcrypt
from util.enums import Environment, AuditAction
from util.logger import logger
import jwt


async def sign_up(request: Request, sign_up_request: SignUpRequest, db_session: AsyncSession) -> JSONResponse | None:
    user = UserSchema(
        id=uuid4(),
        email=sign_up_request.email,
        name=sign_up_request.name,
        password=bcrypt.hash(sign_up_request.password),
        role=sign_up_request.account_type,
        is_active=True
    )
    try:
        # Add a user
        user_repository: UserRepository = UserRepositoryImpl(db_session=db_session)
        existing_user = await user_repository.find_by_email(sign_up_request.email)
        if existing_user:
            raise HTTPException(status_code=409, detail="User already exists with this email.")
        await user_repository.add(user=user)

        # Create a token
        token: str = await create_token(user=user, db_session=db_session)

        # Create public/private key pair
        public_key, encrypted_private_key = utils.generate_encryption_key_pair()
        encryption_repository: EncryptionKeyStoreRepository = EncryptionKeyStoreRepositoryImpl(db_session=db_session)
        await encryption_repository.create_public_key(user_id=user.id, public_key=public_key, encrypted_private_key=encrypted_private_key)

        # Audit Log Auth
        await audit_auth(user_id=user.id, audit_action=AuditAction.SIGNUP, request=request, db_session=db_session)

        await db_session.commit()

        return get_response(token=token, user=user)

    except HTTPException as http_exc:
        await db_session.rollback()
        logger.warning(f"Auth failed: {http_exc.detail}")
        raise http_exc

    except Exception as e:
        logger.error(f"Sign up error: {e}")
        await db_session.rollback()
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


async def sign_in(request: Request, sign_in_request: SignInRequest, db_session: AsyncSession) -> JSONResponse | None:
    try:
        # Check for user
        user_repository: UserRepository = UserRepositoryImpl(db_session=db_session)
        user: UserSchema = await user_repository.find_by_email(sign_in_request.email)

        # Check if user is valid
        if not user:
            raise HTTPException(status_code=401, detail="Invalid Credentials")

        # Create/Fetch Auth Log
        valid = bcrypt.verify(sign_in_request.password, user.password)
        await process_sign_in_attempt(user_id=user.id, password_valid=valid, db_session=db_session)

        # Audit Log Auth
        await audit_auth(user_id=user.id, audit_action=AuditAction.SIGNIN, request=request, db_session=db_session)

        # Create a token
        token: str = await create_token(user=user, db_session=db_session)
        await db_session.commit()

        return get_response(token=token, user=user)

    except HTTPException as http_exc:
        await db_session.rollback()
        logger.warning(f"Auth failed: {http_exc.detail}")
        raise http_exc

    except Exception as e:
        logger.error(f"Sign in error: {e}")
        await db_session.rollback()
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


def get_response(token: str, user: UserSchema) -> JSONResponse:
    response = JSONResponse(content={"message": "Success", "role": user.role.value})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True if ENVIRONMENT == Environment.PROD else False,
        samesite="lax",
        max_age=Keys.TOKEN_MAX_AGE
    )
    return response


async def create_token(user: UserSchema, db_session: AsyncSession) -> str | None:
    try:
        created_at = int(time.time())
        expires_at = created_at + Keys.TOKEN_MAX_AGE
        token = jwt.encode({"user_id": str(user.id), "iat": created_at, "exp": expires_at, "role": user.role.value}, Keys.JWT_SECRET, algorithm='HS256')
        auth_token_repo: AuthTokenRepository = AuthTokenRepositoryImpl(db_session=db_session)
        await auth_token_repo.add(user_id=user.id, token=token, created_at=created_at, expires_at=expires_at)
        return token
    except Exception as e:
        await db_session.rollback()
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
        await db_session.rollback()
        return { "valid": False }


async def process_sign_in_attempt(user_id: UUID, password_valid: bool, db_session: AsyncSession):
    """
        Fetch or create an AuthLogs entry for user_id,
        enforce blocked_until, then bump or reset counters.
        Raises HTTPException(403) if still blocked,
        or HTTPException(401) if password_invalid.
        """
    repo: AuthLogsRepository = AuthLogsRepositoryImpl(db_session)
    log: AuthLogsSchema = await repo.get(user_id) or await repo.create(user_id)
    now = int(time.time())

    if log.blocked_until and now < log.blocked_until:
        raise HTTPException(
            status_code=403,
            detail=f"Too many attempts. Try again after {time.ctime(log.blocked_until)}"
        )

    if not password_valid:
        log.failed_attempts += 1
        log.last_attempt = now
        if log.failed_attempts >= Keys.MAX_RETRIES:
            log.blocked_until = now + Keys.BLOCK_DURATION_POST_MAX_RETRIES
        await repo.upsert(log)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    log.failed_attempts = 0
    log.blocked_until = None
    log.last_attempt = now
    await repo.upsert(log)


async def logout(request: Request, db_session: AsyncSession):
    try:
        token = request.cookies.get("access_token")
        token_repo: AuthTokenRepository = AuthTokenRepositoryImpl(db_session=db_session)
        await token_repo.delete(token=token)

        resp = JSONResponse({"message": "Logged out"})
        resp.delete_cookie(
            key="access_token",
            httponly=True,
            secure=True if ENVIRONMENT == Environment.PROD else False,
            samesite="lax"
        )
        await db_session.commit()
        return resp
    except Exception as e:
        await db_session.rollback()
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


async def audit_auth(user_id: UUID, audit_action: AuditAction, request: Request, db_session: AsyncSession):
    try:
        audit_repo: AuditLogRepository = AuditLogRepositoryImpl(db_session=db_session)
        await audit_repo.add(
            user_id=user_id,
            action=audit_action,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            doc_id=None
        )
    except Exception as e:
        raise e

