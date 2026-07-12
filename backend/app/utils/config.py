from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "OmniAgent API"
    ENVIRONMENT: str = "development"
    
    # API Keys
    GROQ_API_KEY: str = ""
    
    # Model Configurations
    # We use llama3-70b-8192 for complex reasoning (Planner)
    # and llama3-8b-8192 for smaller/faster tasks (Sentiment, etc.)
    PLANNER_MODEL: str = "llama-3.3-70b-versatile" 
    TOOL_MODEL: str = "llama-3.1-8b-instant"     
    
    class Config:
        env_file = ".env"

settings = Settings()
