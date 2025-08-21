"""
OpenAI провайдер для AI валидации
"""

import os
import requests
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv
from .base import BaseAIProvider

load_dotenv()

class OpenAIProvider(BaseAIProvider):
    """Провайдер для OpenAI GPT моделей"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        base_url: str = "https://api.openai.com/v1",
        timeout: int = 30,
        temperature: float = 0.2,
        max_tokens: int = 2000
    ):
        super().__init__("openai", model)
        self.api_key = api_key or os.getenv("AI_TOKEN")
        self.base_url = base_url
        
        self.timeout = timeout
            
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API ключ не найден. "
                "Установите переменную AI_TOKEN или передайте api_key параметр"
            )
    
    def _make_request(self, messages: List[Dict[str, str]]) -> str:
        """Запрос к OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Базовый payload
        payload = {
            "model": self.model,
            "messages": messages
        }
        
        # response_format поддерживается только новыми моделями
        if self._supports_json_format():
            payload["response_format"] = {"type": "json_object"}
        
        # Умная логика для разных GPT моделей
        self._configure_model_params(payload)
        
        # Выполняем запрос
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        
        # Логирование для отладки при ошибках
        if response.status_code != 200:
            print(f"🚨 OpenAI API Error {response.status_code}:")
            print(f"📤 Model: {self.model}")
            print(f"📥 Response: {response.text[:500]}...")
        
        response.raise_for_status()
        data = response.json()
        
        return data["choices"][0]["message"]["content"].strip()
    
    def _configure_model_params(self, payload: dict):
        """Простая настройка параметров для всех GPT моделей"""
        # Используем стандартные параметры для всех моделей
        payload["max_tokens"] = self.max_tokens
        payload["temperature"] = self.temperature
    
    def _supports_json_format(self) -> bool:
        """Проверяет поддерживает ли модель response_format: json_object"""
        model = self.model.lower()
        
        # Простая проверка - только новые модели поддерживают JSON format
        return any(x in model for x in ['turbo-1106', 'turbo-0125', 'gpt-4-turbo', 'gpt-4o', 'preview'])
