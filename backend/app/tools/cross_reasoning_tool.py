from app.agents.tool_registry import BaseTool
from app.schemas.tool import ToolMetadata, ToolParameter
from app.schemas.common import InputType
from app.utils.config import settings
from groq import Groq

class CrossReasoningTool(BaseTool):
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="cross_reasoning_tool",
            description="Aggregates and compares outputs from multiple extraction tools to answer a query.",
            supported_inputs=[InputType.TEXT],
            required_parameters=[
                ToolParameter(name="user_query", type="str", description="Original user query."),
                ToolParameter(name="extracted_text", type="str", description="Text from PDF/Image", required=False),
                ToolParameter(name="transcript", type="str", description="Audio/Video transcript", required=False)
            ],
            estimated_latency_sec=4
        )

    async def execute(self, user_query: str, extracted_text: str = None, transcript: str = None, **kwargs) -> dict:
        prompt = f"""You are the final reasoning engine for OmniAgent.
User Query: {user_query}

Context 1 (Document/Image Text):
{extracted_text[:4000] if extracted_text else 'None'}

Context 2 (Audio/Video Transcript):
{transcript[:4000] if transcript else 'None'}

Synthesize the contexts and answer the user's query comprehensively. If context is missing, say so.
"""
        response = self.client.chat.completions.create(
            model=settings.PLANNER_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return {"final_response": response.choices[0].message.content}
