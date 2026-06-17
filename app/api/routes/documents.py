from fastapi import APIRouter, HTTPException
from app.services.storage_service import storage_service
from app.core.database import get_database

router = APIRouter()

@router.get("/{doc_id}/url")
async def get_document_url(doc_id: str):
    db = get_database()
    doc = await db["documents"].find_one({"id": doc_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    try:
        url = storage_service.generate_presigned_url(doc["filename"])
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
