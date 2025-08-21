"""
Простой пример использования requests-ai-validator
"""

import os
import requests_ai_validator as requests
from pydantic import BaseModel

# Настройка через переменные окружения (или .env файл)
os.environ['AI_PROVIDER'] = 'openai'
os.environ['AI_TOKEN'] = 'your-openai-api-key'


class UserModel(BaseModel):
    id: int
    name: str
    email: str


def example_basic_usage():
    """Базовое использование"""
    print("🎯 БАЗОВОЕ ИСПОЛЬЗОВАНИЕ")
    print("=" * 40)
    
    # Обычный запрос (как всегда)
    response = requests.get("https://jsonplaceholder.typicode.com/users/1")
    print(f"📡 Обычный запрос: {response.status_code}")
    
    # С AI валидацией (добавили параметры)
    response = requests.get(
        "https://jsonplaceholder.typicode.com/users/2",
        ai_validation=True,
        ai_schema=UserModel
    )
    print(f"🤖 С AI валидацией: {response.status_code}")
    print("✅ AI валидация прошла!")


def example_post_request():
    """Пример POST запроса"""
    print("\n🎯 POST ЗАПРОС С AI ВАЛИДАЦИЕЙ")
    print("=" * 40)
    
    user_data = {
        "name": "John Doe",
        "email": "john@example.com"
    }
    
    response = requests.post(
        "https://jsonplaceholder.typicode.com/posts",
        json=user_data,
        ai_validation=True,
        ai_schema=UserModel,
        ai_rules=["Пользователь должен быть успешно создан"]
    )
    print(f"📤 POST с AI валидацией: {response.status_code}")


def example_session_usage():
    """Пример использования с Session"""
    print("\n🎯 ИСПОЛЬЗОВАНИЕ С SESSION")
    print("=" * 40)
    
    # Создаем session с AI
    session = requests.Session(ai_provider="openai")
    
    response = session.get(
        "https://jsonplaceholder.typicode.com/users/3",
        ai_validation=True,
        ai_schema=UserModel
    )
    print(f"🔧 Session с AI: {response.status_code}")


def main():
    print("🚀 REQUESTS-AI-VALIDATOR - ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ")
    print("=" * 60)
    
    try:
        example_basic_usage()
        example_post_request()
        example_session_usage()
        
        print("\n🎉 ВСЕ ПРИМЕРЫ ВЫПОЛНЕНЫ!")
        print("=" * 60)
        print("📋 ЧТО НУЖНО:")
        print("1. Установить: pip install requests-ai-validator")
        print("2. Настроить .env с AI_TOKEN")
        print("3. Заменить import requests")
        print("4. Добавить ai_validation=True где нужно")
        print("5. Готово!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\n💡 Убедитесь что:")
        print("- Установлен AI_TOKEN в переменных окружения")
        print("- Выбран корректный AI_PROVIDER")
        print("- Есть доступ к интернету для AI API")


if __name__ == "__main__":
    main()