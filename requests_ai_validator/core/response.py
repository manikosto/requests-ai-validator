"""
AI-enhanced Response объект с методом validate_with_ai
"""

import requests
from typing import Optional, Dict, Any, Union, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..providers.base import BaseAIProvider
    from ..schemas.base import BaseSchema
import json
import logging
from dataclasses import dataclass
from enum import Enum

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
        
        @staticmethod
        def attach(body, name=None, attachment_type=None):
            pass
        
        class attachment_type:
            TEXT = "text"
            JSON = "json"
            HTML = "html"
    
    allure = MockAllure()

logger = logging.getLogger(__name__)


class ValidationResult(str, Enum):
    """AI validation result"""
    SUCCESS = "success"
    FAILED = "failed"
    ERROR = "error"


@dataclass
class ValidationReport:
    """Validation report"""
    result: ValidationResult
    message: str
    details: Optional[Dict[str, Any]] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    rules_used: Optional[List[str]] = None
    schema_used: Optional[str] = None
    raw_ai_response: Optional[str] = None


class AIResponse:
    """
    Обертка над requests.Response с AI валидацией
    
    Все стандартные методы и свойства requests.Response доступны,
    плюс дополнительный метод validate_with_ai()
    """
    
    def __init__(self, response: requests.Response, ai_provider: Optional[Any] = None):
        self._response = response
        self._ai_provider = ai_provider
        self._validation_history = []
    
    @allure.step("AI Response Validation")
    def validate_with_ai(
        self,
        schema: Optional[Any] = None,
        rules: Optional[List[str]] = None,
        ai_rules: Optional[List[str]] = None,
        expected_success: Optional[bool] = None,
        request_data: Optional[Dict[str, Any]] = None,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        fail_on_error: bool = False
    ) -> ValidationReport:
        """
        Основной метод AI валидации
        
        Args:
            schema: Схема для валидации (Pydantic модель, JSON Schema, OpenAPI, путь к файлу)
            rules: Дополнительные бизнес-правила
            ai_rules: Кастомные инструкции для AI (как AI должен проводить валидацию)
            expected_success: Ожидаемый результат (True=позитивный тест, False=негативный тест)
            request_data: Данные запроса для сравнения с ответом (полезно для CRUD операций)
            endpoint: Эндпоинт для контекста (если не указан, берется из URL)
            method: HTTP метод для контекста
            fail_on_error: Падать ли при AI ошибке (False=только возвращает результат)
            
        Returns:
            ValidationReport: Результат валидации
            
        Raises:
            ValueError: Если нет AI провайдера
            AssertionError: Если expected_success задан и результат не соответствует ожиданиям
        """
        if not self._ai_provider:
            raise ValueError("AI provider not configured. Use session.configure_ai()")
        
        # Подготовка данных запроса
        if request_data is None:
            # Автоматически извлекаем данные из requests.Request
            request_data_auto = {
                "method": method or self._response.request.method,
                "url": endpoint or str(self._response.request.url),
                "headers": dict(self._response.request.headers),
            }
            
            # Добавляем тело запроса если есть
            if hasattr(self._response.request, 'body') and self._response.request.body:
                try:
                    if isinstance(self._response.request.body, bytes):
                        body_str = self._response.request.body.decode('utf-8')
                        request_data_auto["body"] = json.loads(body_str)
                    elif isinstance(self._response.request.body, str):
                        request_data_auto["body"] = json.loads(self._response.request.body)
                    else:
                        request_data_auto["body"] = str(self._response.request.body)
                except Exception:
                    # Если не JSON, сохраняем как строку
                    if isinstance(self._response.request.body, bytes):
                        request_data_auto["body"] = self._response.request.body.decode('utf-8', errors='ignore')
                    else:
                        request_data_auto["body"] = str(self._response.request.body)
            
            final_request_data = request_data_auto
        else:
            # Используем переданные пользователем данные запроса
            final_request_data = {
                "method": method or self._response.request.method,
                "url": endpoint or str(self._response.request.url),
                "headers": dict(self._response.request.headers),
                "user_provided_data": request_data  # Данные, переданные пользователем
            }
            
            # Добавляем автоматически извлеченное тело запроса для сравнения
            if hasattr(self._response.request, 'body') and self._response.request.body:
                try:
                    if isinstance(self._response.request.body, bytes):
                        body_str = self._response.request.body.decode('utf-8')
                        final_request_data["actual_body"] = json.loads(body_str)
                    elif isinstance(self._response.request.body, str):
                        final_request_data["actual_body"] = json.loads(self._response.request.body)
                except Exception:
                    pass
        
        # Подготовка данных ответа
        response_data = {
            "status_code": self._response.status_code,
            "headers": dict(self._response.headers),
            "elapsed": self._response.elapsed.total_seconds()
        }
        
        # Добавляем тело ответа
        try:
            response_data["body"] = self._response.json()
        except:
            response_data["body"] = self._response.text
        
        # Подготовка схемы
        schema_info = None
        if schema:
            # Отложенный импорт для избежания циклических зависимостей
            from ..schemas.base import BaseSchema
            from ..schemas.factory import create_schema
            
            if isinstance(schema, BaseSchema):
                schema_info = schema
            else:
                schema_info = create_schema(schema)
        
        # Валидация через AI провайдер
        try:
            validation_result = self._ai_provider.validate(
                request_data=final_request_data,
                response_data=response_data,
                schema=schema_info,
                rules=rules or [],
                ai_rules=ai_rules or []
            )
            
            # Создаем отчет
            result_str = validation_result.get("result", "error")
            # Конвертируем строку в ValidationResult enum
            if result_str == "success":
                result_enum = ValidationResult.SUCCESS
            elif result_str == "failed":
                result_enum = ValidationResult.FAILED
            else:
                result_enum = ValidationResult.ERROR
                
            # Handle new format with reason or old format with details
            details = validation_result.get("details")
            reason = validation_result.get("reason")
            
            # If reason exists at top level, use it
            if reason:
                details = {"reason": reason}
            # If reason exists inside details, extract it
            elif details and isinstance(details, dict) and "reason" in details:
                reason = details["reason"]
                details = {"reason": reason}
            
            report = ValidationReport(
                result=result_enum,
                message=validation_result.get("message", ""),
                details=details,
                provider=self._ai_provider.name,
                model=getattr(self._ai_provider, 'model', None),
                rules_used=rules,
                schema_used=str(schema_info) if schema_info else None,
                raw_ai_response=validation_result.get("raw")
            )
            
            # Save to history
            self._validation_history.append(report)
            
            # Attach to Allure report
            self._attach_to_allure(request_data, response_data, report, rules, ai_rules)
            
            # Check expected_success if specified
            if expected_success is not None:
                if expected_success and report.result != ValidationResult.SUCCESS:
                    # Positive test but validation failed
                    error_details = self._format_validation_error(report)
                    raise AssertionError(f"❌ Positive test failed AI validation: {report.message}\n{error_details}")
                
                if not expected_success and report.result == ValidationResult.SUCCESS:
                    # Negative test but validation passed
                    raise AssertionError(f"❌ Negative test unexpectedly passed AI validation: {report.message}")
            
            # Check fail_on_error if specified
            if fail_on_error and report.result != ValidationResult.SUCCESS:
                error_details = self._format_validation_error(report)
                raise AssertionError(f"❌ AI validation failed: {report.message}\n{error_details}")
            
            return report
            
        except AssertionError:
            # Re-raise AssertionError (expected behavior)
            raise
        except Exception as e:
            logger.error(f"AI validation error: {e}")
            report = ValidationReport(
                result=ValidationResult.ERROR,
                message=f"Validation error: {str(e)}",
                details={"exception": str(e)},
                provider=self._ai_provider.name if self._ai_provider else None
            )
            self._validation_history.append(report)
            return report
    
    def assert_valid(
        self,
        schema: Optional[Any] = None,
        rules: Optional[List[str]] = None,
        expected_result: bool = True,
        **kwargs
    ):
        """
        Валидация с утверждением - падает при неудаче
        
        Args:
            schema: Схема для валидации
            rules: Правила валидации
            expected_result: Ожидаемый результат (True для успеха, False для неудачи)
            **kwargs: Дополнительные параметры
            
        Raises:
            AssertionError: Если валидация не соответствует ожиданиям
        """
        report = self.validate_with_ai(schema=schema, rules=rules, **kwargs)
        
        if expected_result and report.result != ValidationResult.SUCCESS:
            # Формируем детальное сообщение об ошибке как в GraphQL версии
            error_details = self._format_validation_error(report)
            raise AssertionError(f"❌ AI validation failed: {report.message}\n{error_details}")
        
        if not expected_result and report.result == ValidationResult.SUCCESS:
            raise AssertionError("❌ AI unexpectedly reported SUCCESS in negative test-case")
    
    def _format_validation_error(self, report: ValidationReport) -> str:
        """Formats detailed validation error message"""
        lines = []
        
        if report.details:
            lines.append("📊 DETAILED BREAKDOWN:")
            
            categories = [
                ("http_compliance", "HTTP Protocol"),
                ("request_validation", "Request Validation"),
                ("response_structure", "Response Structure"),
                ("schema_compliance", "Schema Compliance"),
                ("data_consistency", "Data Consistency"),
                ("business_rules", "Business Rules"),
                ("security", "Security"),
                ("performance", "Performance")
            ]
            
            # Show ONLY failed categories
            failed_found = False
            for key, name in categories:
                if key in report.details:
                    category_data = report.details[key]
                    
                    # Поддержка как старого формата (строка), так и нового (объект)
                    if isinstance(category_data, str):
                        status = category_data
                        explanation = None
                        checks = None
                    else:
                        status = category_data.get("status", "unknown")
                        explanation = category_data.get("explanation")
                        checks = category_data.get("checks")
                    
                    # Show only failed categories
                    if status == "failed":
                        failed_found = True
                        lines.append(f"   ❌ {name}: {status}")
                        
                        # Add explanation if available
                        if explanation:
                            lines.append(f"      💭 {explanation}")
                        
                        # Add checks if available
                        if checks:
                            lines.append(f"      🔍 Checks:")
                            for check in checks:
                                lines.append(f"         • {check}")
            
            if not failed_found:
                lines.append("   (No specific failed categories)")
            
            # Specific issues
            if report.details.get("issues"):
                lines.append("\n🚨 ISSUES FOUND:")
                for i, issue in enumerate(report.details["issues"], 1):
                    lines.append(f"   {i}. {issue}")
            
            # Рекомендации
            if report.details.get("recommendations"):
                lines.append("\n💡 RECOMMENDATIONS:")
                for i, rec in enumerate(report.details["recommendations"], 1):
                    lines.append(f"   {i}. {rec}")
        
        # Информация о провайдере
        if report.provider and report.model:
            lines.append(f"\n🔧 AI PROVIDER: {report.provider} ({report.model})")
        
        # Правила валидации
        if report.rules_used:
            lines.append("\n📋 VALIDATION RULES:")
            for i, rule in enumerate(report.rules_used, 1):
                lines.append(f"   {i}. {rule}")
        
        # Новый GraphQL-стиль формат
        if self._should_use_graphql_format(report):
            return self._format_graphql_style_error(report)
        
        return "\n".join(lines)
    
    def _should_use_graphql_format(self, report: ValidationReport) -> bool:
        """Checks if GraphQL-style format should be used"""
        if not report.details:
            return False
        
        # Проверяем есть ли новый формат (строки вместо объектов)
        for key in ["http_compliance", "request_validation", "response_structure", "schema_compliance"]:
            if key in report.details and isinstance(report.details[key], str):
                return True
        return False
    
    def _format_graphql_style_error(self, report: ValidationReport) -> str:
        """Format error in simple reason-based style"""
        if not report.details:
            return "No details available"
        
        # Новый простой формат - только reason
        if "reason" in report.details:
            return report.details["reason"]
        
        # Fallback для старого формата - выбираем самую важную проблему
        categories = [
            ("schema_compliance", "Schema compliance"),
            ("data_consistency", "Data consistency"), 
            ("http_compliance", "HTTP compliance"),
            ("request_validation", "Request validation"),
            ("response_structure", "Response structure")
        ]
        
        for key, name in categories:
            if key in report.details:
                category_data = report.details[key]
                if isinstance(category_data, str) and any(word in category_data.lower() for word in [
                    "failed", "missing", "incorrect", "invalid", "mismatch", "error"
                ]):
                    return f"{name} failed: {category_data}"
        
        return "Validation issues found"
    
    def _attach_to_allure(
        self, 
        request_data: Dict[str, Any], 
        response_data: Dict[str, Any], 
        report: ValidationReport,
        rules: Optional[List[str]] = None,
        ai_rules: Optional[List[str]] = None
    ):
        """Attaches only AI Raw and Detailed to Allure report"""
        if not ALLURE_AVAILABLE:
            return
        
        # 1. AI Raw Response - raw AI output
        if report.raw_ai_response:
            allure.attach(
                report.raw_ai_response,
                name="AI Raw Response",
                attachment_type=allure.attachment_type.TEXT
            )
        
        # 2. AI Detailed Feedback - детальный фидбек
        detailed_feedback = self._format_detailed_feedback_for_allure(report)
        allure.attach(
            detailed_feedback,
            name="AI Detailed Feedback",
            attachment_type=allure.attachment_type.TEXT
        )
    
    def _format_detailed_feedback_for_allure(self, report: ValidationReport) -> str:
        """Formats detailed feedback for Allure report"""
        lines = []
        
        lines.append("🤖 DETAILED AI FEEDBACK")
        lines.append("=" * 60)
        
        # Основной результат
        result_emoji = {
            "success": "✅",
            "failed": "❌", 
            "error": "🚨"
        }.get(report.result.value, "❓")
        
        lines.append(f"{result_emoji} RESULT: {report.result.value.upper()}")
        lines.append(f"💬 MESSAGE: {report.message}")
        
        if report.provider:
            lines.append(f"🔧 PROVIDER: {report.provider}")
        if report.model:
            lines.append(f"🧠 MODEL: {report.model}")
        
        # Show reason for failed validations
        if report.details:
            # New simple format with reason
            if "reason" in report.details:
                lines.append("\n🔍 FAILURE REASON:")
                lines.append(f"   {report.details['reason']}")
            else:
                # Fallback for old format
                lines.append("\n📊 DETAILED BREAKDOWN:")
                
                categories = [
                    ("http_compliance", "HTTP Protocol Compliance"),
                    ("request_validation", "Request Validation"),
                    ("response_structure", "Response Structure"),
                    ("schema_compliance", "Schema Compliance"),
                    ("data_consistency", "Data Consistency")
                ]
                
                for key, name in categories:
                    if key in report.details:
                        category_data = report.details[key]
                    
                        if isinstance(category_data, str):
                            status = category_data
                            explanation = None
                            checks = None
                        else:
                            status = category_data.get("status", "unknown")
                            explanation = category_data.get("explanation")
                            checks = category_data.get("checks")
                        
                        emoji = "✅" if status == "passed" else "❌" if status == "failed" else "⏭️"
                        lines.append(f"   {emoji} {name}: {status}")
                        
                        if explanation:
                            lines.append(f"      💭 {explanation}")
                        
                        if checks:
                            lines.append(f"      🔍 Checks:")
                            for check in checks:
                                lines.append(f"         • {check}")
            
            # Проблемы
            if report.details.get("issues"):
                lines.append("\n🚨 ISSUES FOUND:")
                for i, issue in enumerate(report.details["issues"], 1):
                    lines.append(f"   {i}. {issue}")
            
            # Рекомендации
            if report.details.get("recommendations"):
                lines.append("\n💡 RECOMMENDATIONS:")
                for i, rec in enumerate(report.details["recommendations"], 1):
                    lines.append(f"   {i}. {rec}")
        
        # Правила
        if report.rules_used:
            lines.append("\n📋 VALIDATION RULES:")
            for i, rule in enumerate(report.rules_used, 1):
                lines.append(f"   {i}. {rule}")
        
        lines.append("=" * 60)
        return "\n".join(lines)
    
    def get_validation_history(self) -> List[ValidationReport]:
        """Get validation history for this response"""
        return self._validation_history.copy()
    
    def last_validation(self) -> Optional[ValidationReport]:
        """Get last validation"""
        return self._validation_history[-1] if self._validation_history else None
    
    def print_validation_details(self, validation: Optional[ValidationReport] = None):
        """
        Выводит детальный AI фидбек в удобном формате
        
        Args:
            validation: Конкретная валидация (если None, берется последняя)
        """
        if validation is None:
            validation = self.last_validation()
        
        if not validation:
            print("❌ No validation data")
            return
        
        import json
        
        print("\n" + "="*60)
        print("🤖 DETAILED AI FEEDBACK")
        print("="*60)
        
        # Main result
        result_emoji = {
            "success": "✅",
            "failed": "❌", 
            "error": "🚨"
        }.get(validation.result.value, "❓")
        
        print(f"{result_emoji} RESULT: {validation.result.value.upper()}")
        print(f"💬 MESSAGE: {validation.message}")
        
        if validation.provider:
            print(f"🔧 PROVIDER: {validation.provider}")
        if validation.model:
            print(f"🧠 MODEL: {validation.model}")
        
        # Detailed breakdown
        if validation.details:
            print(f"\n📊 DETAILED BREAKDOWN:")
            
            detail_emojis = {
                "passed": "✅",
                "failed": "❌",
                "skipped": "⏭️"
            }
            
            categories = [
                ("http_compliance", "HTTP Protocol Compliance"),
                ("request_validation", "Request Validation"),
                ("response_structure", "Response Structure"),
                ("schema_compliance", "Schema Compliance"),
                ("data_consistency", "Data Consistency"),
                ("business_rules", "Business Rules"),
                ("security", "Security & Best Practices"),
                ("performance", "Performance & Efficiency")
            ]
            
            for key, name in categories:
                if key in validation.details:
                    category_data = validation.details[key]
                    
                    # Поддержка как старого формата (строка), так и нового (объект)
                    if isinstance(category_data, str):
                        status = category_data
                        explanation = None
                        checks = None
                    else:
                        status = category_data.get("status", "unknown")
                        explanation = category_data.get("explanation")
                        checks = category_data.get("checks")
                    
                    emoji = detail_emojis.get(status, "❓")
                    print(f"   {emoji} {name}: {status}")
                    
                    # Выводим объяснение если есть
                    if explanation:
                        print(f"      💭 {explanation}")
                    
                    # Выводим проверки если есть
                    if checks:
                        print(f"      🔍 Проверки:")
                        for check in checks:
                            print(f"         • {check}")
            
            # Проблемы
            if validation.details.get("issues"):
                print(f"\n🚨 ISSUES FOUND:")
                for i, issue in enumerate(validation.details["issues"], 1):
                    print(f"   {i}. {issue}")
            
            # Рекомендации
            if validation.details.get("recommendations"):
                print(f"\n💡 RECOMMENDATIONS:")
                for i, rec in enumerate(validation.details["recommendations"], 1):
                    print(f"   {i}. {rec}")
        
        # Используемые правила
        if validation.rules_used:
            print(f"\n📋 VALIDATION RULES:")
            for i, rule in enumerate(validation.rules_used, 1):
                print(f"   {i}. {rule}")
        
        # Schema
        if validation.schema_used:
            print(f"\n📄 SCHEMA: {validation.schema_used}")
        
        # Raw AI response (if not too long)
        if validation.raw_ai_response and len(validation.raw_ai_response) < 1000:
            print(f"\n🔍 RAW AI RESPONSE:")
            try:
                raw_json = json.loads(validation.raw_ai_response)
                print(json.dumps(raw_json, indent=2, ensure_ascii=False))
            except:
                print(validation.raw_ai_response)
        
        print("="*60)
    
    # Полное проксирование всех методов и свойств requests.Response
    def __getattr__(self, name):
        """Проксирование всех атрибутов requests.Response"""
        return getattr(self._response, name)
    
    def __setattr__(self, name, value):
        """Proxy attribute setting"""
        # AI-специфичные атрибуты сохраняем в AIResponse
        if name.startswith('_') or name in [
            'validate_with_ai', 'assert_valid', 'get_validation_history', 
            'last_validation', 'json_data', 'is_success', 'is_json'
        ]:
            super().__setattr__(name, value)
        else:
            # Остальные атрибуты проксируем в requests.Response
            setattr(self._response, name, value)
    
    def __dir__(self):
        """Show all available methods and properties"""
        ai_methods = [
            'validate_with_ai', 'assert_valid', 'get_validation_history', 
            'last_validation', 'json_data', 'is_success', 'is_json'
        ]
        response_methods = dir(self._response)
        return sorted(set(ai_methods + response_methods))
    
    # Проксирование основных методов requests.Response для совместимости
    def json(self, **kwargs):
        """Проксирование метода json()"""
        return self._response.json(**kwargs)
    
    def iter_content(self, chunk_size=1, decode_unicode=False):
        """Проксирование метода iter_content()"""
        return self._response.iter_content(chunk_size=chunk_size, decode_unicode=decode_unicode)
    
    def iter_lines(self, chunk_size=512, decode_unicode=None, delimiter=None):
        """Проксирование метода iter_lines()"""
        return self._response.iter_lines(
            chunk_size=chunk_size, 
            decode_unicode=decode_unicode, 
            delimiter=delimiter
        )
    
    def raise_for_status(self):
        """Проксирование метода raise_for_status()"""
        return self._response.raise_for_status()
    
    def close(self):
        """Проксирование метода close()"""
        return self._response.close()
    
    # Основные свойства для удобства
    @property
    def json_data(self):
        """Convenient access to JSON data"""
        try:
            return self._response.json()
        except:
            return None
    
    @property
    def is_success(self):
        """Check if request was successful"""
        return 200 <= self._response.status_code < 300
    
    @property
    def is_json(self):
        """Проверка, является ли ответ JSON"""
        return 'application/json' in self._response.headers.get('content-type', '')
    
    def __repr__(self):
        return f"<AIResponse [{self._response.status_code}]>"
    
    def __bool__(self):
        return self._response.ok
