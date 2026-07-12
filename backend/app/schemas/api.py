from typing import List, Optional
from pydantic import BaseModel
from app.schemas.planner import PlanTrace

class ChatRequest(BaseModel):
    message: str
    file_urls: Optional[List[str]] = None
    # For file uploads, we'll use Form data in FastAPI's UploadFile instead of JSON.

class ChatResponse(BaseModel):
    response: str
    trace: PlanTrace
