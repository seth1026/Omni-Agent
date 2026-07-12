import json
from groq import Groq
from app.utils.config import settings
from app.utils.prompts import PLANNER_SYSTEM_PROMPT
from app.schemas.planner import ExecutionPlan
from app.schemas.tool import ToolMetadata
from typing import List, Dict

class Planner:
    def __init__(self, tools_metadata: List[ToolMetadata]):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.tools_metadata = tools_metadata

    def _format_tools_for_prompt(self) -> str:
        formatted = []
        for t in self.tools_metadata:
            inputs = [i.value for i in t.supported_inputs]
            formatted.append(f"- {t.name}: {t.description} (Supports: {inputs})")
        return "\n".join(formatted)

    async def plan(self, user_message: str, available_files: List[Dict]) -> ExecutionPlan:
        tool_descriptions = self._format_tools_for_prompt()
        system_prompt = PLANNER_SYSTEM_PROMPT.format(tool_descriptions=tool_descriptions)
        
        user_content = f"User Request: {user_message}\nFiles provided: {json.dumps(available_files)}"
        
        try:
            response = self.client.chat.completions.create(
                model=settings.PLANNER_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            plan_dict = json.loads(response.choices[0].message.content)
            return ExecutionPlan(**plan_dict)
            
        except Exception as e:
            # If the LLM goes rogue or the API trips up, play it safe and ask the user what to do
            return ExecutionPlan(
                requires_clarification=True,
                clarification_message=f"I encountered an error while planning: {str(e)}",
                tool_plan=[],
                reasoning="Failed to parse LLM output or reach API."
            )
