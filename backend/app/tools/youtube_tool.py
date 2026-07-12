from app.agents.tool_registry import BaseTool
from app.schemas.tool import ToolMetadata, ToolParameter
from app.schemas.common import InputType
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

class YouTubeTool(BaseTool):
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="youtube_tool",
            description="Fetches the transcript of a YouTube video given its URL.",
            supported_inputs=[InputType.YOUTUBE],
            required_parameters=[
                ToolParameter(name="url", type="str", description="URL of the YouTube video.")
            ],
            estimated_latency_sec=2
        )

    def extract_video_id(self, url: str) -> str:
        parsed_url = urlparse(url)
        if parsed_url.hostname == 'youtu.be':
            return parsed_url.path[1:]
        if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
            if parsed_url.path == '/watch':
                p = parse_qs(parsed_url.query)
                return p['v'][0]
        raise ValueError(f"Invalid YouTube URL: {url}")

    async def execute(self, url: str = None, **kwargs) -> dict:
        try:
            # Check if they gave us a URL directly, otherwise let's hunt for one in the text
            target_url = url
            if not target_url:
                user_query = kwargs.get("user_query", "")
                extracted_text = kwargs.get("extracted_text", "")
                
                # Mash everything together and see if a link is hiding in there
                combined_text = user_query + " " + extracted_text
                
                import re
                urls = re.findall(r'(https?://[^\s]+)', combined_text)
                if urls:
                    target_url = urls[0]
                else:
                    return {"transcript": "", "error": "No YouTube URL provided."}
                    
            video_id = self.extract_video_id(target_url)
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            full_transcript = " ".join([t['text'] for t in transcript_list])
            return {"transcript": full_transcript}
        except Exception as e:
            return {"transcript": "", "error": f"Could not fetch transcript: {str(e)}"}
