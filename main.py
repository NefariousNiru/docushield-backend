from util import logger
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from config.database import engine, Base
import routes


@asynccontextmanager
async def lifespan(fastApiApp: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",  # Frontend on local development
        "https://docushield-frontend-production.up.railway.app",
    ],
    allow_credentials=True,  # Allow cookies and other credentials
    allow_methods=["POST", "GET", "OPTIONS"],  # Allowed HTTP Methods
    allow_headers=["Authorization", "Content-Type", "Accept"], # Allowed HTTP Headers
)

routes.register(app)