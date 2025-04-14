import os
from util.enums import Environment


ENVIRONMENT: Environment = Environment.DEV
class Keys:
    JWT_SECRET = os.getenv("JWT_SECRET")
    if not JWT_SECRET:
        raise RuntimeError("'JWT_SECRET' TOKEN not found in Environment.")
    DATABASE_ENV_KEY = 'DOCUSHIELD_DB_URL'
    TOKEN_MAX_AGE = 7 * 24 * 60 * 60