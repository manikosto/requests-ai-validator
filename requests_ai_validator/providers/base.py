"""
Base class for AI providers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging
import json

logger = logging.getLogger(__name__)


class BaseAIProvider(ABC):
    """Base class for AI providers"""
    
    def __init__(self, name: str, model: Optional[str] = None):
        self.name = name
        self.model = model
    
    @abstractmethod
    def _make_request(self, messages: List[Dict[str, str]]) -> str:
        """
        Send request to AI model
        
        Args:
            messages: List of messages for AI
            
        Returns:
            str: Response from AI model
        """
        pass
    
    def validate(
        self,
        request_data: Dict[str, Any],
        response_data: Dict[str, Any],
        schema: Optional[Any] = None,
        rules: Optional[List[str]] = None,
        ai_rules: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        API interaction validation
        
        Args:
            request_data: Request data
            response_data: Response data
            schema: Schema for validation
            rules: Additional rules
            
        Returns:
            Dict[str, Any]: Validation result
        """
        try:
            # Prepare messages for AI
            messages = self._build_validation_messages(
                request_data, response_data, schema, rules, ai_rules
            )
            
            # Request to AI
            ai_response = self._make_request(messages)
            
            # Parse response
            return self._parse_ai_response(ai_response)
            
        except Exception as e:
            logger.error(f"Validation error via {self.name}: {e}")
            return {
                "result": "error",
                "message": f"Provider {self.name} error: {str(e)}",
                "details": {"exception": str(e)},
                "raw": None
            }
    
    def _build_validation_messages(
        self,
        request_data: Dict[str, Any],
        response_data: Dict[str, Any],
        schema: Optional[Any] = None,
        rules: Optional[List[str]] = None,
        ai_rules: Optional[List[str]] = None
    ) -> List[Dict[str, str]]:
        """Build messages for AI validation"""
        
        # Simple English prompt
        system_prompt = """
You are a strict but schema-aware REST API validator with deep expertise in HTTP protocols, data validation, and API design patterns.

Your task is to validate the following aspects of the REST API interaction:

1. ✅ **HTTP Protocol Compliance**:
   - The HTTP method must be appropriate for the operation (GET for retrieval, POST for creation, PUT for updates, DELETE for removal).
   - Status codes must align with the operation outcome (200/201 for success, 400 for client errors, 500 for server errors).
   - Headers must be correctly formatted and semantically appropriate (Content-Type, Authorization, etc.).
   - URL structure should follow RESTful conventions.

2. ✅ **Request Validation**:
   - **CRITICAL**: ONLY validate the actual payload that was sent in the request.
   - **FORBIDDEN**: DO NOT invent, assume, or require fields that were not in the actual request.
   - **ONLY CHECK**: Structure is valid JSON, data types are correct for fields that ARE present.
   - **EXAMPLE**: If request contains {"name": "John", "email": "test@test.com"} - validate ONLY these 2 fields.
   - **NEVER SAY**: "Request should contain field X" unless X was actually in the request.
   - **CORRECT RESPONSE**: "Request contains valid data: name, email" (only list actual fields).

3. ✅ **Response Structure**:
   - Response format must match the expected structure for the endpoint.
   - All required fields must be present in successful responses.
   - Data types in response must be consistent and appropriate.
   - Error responses must provide meaningful information without exposing sensitive details.

4. ✅ **Schema Compliance** (if schema provided):
   - **CRITICAL**: Validate response data against provided schema (Pydantic models, JSON Schema, OpenAPI).
   - **MANDATORY**: For Pydantic models, EVERY field defined in the model MUST be present in the response.
   - **ULTRA STRICT FIELD CHECKING**: 
     * Missing field: Schema requires "nickname", response has no "nickname" key → FAILED
     * Null value: Schema requires "avatar_url": str, response has "avatar_url": null → FAILED  
     * Empty string: Schema requires "name": str, response has "name": "" → FAILED
     * Wrong type: Schema requires "id": int, response has "id": "123" → FAILED
   - **FIELD DETECTION EXAMPLES**:
     * Response: {"id": 1, "name": "John"} + Schema needs "nickname" → "missing required field 'nickname'"
     * Response: {"id": 1, "name": "", "nickname": null} → "empty field 'name', null field 'nickname'"
     * Response: {"id": "123"} + Schema needs id: int → "field 'id' wrong type: expected int got string"
   - **CHECK EVERY FIELD** in the schema against response - be extremely thorough

5. ✅ **Data Consistency**:
   - **ONLY COMPARE**: Fields that exist in BOTH request payload AND response.
   - **EXAMPLE**: Request {"name": "John", "email": "test@test.com"}, Response {"id": 1, "name": "John", "created_at": "2024-01-01"}
   - **CHECK**: name field matches between request and response
   - **IGNORE**: email (not in response), id (not in request), created_at (not in request)
   - **CORRECT RESPONSE**: "Common field 'name' matches between request and response"
   - **WRONG RESPONSE**: "Email field missing in response" (email wasn't required to be in response)

6. ✅ **Business Rule Compliance**:
   - Only validate business rules if explicitly provided in the `<rules>` section.
   - Do not infer or assume business constraints beyond what is explicitly stated.
   - Focus on the specific rules provided by the user.

7. ✅ **Security and Best Practices**:
   - Check for potential sensitive data exposure in responses.
   - Validate proper error handling (informative but not verbose).
   - Ensure consistent API behavior patterns.
   - Check for proper handling of authentication and authorization.

8. ✅ **Performance and Efficiency**:
   - Response times should be reasonable for the operation.
   - Data payload sizes should be appropriate.
   - Caching headers should be present where applicable.

9. ⚠️ **Ignore Non-Critical Metadata**:
   - Ignore server-specific headers that don't affect functionality.
   - Case-insensitive matching for enum values is acceptable unless explicitly forbidden.
   - Minor formatting differences in non-critical fields are acceptable.

10. 🛑 **Output Format**:
    - Return a single, strict JSON object with this exact structure:
    ```json
    {
      "result": "success" | "failed" | "error",
      "message": "<concise summary>",
      "reason": "<specific reason for failure, only if result is failed>"
    }
    ```
    
    **For SUCCESS**: Only include result and message
    **For FAILED**: Include specific reason with concrete issues
    **Examples of good reasons**:
    - "Schema compliance failed: missing required fields 'nickname', 'avatar_url' in response"
    - "Data consistency failed: field 'email' mismatch between request and response"
    - "HTTP compliance failed: status code 422 instead of expected 201 for POST"

**CRITICAL REQUIREMENTS**:
- Never include explanations, Markdown, code blocks, or any text outside the JSON object
- Always respond in valid JSON format and English language
- Be specific about field names and concrete issues
- For successful validations: simple success message
- For failed validations: specific reason with exact problem details

**REASON FORMAT EXAMPLES**:
- "Schema compliance failed: missing required fields 'nickname', 'avatar_url' in response"
- "Data consistency failed: field 'email' value 'test@test.com' in request but 'user@example.com' in response"  
- "HTTP compliance failed: status code 422 instead of expected 201 for POST operation"
- "Request validation failed: invalid data type for field 'age' - expected integer but got string"

**LANGUAGE REQUIREMENT**: RESPOND ONLY IN ENGLISH"""
        
        # Prepare schema information
        schema_info = ""
        if schema:
            schema_info = f"\n\n**SCHEMA:**\n{schema.get_ai_description()}"
        
        # Prepare rules
        rules_info = ""
        if rules:
            rules_info = f"\n\n**BUSINESS RULES:**\n" + "\n".join(f"- {rule}" for rule in rules)
        
        # Prepare AI instructions
        ai_rules_info = ""
        if ai_rules:
            ai_rules_info = f"\n\n**AI INSTRUCTIONS:**\n" + "\n".join(f"- {rule}" for rule in ai_rules)
        
        # Special handling for request-response data comparison
        request_analysis = ""
        if request_data.get("user_provided_data"):
            request_analysis = f"""

**REQUEST DATA FOR COMPARISON:**
```json
{json.dumps(request_data["user_provided_data"], indent=2, ensure_ascii=False)}
```

**ACTUAL REQUEST BODY:**
```json
{json.dumps(request_data.get("actual_body", {}), indent=2, ensure_ascii=False)}
```

**IMPORTANT:** Compare request data with response for consistency:
- For CREATE operations: verify that sent data is preserved in response
- For UPDATE operations: ensure changes are reflected in response  
- For DELETE operations: check deletion confirmation
- Find inconsistencies between what was sent and what was received"""
        
        user_content = f"""**REQUEST:**
```json
{json.dumps(request_data, indent=2, ensure_ascii=False)}
```

**RESPONSE:**
```json  
{json.dumps(response_data, indent=2, ensure_ascii=False)}
```{request_analysis}{schema_info}{rules_info}{ai_rules_info}

Analyze this API interaction."""
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
    
    def _parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI response"""
        import json
        
        try:
            # Clean response from extra text
            response_text = ai_response.strip()
            
            if response_text.startswith("```json"):
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                response_text = response_text[start:end]
            elif not response_text.startswith("{"):
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                if start != -1 and end != 0:
                    response_text = response_text[start:end]
            
            data = json.loads(response_text)
            
            # Normalize result
            result = data.get("result", "").lower()
            if result in {"success", "passed", "valid", "ok"}:
                result = "success"
            elif result in {"failed", "invalid", "fail"}:
                result = "failed"
            else:
                result = "error"
            
            # Prepare details - include reason if present
            details = data.get("details", {})
            reason = data.get("reason")
            
            # If reason exists at top level, add it to details
            if reason:
                details["reason"] = reason
            
            return {
                "result": result,
                "message": data.get("message", ""),
                "details": details,
                "reason": reason,  # Also include at top level
                "raw": ai_response
            }
            
        except Exception as e:
            logger.error(f"AI response parsing error: {e}")
            return {
                "result": "error",
                "message": f"Parsing error: {str(e)}",
                "details": {"parse_error": str(e)},
                "raw": ai_response
            }
