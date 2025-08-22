"""
OpenAPI/Swagger схемы для валидации
"""

from typing import Dict, Any, Optional, List
import json
from pathlib import Path

from .base import BaseSchema
from .json_schema import JSONSchema


class OpenAPISchema(BaseSchema):
    """Schema based on OpenAPI specification"""
    
    def __init__(
        self, 
        spec: Dict[str, Any], 
        path: str, 
        method: str, 
        response_code: str = "200"
    ):
        """
        Args:
            spec: OpenAPI спецификация
            path: Путь эндпоинта (например, "/users/{id}")
            method: HTTP метод ("get", "post", etc.)
            response_code: Код ответа для валидации (по умолчанию "200")
        """
        self.spec = spec
        self.path = path
        self.method = method.lower()
        self.response_code = response_code
        self._response_schema = self._extract_response_schema()
    
    def _extract_response_schema(self) -> Optional[Dict[str, Any]]:
        """Extract response schema from OpenAPI specification"""
        try:
            paths = self.spec.get("paths", {})
            path_item = paths.get(self.path, {})
            operation = path_item.get(self.method, {})
            responses = operation.get("responses", {})
            response = responses.get(self.response_code, {})
            
            # OpenAPI 3.x
            if "content" in response:
                content = response["content"]
                json_content = content.get("application/json", {})
                return json_content.get("schema", {})
            
            # OpenAPI 2.x (Swagger)
            elif "schema" in response:
                return response["schema"]
            
            return None
        except Exception:
            return None
    
    def validate_structure(self, data: Dict[str, Any]) -> Optional[List[str]]:
        """Структурная валидация через JSON Schema"""
        if not self._response_schema:
            return ["Response schema not found in OpenAPI specification"]
        
        # Используем JSON Schema валидацию
        json_schema = JSONSchema(self._response_schema)
        return json_schema.validate_structure(data)
    
    def get_ai_description(self) -> str:
        """Описание для AI"""
        operation_info = self._get_operation_info()
        schema_info = (
            f"Response Schema:\n{json.dumps(self._response_schema, indent=2)}"
            if self._response_schema else "Response schema not defined"
        )
        
        return f"""OpenAPI Operation:
Endpoint: {self.method.upper()} {self.path}
Response Code: {self.response_code}

{operation_info}

{schema_info}"""
    
    def _get_operation_info(self) -> str:
        """Get operation information"""
        try:
            paths = self.spec.get("paths", {})
            path_item = paths.get(self.path, {})
            operation = path_item.get(self.method, {})
            
            info_parts = []
            
            if "summary" in operation:
                info_parts.append(f"Summary: {operation['summary']}")
            
            if "description" in operation:
                info_parts.append(f"Description: {operation['description']}")
            
            if "tags" in operation:
                info_parts.append(f"Tags: {', '.join(operation['tags'])}")
            
            # Параметры
            if "parameters" in operation:
                params = []
                for param in operation["parameters"]:
                    param_info = f"{param['name']} ({param.get('in', 'unknown')})"
                    if param.get('required'):
                        param_info += " [required]"
                    params.append(param_info)
                info_parts.append(f"Parameters: {', '.join(params)}")
            
            return "\n".join(info_parts) if info_parts else "Operation information not available"
        except Exception:
            return "Error getting operation information"
    
    def get_schema_type(self) -> str:
        return "openapi"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "openapi",
            "path": self.path,
            "method": self.method,
            "response_code": self.response_code,
            "response_schema": self._response_schema
        }
    
    @classmethod
    def from_file(
        cls, 
        file_path: str, 
        path: str, 
        method: str, 
        response_code: str = "200"
    ) -> 'OpenAPISchema':
        """Load OpenAPI schema from file"""
        file_path = Path(file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.suffix.lower() in ['.yaml', '.yml']:
                try:
                    import yaml
                    spec = yaml.safe_load(f)
                except ImportError:
                    raise ImportError("PyYAML not installed for loading YAML files")
            else:
                spec = json.load(f)
        
        return cls(spec, path, method, response_code)
    
    @classmethod
    def from_url(
        cls, 
        url: str, 
        path: str, 
        method: str, 
        response_code: str = "200"
    ) -> 'OpenAPISchema':
        """Загрузка OpenAPI схемы по URL"""
        import requests
        
        response = requests.get(url)
        response.raise_for_status()
        
        if url.endswith(('.yaml', '.yml')):
            try:
                import yaml
                spec = yaml.safe_load(response.text)
            except ImportError:
                raise ImportError("PyYAML не установлен для загрузки YAML")
        else:
            spec = response.json()
        
        return cls(spec, path, method, response_code)
