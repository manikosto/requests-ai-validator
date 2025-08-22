"""
Anthropic Claude провайдер для AI валидации
"""

import os
import requests
import json
from typing import List, Dict, Optional

from .base import BaseAIProvider


class AnthropicProvider(BaseAIProvider):
    """Provider for Anthropic Claude models"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-sonnet-20240229",
        timeout: int = 30,
        temperature: float = 0.2,
        max_tokens: int = 2000
    ):
        super().__init__("anthropic", model)
        self.api_key = api_key or os.getenv("AI_TOKEN")
        self.timeout = timeout
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        if not self.api_key:
            raise ValueError(
                "Anthropic API ключ не найден. "
                "Set AI_TOKEN environment variable or pass api_key parameter"""
            )
    
    def _make_request(self, messages: List[Dict[str, str]]) -> str:
        """Запрос к Anthropic API"""
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        # Claude ожидает system сообщение отдельно
        system_message = None
        user_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                user_messages.append(msg)
        
        payload = {
            "model": self.model,
            "messages": user_messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        if system_message:
            payload["system"] = system_message
        
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        data = response.json()
        
        return data["content"][0]["text"].strip()
