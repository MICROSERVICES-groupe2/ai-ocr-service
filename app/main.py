from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File
from app.api.routes import ocr, scoring, documents
from app.core.database import connect_to_mongo, close_mongo_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(title="AI OCR Service", lifespan=lifespan)

app.include_router(ocr.router, prefix="/api/ocr", tags=["ocr"])
app.include_router(scoring.router, prefix="/api/scoring", tags=["scoring"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])

@app.get("/health")
def health_check():
    return {"status": "UP"}
