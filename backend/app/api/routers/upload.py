from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
import uuid
import shutil
from app.utils.logging import logger

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def upload_files(files: List[UploadFile] = File(...)):
    uploaded_urls = []
    
    for file in files:
        try:
            # Generate unique filename to prevent collisions
            ext = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{ext}"
            file_path = os.path.join(UPLOAD_DIR, unique_filename)
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                
            # For local execution, the absolute path acts as the URL/identifier
            uploaded_urls.append(os.path.abspath(file_path))
            
        except Exception as e:
            logger.error(f"Error uploading file {file.filename}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to upload {file.filename}")
            
    return {"urls": uploaded_urls}
