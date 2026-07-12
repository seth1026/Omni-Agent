from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from app.schemas.common import InputType

class ToolParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True

class ToolMetadata(BaseModel):
    name: str
    description: str
    supported_inputs: List[InputType]
    required_parameters: List[ToolParameter]
    estimated_latency_sec: int = 1

class ToolExecutionResult(BaseModel):
    tool_name: str
    status: str
    output: Any
    latency_ms: float
    error_message: Optional[str] = None
