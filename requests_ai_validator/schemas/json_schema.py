"""
JSON Schema валидация
"""

from typing import Dict, Any, Optional, List
import json
from pathlib import Path

try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False

from .base import BaseSchema


class JSONSchema(BaseSchema):
    """Схема на основе JSON Schema"""
    
    def __init__(self, schema: Dict[str, Any]):
        if not isinstance(schema, dict):
            raise ValueError("JSON Schema must be a dictionary")
        
        self.schema = schema
    
    def validate_structure(self, data: Dict[str, Any]) -> Optional[List[str]]:
        """Структурная валидация с помощью jsonschema"""
        if not JSONSCHEMA_AVAILABLE:
            return ["jsonschema не установлен. Установите: pip install jsonschema"]
        
        try:
            jsonschema.validate(data, self.schema)
            return None
        except jsonschema.ValidationError as e:
            return [f"JSON Schema ошибка: {str(e)}"]
        except Exception as e:
            return [f"Ошибка валидации: {str(e)}"]
    
    def get_ai_description(self) -> str:
        """Описание схемы для AI"""
        return f"JSON Schema:\n{json.dumps(self.schema, indent=2)}"
    
    def get_schema_type(self) -> str:
        return "json_schema"
    
    def to_dict(self) -> Dict[str, Any]:
        return self.schema
    
    @classmethod
    def from_file(cls, file_path: str) -> 'JSONSchema':
        """Load schema from file"""
        path = Path(file_path)
        
        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix.lower() in ['.yaml', '.yml']:
                try:
                    import yaml
                    schema = yaml.safe_load(f)
                except ImportError:
                    raise ImportError("PyYAML not installed for loading YAML files")
            else:
                schema = json.load(f)
        
        return cls(schema)
    
    @classmethod
    def from_url(cls, url: str) -> 'JSONSchema':
        """Загрузка схемы по URL"""
        import requests
        
        response = requests.get(url)
        response.raise_for_status()
        
        if url.endswith(('.yaml', '.yml')):
            try:
                import yaml
                schema = yaml.safe_load(response.text)
            except ImportError:
                raise ImportError("PyYAML не установлен для загрузки YAML")
        else:
            schema = response.json()
        
        return cls(schema)
