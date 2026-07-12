from app.agents.tool_registry import BaseTool
from app.schemas.tool import ToolMetadata, ToolParameter
from app.schemas.common import InputType
from app.utils.config import settings
from groq import Groq

class SummaryTool(BaseTool):
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="summary_tool",
            description="Summarizes text into one line, three bullets, and five sentences.",
            supported_inputs=[InputType.TEXT],
            required_parameters=[
                ToolParameter(name="text", type="str", description="The text to summarize.")
            ],
            estimated_latency_sec=2
        )

    async def execute(self, text: str = None, **kwargs) -> dict:
        target_text = text or kwargs.get("extracted_text") or kwargs.get("transcript") or kwargs.get("user_query")
        if not target_text:
            return {"summary": "No text provided to summarize."}
            
        prompt = f"""Summarize the following text. 
Provide exactly three sections:
1. One Line Summary
2. Three Bullet Summary
3. Five Sentence Summary

Text:
{target_text[:8000]} # Trim to avoid context limits
"""
        response = self.client.chat.completions.create(
            model=settings.TOOL_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return {"summary": response.choices[0].message.content}
