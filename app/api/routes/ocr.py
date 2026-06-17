import uuid
import hashlib
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ocr_service import ocr_service
from app.services.parsing_service import ParsingService
from app.services.storage_service import storage_service
from app.core.database import get_database
from app.core.logging import logger

router = APIRouter()

@router.post("/extract")
async def extract_text(file: UploadFile = File(...)):
    logger.info(f"Received file for extraction: {file.filename}")
    try:
        contents = await file.read()
        
        # 1. Extraction (Preprocessing + OCR)
        ocr_result = ocr_service.extract(contents, file.filename)
        
        # 2. Parsing
        parsed_data = ParsingService.parse(ocr_result["text"], ocr_result["confidence"])
        
        # 3. Storage
        doc_id = str(uuid.uuid4())
        unique_filename = f"{doc_id}_{file.filename}"
        
        minio_url = storage_service.upload_file(contents, unique_filename, file.content_type)
        
        # Hash
        sha256_hash = hashlib.sha256(contents).hexdigest()
        
        # MongoDB
        db = get_database()
        doc_record = {
            "id": doc_id,
            "filename": unique_filename,
            "original_filename": file.filename,
            "minio_url": minio_url,
            "content_type": file.content_type,
            "sha256_hash": sha256_hash,
            "statut_ocr": "COMPLETED",
            "ocr_result": parsed_data,
            "date_upload": datetime.utcnow().isoformat() + "Z"
        }
        await db["documents"].insert_one(doc_record)
        
        return {
            "status": "success",
            "document_id": doc_id,
            "parsed_data": parsed_data
        }
    except Exception as e:
        logger.error(f"Error during extraction: {str(e)}")
        raise HTTPException(status_code=500, detail="Error during OCR extraction")
