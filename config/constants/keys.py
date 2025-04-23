import os
from util.enums import Environment


ENVIRONMENT: Environment = Environment.PROD if os.getenv("ENV") == Environment.PROD.value else Environment.DEV
class Keys:
    JWT_SECRET = os.getenv("JWT_SECRET")
    RSA_PAIR_SECRET = JWT_SECRET
    if not JWT_SECRET:
        raise RuntimeError("'JWT_SECRET' TOKEN not found in Environment.")
    DATABASE_ENV_KEY = 'DOCUSHIELD_DB_URL'
    TOKEN_MAX_AGE = 7 * 24 * 60 * 60
    SIGNATURE_SEPARATOR = b'|||DOCUSHIELD_SIG|||'
    AES_RSA_SEPARATOR = b'|||DOCUSHIELD_HYBRID|||'
    MAX_RETRIES = 3
    BLOCK_DURATION_POST_MAX_RETRIES = 24 * 60 * 60
