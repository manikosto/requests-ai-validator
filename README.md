# 🤖 requests-ai-validator

**AI-powered REST API testing framework - drop-in replacement for requests with intelligent validation**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 What is it?

`requests-ai-validator` is a drop-in replacement for the popular `requests` library that adds **AI-powered validation** capabilities to your REST API tests. It uses Large Language Models (LLMs) to intelligently validate API responses, request-response consistency, and business logic.

<img width="879" height="900" alt="Xnip Helper 2025-08-22 4 42 00 PM" src="https://github.com/user-attachments/assets/564866a2-f15b-4dc5-98a6-866e0cca935f" />


## ✨ Key Features

- 🔄 **Drop-in replacement** for `requests` - change only the import statement
- 🤖 **AI-powered validation** - intelligent analysis of API interactions
- 📊 **Multiple AI providers** - OpenAI, Anthropic, Ollama support
- 🎯 **Schema validation** - Pydantic models, JSON Schema, OpenAPI support
- 🌍 **English feedback** - clear and professional AI responses
- 📋 **Business rules** - custom validation rules
- 📊 **Allure integration** - detailed reporting
- ⚙️ **Environment configuration** - easy setup via .env

## 🚀 Quick Start

### Installation

```bash
pip install requests-ai-validator
```

### Basic Usage

```python
# Replace this line:
import requests

# With this line:
import requests_ai_validator as requests

# Use exactly like regular requests + AI validation:
from pydantic import BaseModel

class UserModel(BaseModel):
    id: int
    name: str
    email: str

# Regular request
response = requests.get("https://api.example.com/users/1")

# With AI validation - just add parameters!
response = requests.get(
    "https://api.example.com/users/1",
    ai_validation=True,
    ai_schema=UserModel,
    ai_rules=["User must exist and be valid"]
)
# If AI finds issues → test fails with detailed feedback
```

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# AI Configuration
AI_TOKEN=your-api-key-here
AI_PROVIDER=openai
AI_MODEL=gpt-3.5-turbo
```

### Supported Providers

| Provider | Models | API Key |
|----------|--------|---------|
| **OpenAI** | gpt-3.5-turbo, gpt-4, gpt-4-turbo, gpt-4o | `AI_TOKEN` |
| **Anthropic** | claude-3-haiku, claude-3-sonnet, claude-3-opus | `AI_TOKEN` |
| **Ollama** | llama2, codellama, mistral | No API key (local) |

### Language

All AI feedback is provided in **English** for universal compatibility and clarity.

## 📖 Usage Examples

### 1. Simple GET Request

```python
import requests_ai_validator as requests
from pydantic import BaseModel

class UserModel(BaseModel):
    id: int
    name: str
    email: str

# AI validation built into the request
response = requests.get(
    "https://api.example.com/users/1",
    ai_validation=True,
    ai_schema=UserModel
)
```

### 2. POST Request with Business Rules

```python
response = requests.post(
    "https://api.example.com/users",
    json={"name": "John", "email": "john@example.com"},
    ai_validation=True,
    ai_schema=UserModel,
    ai_rules=[
        "User should be successfully created",
        "ID should be a positive number"
    ]
)
```

### 3. Session Usage

```python
session = requests.Session(ai_provider="openai")

response = session.get(
    url,
    ai_validation=True,
    ai_schema=Model
)
```

### 4. Manual Configuration

```python
# Override environment settings
requests.configure_global_ai(
    ai_provider="anthropic",
    api_key="your-claude-key",
    model="claude-3-sonnet"
)
```

## 🎯 AI Validation Categories

The AI validates 5 key areas:

| Category | Description | Example |
|----------|-------------|---------|
| **http_compliance** | HTTP protocol validation | "Status code 200 correct for GET request" |
| **request_validation** | Request payload validation | "Request contains valid data: name, email" |
| **response_structure** | Response format validation | "Response has valid JSON structure" |
| **schema_compliance** | Schema adherence | "All required fields present in response" |
| **data_consistency** | Request-response consistency | "Common fields match: name, email" |

## ❌ Error Handling

When AI validation fails, you get detailed feedback:

```python
AssertionError: ❌ AI validation failed: Schema validation issues found.
{'schema_compliance': "Missing required field 'missing_field' in response", 'data_consistency': 'Request field name does not match response'}
```

## 🔧 Advanced Usage

### Positive vs Negative Tests

```python
# Positive test - expect AI to find no issues
response = requests.get(url, ai_validation=True, expected_result=True)

# Negative test - expect AI to find issues  
response = requests.get(url, ai_validation=True, expected_result=False)
```

### Custom AI Instructions

```python
response = requests.post(
    url,
    json=data,
    ai_validation=True,
    ai_schema=Model,
    ai_rules=["Business rule 1", "Business rule 2"],
    ai_instructions=["Focus on data consistency", "Ignore performance"]
)
```

### Manual AI Validation

```python
# Get response first
response = requests.get(url)

# Then validate manually
validation_result = response.validate_with_ai(
    schema=Model,
    rules=["Custom rules"],
    expected_success=True
)

# Print detailed feedback (optional)
response.print_validation_details()
```

## 📊 Integration with Existing Code

### Minimal Changes Required

```python
# Before:
import requests
response = requests.get(url)
assert response.status_code == 200
return Model(**response.json())

# After:
import requests_ai_validator as requests  # Only this line changed
response = requests.get(url, ai_validation=True, ai_schema=Model)  # Added AI validation
assert response.status_code == 200
return Model(**response.json())
```

### Framework Integration

Works seamlessly with popular testing frameworks:

- ✅ **pytest** - automatic test failure on AI issues
- ✅ **Allure** - detailed AI feedback in reports
- ✅ **unittest** - standard assertions work
- ✅ **Custom frameworks** - minimal integration effort

## 🔍 How It Works

1. **Make request** - uses standard `requests` library
2. **AI analysis** - sends request/response to LLM for validation
3. **Intelligent feedback** - gets structured analysis of API interaction
4. **Test control** - fails test if AI finds issues (configurable)

## 🎯 Benefits

- 🧠 **Intelligent validation** - catches issues traditional testing misses
- 🚀 **Easy adoption** - minimal code changes required
- 🔍 **Deep analysis** - validates business logic, not just structure
- 📊 **Rich feedback** - detailed explanations of issues found
- ⚡ **Fast integration** - works with existing test suites
- 🌍 **Multi-language** - supports different feedback languages

## 📋 Requirements

- Python 3.8+
- `requests` library
- `pydantic` for schema validation
- AI provider API key (OpenAI, Anthropic) or local Ollama

## 🔗 Links

- **GitHub**: [Source code](https://github.com/manikosto/requests-ai-validator)
- **PyPI**: [Package](https://pypi.org/project/requests-ai-validator/)
- **Issues**: [Report bugs](https://github.com/manikosto/requests-ai-validator/issues)
- **Examples**: See `project/` directory for integration examples

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🎨 Created with

This framework was created with **Вайб кодинг** - AI-powered development approach that combines human creativity with AI assistance to build elegant and powerful solutions.

---

**Transform your API testing with AI intelligence! 🚀**
