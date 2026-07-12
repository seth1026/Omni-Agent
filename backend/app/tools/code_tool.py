from app.agents.tool_registry import BaseTool
from app.schemas.tool import ToolMetadata, ToolParameter
from app.schemas.common import InputType
from app.utils.config import settings
from groq import Groq

class CodeTool(BaseTool):
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="code_tool",
            description="Explains code, finds bugs, and suggests improvements.",
            supported_inputs=[InputType.TEXT],
            required_parameters=[
                ToolParameter(name="code", type="str", description="The code snippet to analyze.")
            ],
            estimated_latency_sec=3
        )

    async def execute(self, code: str = None, user_query: str = None, **kwargs) -> dict:
        target_code = code or user_query
        if not target_code:
            return {"analysis": "No code provided to analyze."}
            
        prompt = f"""Analyze the following code. Provide your response structured as follows:
1. **Explanation**: Briefly explain what the code does.
2. **Bugs**: List any obvious bugs or state "None found".
3. **Time Complexity**: Big-O notation.
4. **Improvements**: Suggest actionable improvements.

Code:
{target_code[:6000]}
"""
        response = self.client.chat.completions.create(
            model=settings.PLANNER_MODEL, # Code reasoning might need a bigger model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return {"analysis": response.choices[0].message.content}
