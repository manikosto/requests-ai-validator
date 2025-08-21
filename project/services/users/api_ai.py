"""
Минимальная интеграция AI в существующий UsersAPI
МАКСИМАЛЬНО ПРАКТИЧНО - почти без изменений
"""

import allure
import requests_ai_validator as requests  # ЕДИНСТВЕННОЕ ИЗМЕНЕНИЕ в импорте
from project.utils.helper_ai import Helper  # Используем AI версию Helper
from project.config.headers import Headers
from project.services.users.endpoints import Endpoints
from project.services.users.payloads import Payloads
from project.services.users.models.model_user import UserResponseModel


class UsersAPI:
    """
    ТОЧНО ТОТ ЖЕ UsersAPI + AI валидация
    Все методы остаются как есть, AI добавляется автоматически
    """

    def __init__(self):
        """ТОЧНО ТА ЖЕ инициализация"""
        self.headers = Headers()
        self.endpoints = Endpoints()
        self.payloads = Payloads()
        self.helper = Helper()  # Теперь с AI возможностями

    @allure.step("Create user")
    def create_user(self) -> UserResponseModel:
        """
        ТОЧНО ТОТ ЖЕ метод + AI валидация
        Код остается как есть, AI работает автоматически
        """
        response = requests.post(  # Теперь это AI-enhanced requests
            url=self.endpoints.create_user,
            json=self.payloads.create_user(),
            headers=self.headers.basic,
        )
        
        # СУЩЕСТВУЮЩИЙ КОД остается БЕЗ ИЗМЕНЕНИЙ
        return self.helper._validate_response(
            response=response,  # Теперь это AIResponse с методом validate_with_ai
            model=UserResponseModel,
            success=True
        )
        # AI валидация выполняется автоматически в helper._validate_response
    
    # НОВЫЕ методы для расширенной AI валидации (опционально)
    
    @allure.step("Create user with AI validation")
    def create_user_with_ai(self, custom_rules=None, ai_rules=None) -> UserResponseModel:
        """
        Расширенная версия create_user с кастомной AI валидацией
        Можно использовать для специальных тестов
        """
        payload = self.payloads.create_user()
        
        response = requests.post(
            url=self.endpoints.create_user,
            json=payload,
            headers=self.headers.basic,
        )
        
        # AI валидация с сравнением данных запроса и ответа
        if hasattr(response, 'validate_with_ai'):
            ai_validation = response.validate_with_ai(
                schema=UserResponseModel,
                rules=custom_rules or [
                    "Пользователь должен быть создан с уникальным ID",
                    "Отправленные данные должны сохраниться в ответе"
                ],
                ai_rules=ai_rules or [
                    "Сравни данные запроса с ответом",
                    "Проверь что все поля сохранились корректно"
                ],
                request_data=payload  # Сравниваем с отправленными данными
            )
            response.ai_validation_result = ai_validation
        
        # Обычная валидация остается как есть
        return self.helper._validate_response(
            response=response,
            model=UserResponseModel,
            success=True
        )
    
    @allure.step("Get user")
    def get_user(self, user_id: str) -> UserResponseModel:
        """Получение пользователя (новый метод для демонстрации)"""
        response = requests.get(
            url=f"{self.endpoints.base_url}/users/{user_id}",
            headers=self.headers.basic,
        )
        
        return self.helper._validate_response(
            response=response,
            model=UserResponseModel,
            success=True
        )
        # AI валидация выполняется автоматически
    
    @allure.step("Update user")
    def update_user(self, user_id: str, update_data: dict) -> UserResponseModel:
        """Обновление пользователя с AI валидацией"""
        response = requests.put(
            url=f"{self.endpoints.base_url}/users/{user_id}",
            json=update_data,
            headers=self.headers.basic,
        )
        
        # AI автоматически сравнит данные обновления с ответом
        return self.helper._validate_response(
            response=response,
            model=UserResponseModel,
            success=True
        )
