"""
Фабрика для создания AI провайдеров
"""

from typing import Optional, Dict, Any

from .base import BaseAIProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .ollama_provider import OllamaProvider


def create_ai_provider(
    provider_type: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs
) -> BaseAIProvider:
    """
    Фабричная функция для создания AI провайдеров
    
    Args:
        provider_type: Тип провайдера ("openai", "anthropic", "ollama")
        api_key: API ключ
        model: Модель для использования
        **kwargs: Дополнительные параметры для провайдера
        
    Returns:
        BaseAIProvider: Экземпляр провайдера
        
    Examples:
        # OpenAI
        provider = create_ai_provider("openai", api_key="sk-...", model="gpt-4o")
        
        # Anthropic
        provider = create_ai_provider("anthropic", api_key="sk-ant-...", model="claude-3-sonnet-20240229")
        
        # Ollama
        provider = create_ai_provider("ollama", model="llama3.1", base_url="http://localhost:11434")
    """
    provider_type = provider_type.lower()
    
    # Подготовка параметров
    init_kwargs = kwargs.copy()
    if api_key:
        init_kwargs["api_key"] = api_key
    if model:
        init_kwargs["model"] = model
    
    # Создание провайдера
    if provider_type in ["openai", "gpt"]:
        return OpenAIProvider(**init_kwargs)
    
    elif provider_type in ["anthropic", "claude"]:
        return AnthropicProvider(**init_kwargs)
    
    elif provider_type in ["ollama", "llama"]:
        return OllamaProvider(**init_kwargs)
    
    else:
        available_providers = ["openai", "gpt", "anthropic", "claude", "ollama", "llama"]
        raise ValueError(
            f"Неизвестный провайдер: {provider_type}. "
            f"Доступные: {', '.join(available_providers)}"
        )


# Удобные функции для создания конкретных провайдеров
def openai_provider(api_key: Optional[str] = None, model: str = "gpt-4o", **kwargs) -> OpenAIProvider:
    """Create OpenAI provider"""
    return OpenAIProvider(api_key=api_key, model=model, **kwargs)


def anthropic_provider(api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229", **kwargs) -> AnthropicProvider:
    """Create Anthropic provider"""
    return AnthropicProvider(api_key=api_key, model=model, **kwargs)


def ollama_provider(model: str = "llama3.1", base_url: str = "http://localhost:11434", **kwargs) -> OllamaProvider:
    """Create Ollama provider"""
    return OllamaProvider(model=model, base_url=base_url, **kwargs)
