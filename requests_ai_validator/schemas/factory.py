"""
Фабрика для создания схем различных типов
"""

from typing import Union, Dict, Any, Type, Optional
from pathlib import Path

from .base import BaseSchema
from .pydantic_schema import PydanticSchema
from .json_schema import JSONSchema
from .openapi_schema import OpenAPISchema

try:
    from pydantic import BaseModel
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = object


def create_schema(
    schema: Union[BaseSchema, Dict[str, Any], Type, str],
    schema_type: Optional[str] = None,
    **kwargs
) -> BaseSchema:
    """
    Фабричная функция для создания схем
    
    Args:
        schema: Схема в различных форматах
        schema_type: Тип схемы (если не может быть определен автоматически)
        **kwargs: Дополнительные параметры для создания схемы
        
    Returns:
        BaseSchema: Экземпляр схемы
        
    Examples:
        # Pydantic модель
        schema = create_schema(UserModel)
        
        # JSON Schema
        schema = create_schema({"type": "object", "properties": {...}})
        
        # OpenAPI из файла
        schema = create_schema("openapi.yaml", schema_type="openapi", path="/users", method="get")
        
        # OpenAPI из URL
        schema = create_schema("https://api.example.com/openapi.json", schema_type="openapi", path="/users", method="get")
    """
    
    # Если уже BaseSchema, возвращаем как есть
    if isinstance(schema, BaseSchema):
        return schema
    
    # Автоопределение типа схемы
    if schema_type is None:
        schema_type = _detect_schema_type(schema)
    
    # Создание схемы по типу
    if schema_type == "pydantic":
        if not PYDANTIC_AVAILABLE:
            raise ImportError("Pydantic not installed")
        return PydanticSchema(schema)
    
    elif schema_type == "json_schema":
        if isinstance(schema, dict):
            return JSONSchema(schema)
        elif isinstance(schema, str):
            return JSONSchema.from_file(schema) if Path(schema).exists() else JSONSchema.from_url(schema)
        else:
            raise ValueError("JSON Schema expects dict or path to file")
    
    elif schema_type == "openapi":
        path = kwargs.get("path")
        method = kwargs.get("method")
        response_code = kwargs.get("response_code", "200")
        
        if not path or not method:
            raise ValueError("Для OpenAPI схемы нужны параметры 'path' и 'method'")
        
        if isinstance(schema, dict):
            return OpenAPISchema(schema, path, method, response_code)
        elif isinstance(schema, str):
            if schema.startswith(("http://", "https://")):
                return OpenAPISchema.from_url(schema, path, method, response_code)
            else:
                return OpenAPISchema.from_file(schema, path, method, response_code)
        else:
            raise ValueError("Для OpenAPI ожидается dict, путь к файлу или URL")
    
    else:
        raise ValueError(f"Неизвестный тип схемы: {schema_type}")


def _detect_schema_type(schema: Union[Dict, Type, str]) -> str:
    """Auto-detect schema type"""
    
    # Pydantic модель
    if PYDANTIC_AVAILABLE and isinstance(schema, type) and issubclass(schema, BaseModel):
        return "pydantic"
    
    # JSON Schema (словарь с $schema или type)
    if isinstance(schema, dict):
        if "$schema" in schema or "type" in schema:
            return "json_schema"
        # OpenAPI спецификация
        elif "openapi" in schema or "swagger" in schema:
            return "openapi"
        else:
            return "json_schema"  # По умолчанию считаем JSON Schema
    
    # Строка - путь к файлу или URL
    if isinstance(schema, str):
        if schema.startswith(("http://", "https://")):
            # URL - нужно определить по содержимому
            return "json_schema"  # По умолчанию
        else:
            # Файл - определяем по расширению
            path = Path(schema)
            if path.suffix.lower() in ['.yaml', '.yml']:
                return "openapi"  # YAML файлы часто OpenAPI
            else:
                return "json_schema"
    
    raise ValueError(f"Не удается определить тип схемы для: {type(schema)}")


# Удобные функции для создания конкретных типов схем
def pydantic_schema(model: Type) -> PydanticSchema:
    """Create Pydantic schema"""
    return PydanticSchema(model)


def json_schema(schema: Union[Dict[str, Any], str]) -> JSONSchema:
    """Создание JSON Schema"""
    if isinstance(schema, dict):
        return JSONSchema(schema)
    else:
        return JSONSchema.from_file(schema)


def openapi_schema(
    spec: Union[Dict[str, Any], str], 
    path: str, 
    method: str, 
    response_code: str = "200"
) -> OpenAPISchema:
    """Create OpenAPI schema"""
    if isinstance(spec, dict):
        return OpenAPISchema(spec, path, method, response_code)
    elif spec.startswith(("http://", "https://")):
        return OpenAPISchema.from_url(spec, path, method, response_code)
    else:
        return OpenAPISchema.from_file(spec, path, method, response_code)
