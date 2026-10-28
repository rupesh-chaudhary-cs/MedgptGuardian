import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "MedGPT Guardian: AI Clinical Decision Support"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS Security: Restrict API access to your React frontend
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # LLM Keys (To be injected via .env in Phase 2)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

settings = Settings()