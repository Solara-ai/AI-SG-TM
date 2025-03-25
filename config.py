from pydantic_settings import BaseSettings
from pydantic import Field

__all__ = ['Settings', 'settings']


class Settings(BaseSettings):
    API_TITLE: str = Field(default="AI API Service", description="Title of the API service")
    API_VERSION: str = Field(default="1.0.0", description="Version of the API")
    ROOT_PATH: str = Field(..., description="Root path of the API service")
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key")
    MONGO_URI: str = Field(..., description="MongoDB URI")
    DEBUG: bool = Field(default=False, description="Enable debug mode")

    class Config:
        env_file = ".env"


settings = Settings()