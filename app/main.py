import json
import logging
from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError
from starlette.concurrency import run_in_threadpool

from app.config.settings import settings
from app.database.mongodb import mongo_database
from app.dependencies import metadata_repository
from app.exceptions.handlers import register_exception_handlers
from app.routes.auth_routes import router as auth_router
from app.routes.contract_routes import router as contract_router
from app.routes.metadata_routes import router as metadata_router

logger = logging.getLogger("metadata_catalog")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Prepara o banco na inicializaçao e fecha o cliente no encerramento.
    settings.validate()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        await run_in_threadpool(mongo_database.ping)
        await run_in_threadpool(metadata_repository.create_indexes)
        yield
    finally:
        mongo_database.close()


app = FastAPI(title="Metadata Catalog API", version="1.0.0", lifespan=lifespan)

register_exception_handlers(app)


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = str(uuid4())
    started = perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        json.dumps(
            {
                "event": "request_completed",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round((perf_counter() - started) * 1000, 2),
            }
        ),
    )
    return response


@app.get("/")
def root():
    return {"message": "Metadata Catalog API", "status": "ok"}


@app.get("/health/live")
def liveness():
    # Verifica se a API responde, sem depender do MongoDB.
    return {"status": "ok"}


@app.get("/health")
@app.get("/health/ready")
def health_check():
    # Verifica a conexao com o banco e retorna 503 em caso de falha.
    try:
        mongo_database.ping()
    except PyMongoError:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "degraded", "database": "unavailable"},
        )
    return {"status": "ok", "database": "ok"}


app.include_router(auth_router)
app.include_router(contract_router)
app.include_router(metadata_router)
