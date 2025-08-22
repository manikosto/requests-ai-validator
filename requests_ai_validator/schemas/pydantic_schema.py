"""
Pydantic схемы для валидации
"""

from typing import Dict, Any, Optional, List, Type
import json

try:
    from pydantic import BaseModel, ValidationError
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = object
    ValidationError = Exception

from .base import BaseSchema


class PydanticSchema(BaseSchema):
    """Schema based on Pydantic model"""
    
    def __init__(self, model: Type[BaseModel]):
        if not PYDANTIC_AVAILABLE:
            raise ImportError("Pydantic не установлен. Установите: pip install pydantic")
        
        if not issubclass(model, BaseModel):
            raise ValueError("Модель должна наследоваться от pydantic.BaseModel")
        
        self.model = model
    
    def validate_structure(self, data: Dict[str, Any]) -> Optional[List[str]]:
        """Структурная валидация с помощью Pydantic"""
        try:
            self.model(**data)
            return None
        except ValidationError as e:
            errors = []
            for error in e.errors():
                field_path = " -> ".join(str(x) for x in error["loc"])
                errors.append(f"{field_path}: {error['msg']}")
            return errors
        except Exception as e:
            return [f"Ошибка валидации: {str(e)}"]
    
    def get_ai_description(self) -> str:
        """Описание схемы для AI"""
        try:
            schema_dict = self.model.model_json_schema()
            return f"Pydantic Model Schema:\n{json.dumps(schema_dict, indent=2)}"
        except Exception:
            return f"Pydantic Model: {self.model.__name__}"
    
    def get_schema_type(self) -> str:
        return "pydantic"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        try:
            return self.model.model_json_schema()
        except Exception:
            return {"type": "pydantic", "model": self.model.__name__}
