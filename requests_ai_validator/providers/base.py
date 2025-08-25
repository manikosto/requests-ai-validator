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
        
        # AI rules are now integrated directly into the simplified prompt
        
        # Simple and practical system prompt
        system_prompt = """
You are a REST API validator focused on practical validation.

🎯 **VALIDATION FOCUS:**
1. **Request vs Response consistency** - check if sent data matches received data
2. **Response vs Schema compliance** - validate response against provided schema (if any)  
3. **Error status codes** - only flag 4xx and 5xx as problems (2xx and 3xx are fine)
4. **Custom rules** - follow any additional rules provided by user

🚨 **CUSTOM RULES OVERRIDE:**
If custom rules are provided, they take HIGHEST PRIORITY and override standard validation.
Custom rules are MANDATORY - follow them exactly even if they contradict standard validation.

**📋 VALIDATION CHECKS:**

1. **Status Code Check:**
   - 2xx, 3xx: SUCCESS (no issues)
   - 4xx, 5xx: FAILED (report as error)

2. **Request-Response Consistency:**
   - Compare fields that exist in BOTH request and response
   - Example: Request {"name": "John"} + Response {"id": 1, "name": "John"} → check name matches
   - Ignore fields that exist only in request OR only in response

3. **Schema Validation (if schema provided):**
   - Check response against schema requirements
   - Report missing required fields, wrong types, invalid values
   - Skip if no schema provided

4. **Custom Rules (if provided):**
   - Follow custom rules EXACTLY
   - If rule allows something → it's SUCCESS (don't report as failure)
   - Custom rules override ALL standard validation

**🛑 OUTPUT FORMAT:**
```json
{
  "result": "success" | "failed" | "error",
  "message": "<concise summary>",
  "reason": "<specific failure reason, only if failed>"
}
```

**LANGUAGE:** English only."""
        
        # Prepare schema information
        schema_info = ""
        if schema:
            schema_info = f"\n\n**SCHEMA:**\n{schema.get_ai_description()}"
        
        # Prepare rules
        rules_info = ""
        if rules:
            rules_info = f"\n\n**BUSINESS RULES:**\n" + "\n".join(f"- {rule}" for rule in rules)
        
        # AI instructions are now handled directly in user_content for higher priority
        
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
        
        # Build user content 
        user_content = f"""**REQUEST:**
```json
{json.dumps(request_data, indent=2, ensure_ascii=False)}
```

**RESPONSE:**
```json  
{json.dumps(response_data, indent=2, ensure_ascii=False)}
```{request_analysis}{schema_info}{rules_info}""" + (f"""

🚨 **CUSTOM VALIDATION RULES (HIGHEST PRIORITY):**
{chr(10).join(f"- {rule}" for rule in ai_rules)}

**IMPORTANT:** These custom rules override standard validation. If a rule allows something, it's SUCCESS.""" if ai_rules else "") + """

Analyze this API interaction using the validation focus above."""
        
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
