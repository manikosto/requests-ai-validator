# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2024-08-20

### Added
- Initial release of requests-ai-validator
- AISession class as drop-in replacement for requests.Session
- AI-powered validation with validate_with_ai() method
- Support for multiple AI providers:
  - OpenAI GPT models
  - Anthropic Claude models  
  - Ollama local models
- Multiple schema validation formats:
  - Pydantic models
  - JSON Schema
  - OpenAPI/Swagger specifications
- Convenience methods:
  - get_and_validate()
  - post_and_validate()
  - put_and_validate()
  - delete_and_validate()
- Auto-validation capabilities
- Validation statistics and history
- Configuration management
- Comprehensive documentation and examples

### Features
- Full compatibility with requests library
- Type hints and modern Python practices
- Extensible architecture for new providers and schemas
- Detailed validation reports with AI insights
- Error handling and retry mechanisms
