import os
from groq import Groq
from app.utils.config import settings
from app.agents.tool_registry import BaseTool
from app.schemas.tool import ToolMetadata, ToolParameter
from app.schemas.common import InputType

class AudioTool(BaseTool):
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="audio_tool",
            description="Transcribes audio files (mp3, wav, m4a) to text using Whisper.",
            supported_inputs=[InputType.AUDIO],
            required_parameters=[
                ToolParameter(name="file_path", type="str", description="Path to the audio file.")
            ],
            estimated_latency_sec=2
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
            
        # Use Groq's ultra-fast cloud Whisper API to save 150MB+ of local RAM!
        with open(target_path, "rb") as file:
            transcription = self.client.audio.transcriptions.create(
                file=(os.path.basename(target_path), file.read()),
                model="whisper-large-v3-turbo",
            )
            
        return {
            "transcript": transcription.text
        }
