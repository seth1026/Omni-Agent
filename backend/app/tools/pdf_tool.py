from app.agents.tool_registry import BaseTool
from app.schemas.tool import ToolMetadata, ToolParameter
from app.schemas.common import InputType
import fitz
import os

class PDFTool(BaseTool):
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="pdf_tool",
            description="Extracts structured text from native PDF documents.",
            supported_inputs=[InputType.PDF],
            required_parameters=[
                ToolParameter(name="file_path", type="str", description="Path to the PDF file.")
            ],
            estimated_latency_sec=1
        )

    async def execute(self, file_path: str = None, **kwargs) -> dict:
        target_path = file_path
        if kwargs.get("file_urls"):
            for url in kwargs["file_urls"]:
                if url.lower().endswith(".pdf"):
                    target_path = url
                    break
                    
        if not target_path or not os.path.exists(target_path):
            raise FileNotFoundError(f"PDF not found at {target_path}")
            
        doc = fitz.open(target_path)
        text = ""
        for page in doc:
            text += page.get_text()
            
        is_likely_scanned = len(text.strip()) < 50 and doc.page_count > 0
        
        doc.close()
        
        return {
            "extracted_text": text,
            "is_likely_scanned": is_likely_scanned
        }
