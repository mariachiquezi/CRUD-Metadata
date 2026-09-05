from fastapi import FastAPI

from app.routes.metadata_routes import router as metadata_router, service as metadata_service
from app.routes.contract_routes import router as contract_router
from app.routes.auth_routes import router as auth_router
from app.exceptions.handlers import register_exception_handlers

app = FastAPI(title="Metadata Catalog API", version="1.0.0")

register_exception_handlers(app)


@app.on_event("startup")
def initialize_database():
    metadata_service.repository.create_indexes()


@app.get("/")
def root():

    return {"message": "Metadata Catalog API", "status": "ok"}


@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(auth_router)
app.include_router(contract_router)
app.include_router(metadata_router)

