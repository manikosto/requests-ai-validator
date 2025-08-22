"""
Функции уровня модуля для совместимости с requests.get(), requests.post() и т.д.
"""

from typing import Optional, Dict, Any, List
from .core.session import AISession
from .core.response import AIResponse

# Глобальная AI session для функций уровня модуля
_global_session: Optional[AISession] = None


def configure_global_ai(
    ai_provider: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs
):
    """
    Настройка глобального AI провайдера для функций requests.get(), requests.post() и т.д.
    
    Автоматически загружает настройки из переменных окружения:
    - AI_PROVIDER (default: openai)
    - AI_TOKEN
    - AI_MODEL (default: gpt-3.5-turbo)
    
    Args:
        ai_provider: AI провайдер ("openai", "anthropic", "ollama")
        api_key: API ключ
        model: Модель для использования
        **kwargs: Дополнительные параметры для session
    """
    import os
    from dotenv import load_dotenv
    
    # Загружаем .env файл
    load_dotenv()
    
    # Используем переменные окружения как defaults
    final_provider = ai_provider or os.getenv('AI_PROVIDER', 'openai')
    final_model = model or os.getenv('AI_MODEL', 'gpt-3.5-turbo')
    
    # API ключ из AI_TOKEN
    final_api_key = api_key or os.getenv('AI_TOKEN')
    
    # ПРИНУДИТЕЛЬНО пересоздаем session (сбрасываем кэш)
    global _global_session
    _global_session = None  # Сбрасываем старую session
    _global_session = AISession(
        ai_provider=final_provider,
        api_key=final_api_key,
        model=final_model,
        **kwargs
    )


def get_global_session() -> AISession:
    """Get global AI session with automatic configuration"""
    global _global_session
    
    # Always reload .env to catch file changes
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    # Always recreate session to ensure latest .env values are used
    # This ensures changing .env file immediately takes effect
    configure_global_ai()
    
    return _global_session


def _should_recreate_session() -> bool:
    """Check if session needs recreation due to .env changes"""
    global _global_session
    
    if _global_session is None:
        return True
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    # Проверяем изменились ли ключевые параметры
    current_provider = os.getenv('AI_PROVIDER', 'openai')
    current_model = os.getenv('AI_MODEL', 'gpt-3.5-turbo')
    current_token = os.getenv('AI_TOKEN')
    
    session_provider = getattr(_global_session.ai_provider, 'name', None) if _global_session.ai_provider else None
    session_model = getattr(_global_session.ai_provider, 'model', None) if _global_session.ai_provider else None
    session_token = getattr(_global_session.ai_provider, 'api_key', None) if _global_session.ai_provider else None
    
    # Если что-то изменилось - пересоздаем
    return (
        session_provider != current_provider or
        session_model != current_model or
        session_token != current_token
    )


# Функции уровня модуля с встроенной AI валидацией
def get(
    url: str,
    ai_validation: bool = False,
    ai_schema: Optional[Any] = None,
    ai_rules: Optional[List[str]] = None,
    ai_expected_success: Optional[bool] = None,
    # Standard requests.get parameters
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    cookies: Optional[Dict[str, str]] = None,
    auth: Optional[Any] = None,
    timeout: Optional[float] = None,
    allow_redirects: bool = True,
    proxies: Optional[Dict[str, str]] = None,
    verify: Optional[bool] = None,
    stream: bool = False,
    cert: Optional[str] = None,
    **kwargs
) -> AIResponse:
    """
    GET запрос с встроенной AI валидацией
    
    Args:
        url: URL для запроса
        ai_validation: Выполнять ли AI валидацию
        ai_schema: Pydantic модель, JSON Schema, OpenAPI spec или путь к файлу
        ai_rules: Список бизнес правил для валидации
        ai_expected_success: Ожидаемый результат (True=позитивный, False=негативный)
        **kwargs: Стандартные параметры requests.get()
    """
    return get_global_session().request(
        'GET', url, 
        ai_validation=ai_validation, 
        ai_schema=ai_schema, 
        ai_rules=ai_rules, 
        ai_expected_success=ai_expected_success,
        params=params,
        headers=headers,
        cookies=cookies,
        auth=auth,
        timeout=timeout,
        allow_redirects=allow_redirects,
        proxies=proxies,
        verify=verify,
        stream=stream,
        cert=cert,
        **kwargs
    )


def post(
    url: str,
    data: Optional[Any] = None,
    json: Optional[Any] = None,
    ai_validation: bool = False,
    ai_schema: Optional[Any] = None,
    ai_rules: Optional[List[str]] = None,
    ai_expected_success: Optional[bool] = None,
    # Standard requests.post parameters
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    cookies: Optional[Dict[str, str]] = None,
    files: Optional[Dict[str, Any]] = None,
    auth: Optional[Any] = None,
    timeout: Optional[float] = None,
    allow_redirects: bool = True,
    proxies: Optional[Dict[str, str]] = None,
    verify: Optional[bool] = None,
    stream: bool = False,
    cert: Optional[str] = None,
    **kwargs
) -> AIResponse:
    """
    POST запрос с встроенной AI валидацией
    
    Args:
        url: URL для запроса
        data: Данные для отправки в теле запроса
        json: JSON данные для отправки
        ai_validation: Выполнять ли AI валидацию
        ai_schema: Pydantic модель, JSON Schema, OpenAPI spec или путь к файлу
        ai_rules: Список бизнес правил для валидации
        ai_expected_success: Ожидаемый результат (True=позитивный, False=негативный)
        **kwargs: Стандартные параметры requests.post()
    """
    return get_global_session().request(
        'POST', url,
        data=data,
        json=json,
        ai_validation=ai_validation,
        ai_schema=ai_schema,
        ai_rules=ai_rules,
        ai_expected_success=ai_expected_success,
        params=params,
        headers=headers,
        cookies=cookies,
        files=files,
        auth=auth,
        timeout=timeout,
        allow_redirects=allow_redirects,
        proxies=proxies,
        verify=verify,
        stream=stream,
        cert=cert,
        **kwargs
    )


def put(url, data=None, json=None, ai_validation=False, ai_schema=None, ai_rules=None, ai_expected_success=None, **kwargs) -> AIResponse:
    """
    PUT запрос с встроенной AI валидацией
    
    Args:
        url: URL для запроса
        data: Данные для отправки в теле запроса
        json: JSON данные для отправки
        ai_validation: Выполнять ли AI валидацию
        ai_schema: Pydantic модель, JSON Schema, OpenAPI spec или путь к файлу
        ai_rules: Список бизнес правил для валидации
        ai_expected_success: Ожидаемый результат (True=позитивный, False=негативный)
        **kwargs: Стандартные параметры requests.put()
    """
    return get_global_session().request('PUT', url, data=data, json=json, 
                                       ai_validation=ai_validation, ai_schema=ai_schema, 
                                       ai_rules=ai_rules, ai_expected_success=ai_expected_success, **kwargs)


def patch(url, data=None, json=None, ai_validation=False, ai_schema=None, ai_rules=None, ai_expected_success=None, **kwargs) -> AIResponse:
    """
    PATCH запрос с встроенной AI валидацией
    
    Args:
        url: URL для запроса
        data: Данные для отправки в теле запроса
        json: JSON данные для отправки
        ai_validation: Выполнять ли AI валидацию
        ai_schema: Pydantic модель, JSON Schema, OpenAPI spec или путь к файлу
        ai_rules: Список бизнес правил для валидации
        ai_expected_success: Ожидаемый результат (True=позитивный, False=негативный)
        **kwargs: Стандартные параметры requests.patch()
    """
    return get_global_session().request('PATCH', url, data=data, json=json, 
                                       ai_validation=ai_validation, ai_schema=ai_schema, 
                                       ai_rules=ai_rules, ai_expected_success=ai_expected_success, **kwargs)


def delete(url, ai_validation=False, ai_schema=None, ai_rules=None, ai_expected_success=None, **kwargs) -> AIResponse:
    """
    DELETE запрос с встроенной AI валидацией
    
    Args:
        url: URL для запроса
        ai_validation: Выполнять ли AI валидацию
        ai_schema: Pydantic модель, JSON Schema, OpenAPI spec или путь к файлу
        ai_rules: Список бизнес правил для валидации
        ai_expected_success: Ожидаемый результат (True=позитивный, False=негативный)
        **kwargs: Стандартные параметры requests.delete()
    """
    return get_global_session().request('DELETE', url, ai_validation=ai_validation, 
                                       ai_schema=ai_schema, ai_rules=ai_rules, 
                                       ai_expected_success=ai_expected_success, **kwargs)


def head(url, ai_validation=False, ai_schema=None, ai_rules=None, ai_expected_success=None, **kwargs) -> AIResponse:
    """
    HEAD запрос с встроенной AI валидацией
    
    Args:
        url: URL для запроса
        ai_validation: Выполнять ли AI валидацию
        ai_schema: Pydantic модель, JSON Schema, OpenAPI spec или путь к файлу
        ai_rules: Список бизнес правил для валидации
        ai_expected_success: Ожидаемый результат (True=позитивный, False=негативный)
        **kwargs: Стандартные параметры requests.head()
    """
    return get_global_session().request('HEAD', url, ai_validation=ai_validation, 
                                       ai_schema=ai_schema, ai_rules=ai_rules, 
                                       ai_expected_success=ai_expected_success, **kwargs)


def options(url, ai_validation=False, ai_schema=None, ai_rules=None, ai_expected_success=None, **kwargs) -> AIResponse:
    """
    OPTIONS запрос с встроенной AI валидацией
    
    Args:
        url: URL для запроса
        ai_validation: Выполнять ли AI валидацию
        ai_schema: Pydantic модель, JSON Schema, OpenAPI spec или путь к файлу
        ai_rules: Список бизнес правил для валидации
        ai_expected_success: Ожидаемый результат (True=позитивный, False=негативный)
        **kwargs: Стандартные параметры requests.options()
    """
    return get_global_session().request('OPTIONS', url, ai_validation=ai_validation, 
                                       ai_schema=ai_schema, ai_rules=ai_rules, 
                                       ai_expected_success=ai_expected_success, **kwargs)


def request(method, url, ai_validation=False, ai_schema=None, ai_rules=None, ai_expected_success=None, **kwargs) -> AIResponse:
    """
    Универсальный HTTP запрос с встроенной AI валидацией
    
    Args:
        method: HTTP метод
        url: URL для запроса
        ai_validation: Выполнять ли AI валидацию
        ai_schema: Pydantic модель, JSON Schema, OpenAPI spec или путь к файлу
        ai_rules: Список бизнес правил для валидации
        ai_expected_success: Ожидаемый результат (True=позитивный, False=негативный)
        **kwargs: Стандартные параметры requests.request()
    """
    return get_global_session().request(method, url, ai_validation=ai_validation, 
                                       ai_schema=ai_schema, ai_rules=ai_rules, 
                                       ai_expected_success=ai_expected_success, **kwargs)


# Convenience функции с AI валидацией
def get_and_validate(
    url,
    schema=None,
    rules=None,
    ai_rules=None,
    expected_success=True,
    **kwargs
) -> AIResponse:
    """GET request with immediate AI validation"""
    session = get_global_session()
    response = session.get(url, **kwargs)
    if session.ai_provider:
        response.validate_with_ai(
            schema=schema,
            rules=rules,
            ai_rules=ai_rules,
            expected_success=expected_success
        )
    return response


def post_and_validate(
    url,
    data=None,
    json=None,
    schema=None,
    rules=None,
    ai_rules=None,
    expected_success=True,
    **kwargs
) -> AIResponse:
    """POST request with immediate AI validation"""
    session = get_global_session()
    response = session.post(url, data=data, json=json, **kwargs)
    if session.ai_provider:
        response.validate_with_ai(
            schema=schema,
            rules=rules,
            ai_rules=ai_rules,
            expected_success=expected_success
        )
    return response


def put_and_validate(
    url,
    data=None,
    json=None,
    schema=None,
    rules=None,
    ai_rules=None,
    expected_success=True,
    **kwargs
) -> AIResponse:
    """PUT request with immediate AI validation"""
    session = get_global_session()
    response = session.put(url, data=data, json=json, **kwargs)
    if session.ai_provider:
        response.validate_with_ai(
            schema=schema,
            rules=rules,
            ai_rules=ai_rules,
            expected_success=expected_success
        )
    return response


def delete_and_validate(
    url,
    schema=None,
    rules=None,
    ai_rules=None,
    expected_success=True,
    **kwargs
) -> AIResponse:
    """DELETE request with immediate AI validation"""
    session = get_global_session()
    response = session.delete(url, **kwargs)
    if session.ai_provider:
        response.validate_with_ai(
            schema=schema,
            rules=rules,
            ai_rules=ai_rules,
            expected_success=expected_success
        )
    return response


# Псевдонимы для Session (для тех кто хочет использовать как requests.Session)
Session = AISession
