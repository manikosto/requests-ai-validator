"""
Базовые классы для схем валидации
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class BaseSchema(ABC):
    """Base class for all validation schemas"""
    
    @abstractmethod
    def validate_structure(self, data: Dict[str, Any]) -> Optional[List[str]]:
        """
        Структурная валидация данных
        
        Returns:
            Optional[List[str]]: Список ошибок или None если валидация прошла
        """
        pass
    
    @abstractmethod
    def get_ai_description(self) -> str:
        """
        Получение описания схемы для AI
        
        Returns:
            str: Описание схемы для передачи AI модели
        """
        pass
    
    @abstractmethod
    def get_schema_type(self) -> str:
        """
        Получение типа схемы
        
        Returns:
            str: Тип схемы (pydantic, json_schema, openapi, etc.)
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертация схемы в словарь (по умолчанию)"""
        return {
            "type": self.get_schema_type(),
            "description": self.get_ai_description()
        }
