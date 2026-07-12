from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from app.schemas.api import ChatRequest, ChatResponse
from app.agents.planner import Planner
from app.agents.executor import Executor
from app.agents.tool_registry import registry
from app.utils.logging import logger

router = APIRouter(prefix="/chat", tags=["Chat"])

def get_planner():
    return Planner(tools_metadata=registry.get_all_metadata())

def get_executor():
    return Executor()

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest, 
    planner: Planner = Depends(get_planner),
    executor: Executor = Depends(get_executor)
):
    try:
        # In a real app, file URLs might be validated or fetched from an S3 bucket
        available_files = [{"url": url} for url in (request.file_urls or [])]
        
        logger.info(f"Received chat request: {request.message[:50]}...")
        
        # 1. Plan
        plan = await planner.plan(user_message=request.message, available_files=available_files)
        
        # 2. Execute
        initial_context = {
            "user_query": request.message
        }
        
        # Inject file_urls into context so tools can dynamically select their supported extensions
        if request.file_urls:
             initial_context["file_urls"] = request.file_urls
             # Keep single file_path fallback just in case
             initial_context["file_path"] = request.file_urls[0]
             
        trace = await executor.execute_plan(plan=plan, initial_context=initial_context)
        
        return ChatResponse(
            response=trace.final_response or "No response generated.",
            trace=trace
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
