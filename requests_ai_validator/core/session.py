"""
AI-enhanced requests session - основная обертка над requests.Session
"""

import requests
from typing import Optional, Dict, Any, Union, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..providers.base import BaseAIProvider
    from ..schemas.base import BaseSchema
import json
import logging

# Allure интеграция
try:
    import allure
    ALLURE_AVAILABLE = True
except ImportError:
    ALLURE_AVAILABLE = False
    # Mock объект для случая когда Allure не установлен
    class MockAllure:
        @staticmethod
        def step(title):
            def decorator(func):
                return func
            return decorator
    
    allure = MockAllure()

from .response import AIResponse

logger = logging.getLogger(__name__)


class AISession(requests.Session):
    """
    Расширенная версия requests.Session с AI валидацией
    
    Использование:
        session = AISession(ai_provider="openai", api_key="your-key")
        response = session.get("https://api.example.com/users")
        validation = response.validate_with_ai(schema=UserSchema, rules=["ID must be positive"])
    """
    
    def __init__(
        self,
        ai_provider: Optional[Any] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ):
        """
        Инициализация AI-enhanced session
        
        Принимает все те же параметры что и requests.Session, плюс AI параметры:
        
        AI Args:
            ai_provider: AI провайдер ("openai", "anthropic", "ollama") или экземпляр провайдера
            api_key: API ключ для провайдера
            model: Модель для использования
            
        Все остальные параметры передаются в requests.Session:
            headers, cookies, auth, proxies, hooks, params, verify, cert, etc.
        """
        # Сохраняем все параметры, которые нужно установить после инициализации
        init_headers = kwargs.pop('headers', None)
        init_cookies = kwargs.pop('cookies', None)
        init_auth = kwargs.pop('auth', None)
        init_proxies = kwargs.pop('proxies', None)
        init_hooks = kwargs.pop('hooks', None)
        init_params = kwargs.pop('params', None)
        init_verify = kwargs.pop('verify', None)
        init_cert = kwargs.pop('cert', None)
        init_timeout = kwargs.pop('timeout', None)
        
        # requests.Session.__init__ принимает только self
        super().__init__()
        
        # Устанавливаем все параметры после инициализации
        if init_headers:
            self.headers.update(init_headers)
        if init_cookies:
            self.cookies.update(init_cookies)
        if init_auth:
            self.auth = init_auth
        if init_proxies:
            self.proxies.update(init_proxies)
        if init_hooks:
            self.hooks.update(init_hooks)
        if init_params:
            self.params.update(init_params)
        if init_verify is not None:
            self.verify = init_verify
        if init_cert:
            self.cert = init_cert
        
        # Сохраняем timeout для использования в запросах
        self._default_timeout = init_timeout
        
        # Настройка AI провайдера
        if ai_provider:
            if isinstance(ai_provider, str):
                from ..providers.factory import create_ai_provider
                self.ai_provider = create_ai_provider(ai_provider, api_key=api_key, model=model)
            else:
                self.ai_provider = ai_provider
        else:
            self.ai_provider = None
        
        # Настройки по умолчанию
        self.default_validation_rules = []
        self.default_ai_rules = []
        self.auto_validate = False
        self.validation_schema = None
        
        # Статистика
        self._validation_stats = {
            "total_requests": 0,
            "validated_requests": 0,
            "successful_validations": 0,
            "failed_validations": 0
        }
    
    def configure_ai(
        self,
        provider,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        """Configure AI provider after session creation"""
        if isinstance(provider, str):
            from ..providers.factory import create_ai_provider
            self.ai_provider = create_ai_provider(provider, api_key=api_key, model=model)
        else:
            self.ai_provider = provider
    
    def set_default_schema(self, schema):
        """Set default schema for all requests"""
        from ..schemas.base import BaseSchema
        from ..schemas.factory import create_schema
        
        if isinstance(schema, BaseSchema):
            self.validation_schema = schema
        else:
            self.validation_schema = create_schema(schema)
    
    def set_default_rules(self, rules: List[str]):
        """Set default validation rules"""
        self.default_validation_rules = rules
    
    def set_default_ai_rules(self, ai_rules: List[str]):
        """Set default AI instructions"""
        self.default_ai_rules = ai_rules
    
    def enable_auto_validation(self, enable: bool = True):
        """Enable automatic validation of all responses"""
        self.auto_validate = enable
    
    # Remove HTTP step to avoid nested structure in Allure
    def request(self, method, url, 
                # AI parameters embedded in request
                ai_validation=False, 
                ai_schema=None, 
                ai_rules=None, 
                ai_expected_success=None,
                **kwargs):
        """
        Переопределенный метод request с встроенной AI валидацией
        
        Стандартные параметры requests.Session.request:
        params, data, headers, cookies, files, auth, timeout, allow_redirects,
        proxies, hooks, stream, verify, cert, json
        
        Новые AI параметры:
        ai_validation: bool - выполнять ли AI валидацию
        ai_schema: Pydantic модель, JSON Schema, OpenAPI spec или путь к файлу
        ai_rules: List[str] - бизнес правила для валидации
        ai_expected_success: bool - ожидаемый результат (True=позитивный, False=негативный)
        """
        # Используем default timeout если не указан
        if 'timeout' not in kwargs and hasattr(self, '_default_timeout') and self._default_timeout:
            kwargs['timeout'] = self._default_timeout
        
        # Выполняем обычный запрос с теми же параметрами
        response = super().request(method, url, **kwargs)
        
        # Создаем AI-enhanced response
        ai_response = AIResponse(response, self.ai_provider)
        
        # Обновляем статистику
        self._validation_stats["total_requests"] += 1
        
        # AI валидация если запрошена
        if ai_validation and self.ai_provider:
            try:
                validation_result = ai_response.validate_with_ai(
                    schema=ai_schema or self.validation_schema,
                    rules=ai_rules or self.default_validation_rules,
                    ai_rules=self.default_ai_rules,
                    expected_success=ai_expected_success if ai_expected_success is not None else True  # По умолчанию ожидаем успех
                )
                # Сохраняем результат в response
                ai_response.ai_validation_result = validation_result
                self._validation_stats["validated_requests"] += 1
                self._validation_stats["successful_validations"] += 1
            except AssertionError:
                # AI валидация упала - это ожидаемое поведение
                self._validation_stats["failed_validations"] += 1
                raise
            except Exception:
                # Техническая ошибка AI валидации
                self._validation_stats["failed_validations"] += 1
        
        # Автоматическая валидация если включена (старое поведение)
        elif self.auto_validate and self.ai_provider:
            try:
                ai_response.validate_with_ai(
                    schema=self.validation_schema,
                    rules=self.default_validation_rules,
                    ai_rules=self.default_ai_rules
                )
                self._validation_stats["validated_requests"] += 1
                self._validation_stats["successful_validations"] += 1
            except Exception as e:
                logger.warning(f"Автоматическая валидация не удалась: {e}")
        
        return ai_response
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics"""
        stats = self._validation_stats.copy()
        if stats["validated_requests"] > 0:
            stats["validation_success_rate"] = (
                stats["successful_validations"] / stats["validated_requests"] * 100
            )
        else:
            stats["validation_success_rate"] = 0
        return stats
    
    def reset_stats(self):
        """Reset statistics"""
        self._validation_stats = {
            "total_requests": 0,
            "validated_requests": 0,
            "successful_validations": 0,
            "failed_validations": 0
        }
    
    # Удобные методы для быстрой валидации
    def get_and_validate(
        self,
        url,
        schema=None,
        rules=None,
        ai_rules=None,
        expected_success=True,
        **kwargs
    ):
        """
        GET запрос с немедленной валидацией
        
        Принимает все параметры requests.get: params, headers, cookies, auth,
        timeout, allow_redirects, proxies, verify, stream, cert
        
        Дополнительные параметры:
            schema: Схема для валидации
            rules: Бизнес-правила валидации
            ai_rules: Кастомные AI инструкции
            expected_success: Ожидаемый результат (True=позитивный, False=негативный тест)
        """
        response = self.get(url, **kwargs)
        if self.ai_provider:
            response.validate_with_ai(
                schema=schema or self.validation_schema,
                rules=rules or self.default_validation_rules,
                ai_rules=ai_rules or self.default_ai_rules,
                expected_success=expected_success
            )
        return response
    
    def assert_valid_response(
        self,
        response,
        schema=None,
        rules=None,
        expected_result=True
    ):
        """
        Валидация ответа с утверждением (аналогично GraphQL версии)
        
        Args:
            response: AIResponse для валидации
            schema: Схема для валидации
            rules: Правила валидации
            expected_result: Ожидаемый результат
            
        Raises:
            AssertionError: Если валидация не соответствует ожиданиям с детальным выводом
        """
        response.assert_valid(
            schema=schema or self.validation_schema,
            rules=rules or self.default_validation_rules,
            expected_result=expected_result
        )
    
    def post_and_validate(
        self,
        url,
        data=None,
        json=None,
        schema=None,
        rules=None,
        **kwargs
    ):
        """
        POST запрос с немедленной валидацией
        
        Принимает все параметры requests.post: data, json, params, headers,
        cookies, files, auth, timeout, allow_redirects, proxies, verify, 
        stream, cert
        
        Дополнительные параметры:
            schema: Схема для валидации
            rules: Правила валидации
        """
        response = self.post(url, data=data, json=json, **kwargs)
        if self.ai_provider:
            response.validate_with_ai(
                schema=schema or self.validation_schema,
                rules=rules or self.default_validation_rules
            )
        return response
    
    def assert_valid_response(
        self,
        response,
        schema=None,
        rules=None,
        expected_result=True
    ):
        """
        Валидация ответа с утверждением (аналогично GraphQL версии)
        
        Args:
            response: AIResponse для валидации
            schema: Схема для валидации
            rules: Правила валидации
            expected_result: Ожидаемый результат
            
        Raises:
            AssertionError: Если валидация не соответствует ожиданиям с детальным выводом
        """
        response.assert_valid(
            schema=schema or self.validation_schema,
            rules=rules or self.default_validation_rules,
            expected_result=expected_result
        )
    
    def put_and_validate(
        self,
        url,
        data=None,
        json=None,
        schema=None,
        rules=None,
        **kwargs
    ):
        """
        PUT запрос с немедленной валидацией
        
        Принимает все параметры requests.put
        """
        response = self.put(url, data=data, json=json, **kwargs)
        if self.ai_provider:
            response.validate_with_ai(
                schema=schema or self.validation_schema,
                rules=rules or self.default_validation_rules
            )
        return response
    
    def assert_valid_response(
        self,
        response,
        schema=None,
        rules=None,
        expected_result=True
    ):
        """
        Валидация ответа с утверждением (аналогично GraphQL версии)
        
        Args:
            response: AIResponse для валидации
            schema: Схема для валидации
            rules: Правила валидации
            expected_result: Ожидаемый результат
            
        Raises:
            AssertionError: Если валидация не соответствует ожиданиям с детальным выводом
        """
        response.assert_valid(
            schema=schema or self.validation_schema,
            rules=rules or self.default_validation_rules,
            expected_result=expected_result
        )
    
    def patch_and_validate(
        self,
        url,
        data=None,
        json=None,
        schema=None,
        rules=None,
        **kwargs
    ):
        """
        PATCH запрос с немедленной валидацией
        
        Принимает все параметры requests.patch
        """
        response = self.patch(url, data=data, json=json, **kwargs)
        if self.ai_provider:
            response.validate_with_ai(
                schema=schema or self.validation_schema,
                rules=rules or self.default_validation_rules
            )
        return response
    
    def assert_valid_response(
        self,
        response,
        schema=None,
        rules=None,
        expected_result=True
    ):
        """
        Валидация ответа с утверждением (аналогично GraphQL версии)
        
        Args:
            response: AIResponse для валидации
            schema: Схема для валидации
            rules: Правила валидации
            expected_result: Ожидаемый результат
            
        Raises:
            AssertionError: Если валидация не соответствует ожиданиям с детальным выводом
        """
        response.assert_valid(
            schema=schema or self.validation_schema,
            rules=rules or self.default_validation_rules,
            expected_result=expected_result
        )
    
    def delete_and_validate(
        self,
        url,
        schema=None,
        rules=None,
        **kwargs
    ):
        """
        DELETE запрос с немедленной валидацией
        
        Принимает все параметры requests.delete: params, headers, cookies,
        auth, timeout, allow_redirects, proxies, verify, stream, cert
        """
        response = self.delete(url, **kwargs)
        if self.ai_provider:
            response.validate_with_ai(
                schema=schema or self.validation_schema,
                rules=rules or self.default_validation_rules
            )
        return response
    
    def assert_valid_response(
        self,
        response,
        schema=None,
        rules=None,
        expected_result=True
    ):
        """
        Валидация ответа с утверждением (аналогично GraphQL версии)
        
        Args:
            response: AIResponse для валидации
            schema: Схема для валидации
            rules: Правила валидации
            expected_result: Ожидаемый результат
            
        Raises:
            AssertionError: Если валидация не соответствует ожиданиям с детальным выводом
        """
        response.assert_valid(
            schema=schema or self.validation_schema,
            rules=rules or self.default_validation_rules,
            expected_result=expected_result
        )
