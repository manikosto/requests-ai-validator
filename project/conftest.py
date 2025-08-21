"""
Конфигурация pytest для проекта
"""

import pytest
import os


@pytest.fixture(autouse=True, scope="session")
def configure_ai_for_tests():
    """Автоматическая настройка AI для всех тестов"""
    
    # Принудительно сбрасываем глобальную session
    import requests_ai_validator as requests
    
    # Очищаем старую session если есть
    if hasattr(requests, '_global_session'):
        requests._global_session = None
    
    # Настраиваем заново из .env
    requests.configure_global_ai()
    
    # Проверяем что настроилось правильно
    session = requests.get_global_session()
    if session.ai_provider:
        model = getattr(session.ai_provider, 'model', 'неизвестна')
        print(f"🤖 AI настроен для тестов: {model}")
    
    yield
    
    # Очистка после тестов
    if hasattr(requests, '_global_session'):
        requests._global_session = None


@pytest.fixture(autouse=True)
def reset_ai_session():
    """Сброс AI session перед каждым тестом"""
    import requests_ai_validator as requests
    
    # Принудительно очищаем глобальную session
    if hasattr(requests.functions, '_global_session'):
        requests.functions._global_session = None
    
    # Пересоздаем session с текущими переменными окружения
    requests.configure_global_ai()
    
    yield
