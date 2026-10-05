import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.config import settings
from app.database import engine, init_db
from app.routers import issues

logging.basicConfig(
    level=logging.INFO,
    format=f"%(asctime)s [{settings.SERVICE_NAME}] %(levelname)s %(message)s",
)
log = logging.getLogger(settings.SERVICE_NAME)
logging.getLogger("httpx").setLevel(logging.WARNING)  


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    log.info("Utility service started")
    yield
    await engine.dispose()


app = FastAPI(title="Utility Service", lifespan=lifespan, root_path=settings.ROOT_PATH)

app.include_router(issues.router)


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    log.warning("Integrity error on %s %s: %s", request.method, request.url.path, exc.orig)
    return JSONResponse(status_code=409, content={"detail": "Data conflict"})


@app.exception_handler(DBAPIError)
async def db_error_handler(request: Request, exc: DBAPIError):
    log.error("Database error on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(status_code=503, content={"detail": "Database error"})


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    log.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "service": settings.SERVICE_NAME}
