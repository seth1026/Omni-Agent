from app.agents.tool_registry import BaseTool
from app.schemas.tool import ToolMetadata, ToolParameter
from app.schemas.common import InputType
from app.utils.config import settings
from groq import Groq
import json

class SentimentTool(BaseTool):
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="sentiment_tool",
            description="Analyzes the sentiment of a given text.",
            supported_inputs=[InputType.TEXT],
            required_parameters=[
                ToolParameter(name="text", type="str", description="The text to analyze.")
            ],
            estimated_latency_sec=1
        )

    async def execute(self, text: str = None, **kwargs) -> dict:
        target_text = text or kwargs.get("extracted_text") or kwargs.get("transcript") or kwargs.get("user_query")
        if not target_text:
            return {"sentiment": "Neutral", "confidence": 0.0, "justification": "No text provided to analyze."}
            
        prompt = f"""Analyze the sentiment of the following text.
Respond ONLY with a valid JSON object matching this schema:
{{
    "sentiment": "Positive" | "Negative" | "Neutral",
    "confidence": float (0.0 to 1.0),
    "justification": "Short reason"
}}

Text:
{target_text[:4000]}
"""
        response = self.client.chat.completions.create(
            model=settings.TOOL_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return {"sentiment": "Neutral", "confidence": 0.0, "justification": "Failed to parse JSON"}
