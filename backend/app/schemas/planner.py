from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.tool import ToolExecutionResult
from app.schemas.common import ProcessingStatus

class ExecutionPlan(BaseModel):
    requires_clarification: bool = Field(description="True if the user intent is ambiguous.")
    clarification_message: Optional[str] = Field(None, description="Question to ask the user if ambiguous.")
    tool_plan: Optional[List[str]] = Field(default_factory=list, description="Ordered list of tool names to execute.")
    reasoning: str = Field(description="Why this plan was selected.")

class PlanTrace(BaseModel):
    plan: ExecutionPlan
    executed_tools: List[ToolExecutionResult] = Field(default_factory=list)
    overall_status: ProcessingStatus = ProcessingStatus.PENDING
    total_execution_time_ms: float = 0.0
    errors: List[str] = Field(default_factory=list)
    final_response: Optional[str] = None
