import time
import secrets
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from app.core.config import settings
from app.db.session import init_db
from app.api.router import api_router

logger.add(
    "logs/backend_{time:YYYY-MM-DD}.log", rotation="1 day", retention="7 days", level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} - {message}"
)
logger.add(
    lambda msg: print(msg, end=""), level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{message}</cyan>",
    colorize=True
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup: Initializing database...")
    try:
        init_db()
    except Exception as e:
        logger.critical(f"Database initialization failed: {e}. Application cannot start.")
        raise SystemExit(f"Database initialization failed: {e}") from e
    yield
    logger.info("Application shutdown.")

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="API for Zero Knowledge Proof authentication",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    log_id = secrets.token_hex(4)
    logger.info(f"RID {log_id} --> {request.method} {request.url.path} from {request.client.host if request.client else 'unknown'}")
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        logger.info(f"RID {log_id} <-- {request.method} {request.url.path} - Status: {response.status_code} ({process_time:.2f}ms)")
        return response
    except Exception as e:
        logger.error(f"RID {log_id} !!! {request.method} {request.url.path} - Unhandled Error: {e}")
        raise

app.include_router(api_router, prefix=settings.API_PREFIX)

@app.get("/", include_in_schema=False)
async def root():
    return {"message": f"{settings.APP_NAME} is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)