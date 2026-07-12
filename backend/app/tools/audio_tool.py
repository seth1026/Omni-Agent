from app.agents.tool_registry import BaseTool
from app.schemas.tool import ToolMetadata, ToolParameter
from app.schemas.common import InputType
import whisper
import os

class AudioTool(BaseTool):
    def __init__(self):
        # We will lazy-load the model in execute() to prevent Render from running out of memory on startup
        self.model = None

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="audio_tool",
            description="Transcribes audio files (mp3, wav, m4a) to text using Whisper.",
            supported_inputs=[InputType.AUDIO],
            required_parameters=[
                ToolParameter(name="file_path", type="str", description="Path to the audio file.")
            ],
            estimated_latency_sec=10
        )

    async def execute(self, file_path: str = None, **kwargs) -> dict:
        target_path = file_path
        if kwargs.get("file_urls"):
            for url in kwargs["file_urls"]:
                if url.lower().endswith(('.mp3', '.wav', '.m4a', '.flac', '.ogg')):
                    target_path = url
                    break
                    
        if not target_path or not os.path.exists(target_path):
            raise FileNotFoundError(f"Audio file not found at {target_path}")
            
        if self.model is None:
            import whisper
            self.model = whisper.load_model("tiny")
            
        result = self.model.transcribe(target_path)
        return {
            "transcript": result["text"]
        }
