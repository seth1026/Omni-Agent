from app.agents.tool_registry import BaseTool
from app.schemas.tool import ToolMetadata, ToolParameter
from app.schemas.common import InputType
from rapidocr_onnxruntime import RapidOCR
import os

class OCRTool(BaseTool):
    def __init__(self):
        # Lazy load RapidOCR to prevent out-of-memory errors on free deployment tiers
        self.engine = None

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="ocr_tool",
            description="Extracts text from image files (png, jpg, etc) using Optical Character Recognition. DO NOT use for PDFs.",
            supported_inputs=[InputType.IMAGE],
            required_parameters=[
                ToolParameter(name="file_path", type="str", description="Path to the image or PDF file.")
            ],
            estimated_latency_sec=3
        )

    async def execute(self, file_path: str = None, **kwargs) -> dict:
        target_path = file_path
        if kwargs.get("file_urls"):
            for url in kwargs["file_urls"]:
                if url.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                    target_path = url
                    break
                    
        if not target_path or not os.path.exists(target_path):
            raise FileNotFoundError(f"Image or PDF not found at {target_path}")
            
        if self.engine is None:
            from rapidocr_onnxruntime import RapidOCR
            self.engine = RapidOCR()
            
        result, _ = self.engine(target_path)
        
        # Free memory aggressively to survive Render's 512MB limit
        del self.engine
        self.engine = None
        import gc
        gc.collect()
        
        if not result:
            return {"extracted_text": "", "confidence": 0.0}
            
        extracted_text = "\n".join([line[1] for line in result])
        
        # Figure out the average confidence score so we know how accurate the scan was
        confidences = [line[2] for line in result if len(line) > 2]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {
            "extracted_text": extracted_text,
            "confidence": float(avg_confidence)
        }
