import time
from typing import Dict, Any, List
from app.schemas.planner import PlanTrace, ExecutionPlan
from app.schemas.common import ProcessingStatus
from app.agents.tool_registry import registry
from app.schemas.tool import ToolExecutionResult

class Executor:
    async def execute_plan(self, plan: ExecutionPlan, initial_context: Dict[str, Any]) -> PlanTrace:
        trace = PlanTrace(plan=plan, overall_status=ProcessingStatus.IN_PROGRESS)
        
        if plan.requires_clarification:
            trace.final_response = plan.clarification_message
            trace.overall_status = ProcessingStatus.COMPLETED
            return trace

        start_total = time.time()
        context_accumulator = dict(initial_context)
        
        for tool_name in (plan.tool_plan or []):
            try:
                tool = registry.get_tool(tool_name)
                # Map context to tool parameters dynamically. 
                # For simplicity, we pass the entire context accumulator.
                # Tools can extract what they need from kwargs.
                result = await tool.run(**context_accumulator)
                trace.executed_tools.append(result)
                
                if result.status == "error":
                    error_msg = f"{tool_name} failed: {result.error_message}"
                    trace.errors.append(error_msg)
                    trace.final_response = f"Execution failed. {error_msg}"
                    trace.overall_status = ProcessingStatus.FAILED
                    trace.total_execution_time_ms = (time.time() - start_total) * 1000
                    return trace
                
                # Shove the tool's output back into the shared context so the next tool can grab it
                if isinstance(result.output, dict):
                    context_accumulator.update(result.output)
                else:
                    context_accumulator[f"{tool_name}_output"] = result.output
                    
            except Exception as e:
                error_msg = f"System error executing {tool_name}: {str(e)}"
                trace.errors.append(error_msg)
                trace.final_response = f"Execution failed. {error_msg}"
                trace.overall_status = ProcessingStatus.FAILED
                trace.total_execution_time_ms = (time.time() - start_total) * 1000
                return trace

        # Figure out what to show the user based on whatever the last tool spit out
        if "final_response" in context_accumulator:
            trace.final_response = context_accumulator["final_response"]
        elif "summary" in context_accumulator:
            trace.final_response = context_accumulator["summary"]
        elif "sentiment" in context_accumulator:
             trace.final_response = f"Sentiment: {context_accumulator['sentiment']} ({context_accumulator.get('justification', '')})"
        elif "analysis" in context_accumulator:
             trace.final_response = context_accumulator["analysis"]
        elif "transcript" in context_accumulator:
            trace.final_response = context_accumulator["transcript"]
        elif "extracted_text" in context_accumulator:
            trace.final_response = context_accumulator["extracted_text"]
        else:
            trace.final_response = "Execution completed successfully."

        trace.overall_status = ProcessingStatus.COMPLETED
        trace.total_execution_time_ms = (time.time() - start_total) * 1000
        return trace
