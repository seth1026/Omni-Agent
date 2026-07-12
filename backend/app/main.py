from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.config import settings
from app.utils.logging import logger
from app.api.routers import chat, upload

# Tool Registration imports
from app.agents.tool_registry import registry
from app.tools import (
    PDFTool, OCRTool, AudioTool, YouTubeTool,
    SummaryTool, SentimentTool, CodeTool, CrossReasoningTool
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Multi-modal Agentic AI System",
    version="1.0.0"
)

# Allow CORS for local frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.PROJECT_NAME} in {settings.ENVIRONMENT} mode.")
    if not settings.GROQ_API_KEY:
        logger.warning("GROQ_API_KEY is not set. LLM features will fail.")
        
    # Register all tools dynamically
    try:
        registry.register(PDFTool())
        registry.register(OCRTool())
        registry.register(AudioTool())
        registry.register(YouTubeTool())
        registry.register(SummaryTool())
        registry.register(SentimentTool())
        registry.register(CodeTool())
        registry.register(CrossReasoningTool())
        logger.info(f"Registered {len(registry.get_all_metadata())} tools successfully.")
    except Exception as e:
        logger.error(f"Failed to register tools: {e}")

@app.get("/health", tags=["System"])
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "environment": settings.ENVIRONMENT}

@app.get("/", tags=["System"])
async def root():
    """Root endpoint to prevent 404 when clicking the Render URL directly."""
    return {
        "message": "OmniAgent API is running! 🚀", 
        "docs": "Append /docs to the URL to view the Swagger API documentation.",
        "status": "Healthy"
    }

# Include API Routers
app.include_router(chat.router, prefix="/api")
app.include_router(upload.router, prefix="/api")

