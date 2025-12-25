"""Application configuration."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "Contract Analysis Agent"
    debug: bool = False

    # Database
    database_url: str = "sqlite+aiosqlite:///./contracts.db"

    # LLM Provider
    llm_provider: str = "ollama"

    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"

    # Anthropic
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-sonnet-20240229"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # LlamaCpp
    llamacpp_model_path: Optional[str] = None
    llamacpp_n_ctx: int = 4096

    # Vector Store
    chroma_persist_dir: str = "./chroma_db"

    # Document Storage
    upload_dir: str = "./uploads"
    max_file_size: int = 52428800  # 50MB

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
