"""
Конфигурация и утилиты
"""

import os
from typing import Optional, Dict, Any

# Глобальная конфигурация
_global_config = {
    "default_ai_provider": "openai",
    "default_model": None,
    "default_api_key": None,
    "auto_validation": False,
    "default_rules": [],
    "timeout": 30,
    "temperature": 0.2,
    "max_tokens": 2000
}


def configure(
    default_ai_provider: Optional[str] = None,
    default_model: Optional[str] = None,
    default_api_key: Optional[str] = None,
    auto_validation: Optional[bool] = None,
    default_rules: Optional[list] = None,
    **kwargs
):
    """
    Глобальная конфигурация библиотеки
    
    Args:
        default_ai_provider: AI провайдер по умолчанию
        default_model: Модель по умолчанию
        default_api_key: API ключ по умолчанию
        auto_validation: Автоматическая валидация
        default_rules: Правила по умолчанию
        **kwargs: Дополнительные параметры
    """
    global _global_config
    
    if default_ai_provider is not None:
        _global_config["default_ai_provider"] = default_ai_provider
    
    if default_model is not None:
        _global_config["default_model"] = default_model
    
    if default_api_key is not None:
        _global_config["default_api_key"] = default_api_key
    
    if auto_validation is not None:
        _global_config["auto_validation"] = auto_validation
    
    if default_rules is not None:
        _global_config["default_rules"] = default_rules
    
    # Дополнительные параметры
    for key, value in kwargs.items():
        _global_config[key] = value


def get_config() -> Dict[str, Any]:
    """Get current configuration"""
    return _global_config.copy()


def reset_config():
    """Reset configuration to default values"""
    global _global_config
    _global_config = {
        "default_ai_provider": "openai",
        "default_model": None,
        "default_api_key": None,
        "auto_validation": False,
        "default_rules": [],
        "timeout": 30,
        "temperature": 0.2,
        "max_tokens": 2000
    }


def load_config_from_env():
    """Load configuration from environment variables"""
    env_mapping = {
        "REQUESTS_AI_PROVIDER": "default_ai_provider",
        "REQUESTS_AI_MODEL": "default_model", 
        "REQUESTS_AI_API_KEY": "default_api_key",
        "REQUESTS_AI_AUTO_VALIDATION": "auto_validation",
        "REQUESTS_AI_TIMEOUT": "timeout",
        "REQUESTS_AI_TEMPERATURE": "temperature",
        "REQUESTS_AI_MAX_TOKENS": "max_tokens"
    }
    
    config_updates = {}
    
    for env_var, config_key in env_mapping.items():
        value = os.getenv(env_var)
        if value is not None:
            # Преобразование типов
            if config_key == "auto_validation":
                config_updates[config_key] = value.lower() in ("true", "1", "yes")
            elif config_key in ["timeout", "max_tokens"]:
                try:
                    config_updates[config_key] = int(value)
                except ValueError:
                    pass
            elif config_key == "temperature":
                try:
                    config_updates[config_key] = float(value)
                except ValueError:
                    pass
            else:
                config_updates[config_key] = value
    
    if config_updates:
        configure(**config_updates)


# Автоматическая загрузка конфигурации из окружения при импорте
load_config_from_env()
