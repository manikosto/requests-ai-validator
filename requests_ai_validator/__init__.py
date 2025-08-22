"""
Requests AI Validator - AI-powered validation for HTTP requests

Обертка над requests с возможностью AI валидации ответов против схем.
Подобно Selenium Wire, но для requests с AI валидацией.
"""

from .core.session import AISession
from .core.response import AIResponse
from .providers.factory import create_ai_provider
from .schemas.factory import create_schema
from .utils.config import configure

# Функции уровня модуля (как requests.get, requests.post и т.д.)
from .functions import (
    configure_global_ai, get_global_session,
    get, post, put, patch, delete, head, options, request,
    get_and_validate, post_and_validate, put_and_validate, delete_and_validate,
    Session
)

__version__ = "1.0.4"
__author__ = "Aleksei Koledachkin"
__email__ = "akoledachkin@gmail.com"

# Основные экспорты
__all__ = [
    # Классы
    "AISession",
    "AIResponse", 
    "Session",
    
    # Фабрики
    "create_ai_provider",
    "create_schema",
    "configure",
    "configure_global_ai",
    "get_global_session",
    
    # Функции уровня модуля (как requests.get, requests.post)
    "get", "post", "put", "patch", "delete", "head", "options", "request",
    
    # Convenience функции с валидацией
    "get_and_validate", "post_and_validate", "put_and_validate", "delete_and_validate"
]

# Удобные алиасы
ai_session = AISession
ai_requests = AISession
