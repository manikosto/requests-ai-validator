"""
Минимальная интеграция AI валидации в существующий Helper
МАКСИМАЛЬНО ПРАКТИЧНО - почти без изменений существующего кода
"""

import json
import allure
import requests_ai_validator as requests  # ЕДИНСТВЕННОЕ ИЗМЕНЕНИЕ в импорте
from pydantic import BaseModel
import os

# AI configuration is loaded from .env file automatically
# Set AI_TOKEN=your-api-key in .env file
requests.configure_global_ai("openai")


class Helper:
    """
    ТОЧНО ТОТ ЖЕ Helper + AI валидация
    Все методы остаются как есть, AI добавляется автоматически
    """

    def attach_response(self, response):
        """ТОЧНО ТОТ ЖЕ метод"""
        result = json.dumps(response, indent=4)
        allure.attach(
            body=result,
            name="API response",
            attachment_type=allure.attachment_type.JSON
        )

    def _validate_response(self, response, model: type[BaseModel], status_code: int = 200,
                          success: bool = True, ai_validation: bool = True):
        """
        ТОЧНО ТОТ ЖЕ метод + AI валидация
        
        Args:
            response: Ответ от requests
            model: Pydantic модель
            status_code: Ожидаемый статус код
            success: Ожидаемый результат
            ai_validation: Выполнять ли AI валидацию (по умолчанию True, тест падает при failed)
        """
        self.attach_response(response.json())
        
        # СУЩЕСТВУЮЩИЕ проверки статус кода
        if success:
            assert response.status_code == status_code, response.json()
        else:
            assert response.status_code != 200, response.json()

        # НОВОЕ: AI валидация ПОСЛЕ проверки статус кода, НО ПЕРЕД Pydantic валидацией
        if ai_validation and hasattr(response, 'validate_with_ai'):
            try:
                ai_result = response.validate_with_ai(
                    schema=model,
                    rules=[
                        "Структура данных должна соответствовать модели",
                        "Все обязательные поля должны присутствовать"
                    ],
                    expected_success=True  # По умолчанию ожидаем успех - тест упадет при failed
                )
                # Сохраняем результат
                response.ai_validation_result = ai_result
                # AI фидбек автоматически прикрепляется к Allure
                
            except AssertionError:
                # Пробрасываем AssertionError дальше (AI валидация упала)
                raise
            except Exception as e:
                # Если AI валидация не удалась технически, продолжаем как обычно
                print(f"⚠️ AI валидация не удалась технически: {e}")

        # Pydantic валидация (только если все предыдущие проверки прошли)
        if success:
            if isinstance(response.json(), dict):
                return model(**response.json())
            elif isinstance(response.json(), list):
                return [model(**item) for item in response.json()]
    
    # НОВЫЙ метод для ручной AI валидации (опционально)
    def validate_with_ai(self, response, model=None, rules=None, request_data=None):
        """
        Дополнительный метод для ручной AI валидации
        Можно использовать в тестах при необходимости
        """
        if hasattr(response, 'validate_with_ai'):
            return response.validate_with_ai(
                schema=model,
                rules=rules or ["Ответ должен быть корректным"],
                request_data=request_data
            )
        return None
