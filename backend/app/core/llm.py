"""LLM provider configuration."""

from functools import lru_cache
from langchain_core.language_models.chat_models import BaseChatModel

from app.core.config import settings


@lru_cache()
def get_llm() -> BaseChatModel:
    """Get configured LLM instance."""
    provider = settings.llm_provider.lower()

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=0.1,
        )

    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            api_key=settings.anthropic_api_key,
            model=settings.anthropic_model,
            temperature=0.1,
        )

    elif provider == "ollama":
        from langchain_community.chat_models import ChatOllama
        return ChatOllama(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            temperature=0.1,
        )

    elif provider == "llamacpp":
        from langchain_community.chat_models import ChatLlamaCpp
        return ChatLlamaCpp(
            model_path=settings.llamacpp_model_path,
            n_ctx=settings.llamacpp_n_ctx,
            temperature=0.1,
        )

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


def get_embeddings():
    """Get embeddings model."""
    provider = settings.llm_provider.lower()

    if provider == "openai":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(api_key=settings.openai_api_key)

    else:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
