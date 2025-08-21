"""
Ollama провайдер для локальных AI моделей
"""

import requests
import json
from typing import List, Dict, Optional

from .base import BaseAIProvider


class OllamaProvider(BaseAIProvider):
    """Провайдер для Ollama (локальные модели)"""
    
    def __init__(
        self,
        model: str = "llama3.1",
        base_url: str = "http://localhost:11434",
        timeout: int = 60,
        temperature: float = 0.2
    ):
        super().__init__("ollama", model)
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.temperature = temperature
    
    def _make_request(self, messages: List[Dict[str, str]]) -> str:
        """Запрос к Ollama API"""
        # Конвертируем сообщения в единый промпт
        prompt_parts = []
        for msg in messages:
            role = msg["role"].upper()
            content = msg["content"]
            prompt_parts.append(f"{role}:\n{content}")
        
        prompt_parts.append("\nASSISTANT:")
        prompt = "\n\n".join(prompt_parts)
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature
            }
        }
        
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        data = response.json()
        
        return data.get("response", "").strip()
