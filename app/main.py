from fastapi import FastAPI

from app.api.metadata_routes import router as metadata_router
from app.api.contract_routes import router as contract_router
from app.exceptions.handlers import register_exception_handlers

app = FastAPI(title="Metadata Catalog API", version="1.0.0")

register_exception_handlers(app)


@app.get("/")
def root():

    return {"message": "Metadata Catalog API", "status": "ok"}


app.include_router(metadata_router)
app.include_router(contract_router)